from datetime import datetime
import json
import base64
import hashlib
import os
import socket
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.padding import PKCS7
import constants
import requests
from datetime import datetime, timezone
import base64
from dateutil.parser import isoparse
class ValidateLicense:
    """
    A class to handle license validation, decryption, and verification.

    This class provides methods for validating a license file, verifying digital
    signatures, decrypting files, and checking IP addresses. It also supports
    key derivation from passwords and license validation based on expiration dates.
    """

    def __init__(self):
        self.message = "started_validate_license"

    def print_log(self, function_name, content):
        """
        Print logs with the function name and content.

        Parameters
        ----------
        function_name : str
            The name of the function printing the log.
        content : str
            The content of the log to be printed.
        """
        print(f"{function_name} : {content}")

    def hash_json(self, data):
        """
        Generate a SHA-256 hash of the JSON data (sorted keys, compact).

        Parameters
        ----------
        data : dict
            The JSON object to hash.

        Returns
        -------
        tuple
            A tuple containing a boolean (success status) and a hash or error message.
        """
        try:
            json_string = json.dumps(data, separators=(",", ":"), sort_keys=True)
            self.message = "json_hashed"
            return True, hashlib.sha256(json_string.encode()).digest()
        except Exception as e:
            return False, f"Error hashing JSON: {str(e)}"

    def check_license(self):
        """
        Perform license validation by decrypting the file, verifying fields, and checking expiration dates.

        Returns
        -------
        tuple
            A tuple containing a boolean (success status) and a message indicating the result or error.
        """
        self.print_log("check_license", "started function....")
        from constants import ImmutableKeys

        keys = ImmutableKeys()
        password = keys.license_password
        public_key = keys.public_key
        encrypted_file_path = "C:/Tara/Data/SecureKeys/license.license"

        if not os.path.exists(encrypted_file_path):
            self.print_log(
                "check_license", f"License file '{encrypted_file_path}' does not exist."
            )
            # self.message = self.check_new_user_or_old()
            return False, self.message

        is_valid, license_data = self.validate_license(
            password, encrypted_file_path, public_key
        )
        print(is_valid, license_data)
        if is_valid:

            if not license_data:
                self.message = "license_file_corrupted"
                return False, self.message

            required_fields = [
                        "user_id",
                        "organization_id",
                        "authorized_ip",
                        "purchase_id",
                        "product_id",
                        "invoice_number",
                        "product_plan_id",
                        "expiry_date",
                        "issued_on",
                        "license_version",
                        # 🔽 Additional enriched fields
                        "organization_name",
                        "organization_email",
                        "organization_gst",
                        "organization_phone",
                        "product_name",
                        "product_plan_name",
                        "account_manager"
                    ]



            if "data" not in license_data or "digital_signature" not in license_data:
                self.message = "license_file_corrupted_missing_fields"
                return False, self.message
            else:
                for field in required_fields:
                    if field not in license_data["data"]:
                        self.message = "license_file_corrupted_missing_fields"
                        return False, self.message

            license_info = license_data["data"]
            # required_fields = ["issued_date", "expiry_date"]
            # for field in required_fields:
            #     if field not in license_info:
            #         self.message = "license_file_corrupted_missing_fields"
            #         return False, self.message

            issued_date = isoparse(license_info["issued_on"]).astimezone(timezone.utc)
            expiry_date = isoparse(license_info["expiry_date"]).astimezone(timezone.utc)
            now = datetime.now(timezone.utc)

            if now < issued_date:
                self.message = "license_not_yet_started"
                return False, self.message

            if now > expiry_date:
                self.message = "license_expired"
                return False, self.message

            return True, "license_valid"
        else:
            return False, license_data

    def decrypt_file(self, password, file_path):
        try:
            with open(file_path, "r") as f:
                lines = f.readlines()
                encrypted_b64 = "".join([line for line in lines if not line.startswith("#")]).strip()

            data = base64.b64decode(encrypted_b64)

            salt = data[:16]
            iv = data[16:32]
            ciphertext = data[32:]

            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend(),
            )
            key = kdf.derive(password.encode())

            # ✅ CBC decryption
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

            # ✅ Remove padding
            unpadder = PKCS7(128).unpadder()
            plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()

            license_data = json.loads(plaintext.decode())

            # ✅ Pretty print decrypted content
            print("🔓 Decrypted License Content:")
            print(json.dumps(license_data, indent=2))

            self.message = "license_decoded"
            return True, license_data

        except Exception as e:
            print(f"❌ Decryption failed: {e}")
            self.message = "license_corrupted"
            return False, self.message

    def check_ip_address(self, ip_address):
        """
        Check if the current system's IP address matches a given IP address.

        Parameters
        ----------
        ip_address : str
            The IP address to compare against.

        Returns
        -------
        tuple
            A tuple containing a boolean (success status) and a message indicating the result.
        """
        status, current_ip = self.get_current_ip()
        if current_ip is None:
            return False, "Failed to retrieve the current IP address."
        print("ip_status: ",current_ip, ip_address)
        return current_ip == ip_address, (
            "IP address matches"
            if current_ip == ip_address
            else "IP address does not match"
        )

    def get_current_ip(self):
        """
        Retrieve the current system's Wi-Fi IP address.

        Returns
        -------
        tuple
            A tuple containing a boolean (success status) and the IP address or an error message.
        """
        try:
            response = requests.get("https://api.ipify.org?format=json")
            if response.status_code == 200:
                return True, response.json().get("ip")
            else:
                print("Failed to get public IPv4 address.")
                return None
        except Exception as e:
            print("Error getting IP address:", e)
            return False, f"Error getting IP address: {e}"
        
        # try:
        #     with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        #         s.connect(("8.8.8.8", 80))
        #         return True, s.getsockname()[0]
        # except Exception as e:
        #     return False, f"Error getting current IP address: {str(e)}"
    
    def validate_license(self, password, file_path, public_key):
     

        with open("C:/Tara/Data/SecureKeys/license.license", "r") as f:
            lines = f.readlines()
            base64_data = "".join([line for line in lines if not line.startswith("#")]).strip()
            print("Decoded bytes length:", len(base64.b64decode(base64_data)))

        """
        Validate the license by decrypting the file, verifying IP, and checking the digital signature.

        Parameters
        ----------
        password : str
            The password used to decrypt the license file.
        file_path : str
            The path to the encrypted license file.
        public_key : str
            The PEM-encoded public key used for signature verification.

        Returns
        -------
        tuple
            A tuple containing a boolean (success status) and the license data or an error message.
        """
        print("validate_license started.....")
        status, license_data = self.decrypt_file(password, file_path)

        if not status:
            print("❌ Decryption failed:", license_data)
            return False, license_data

        # 🔄 Convert license format if needed (metadata → data)
        if "metadata" in license_data and "signature" in license_data:
            license_data = {
                "data": license_data["metadata"],
                "digital_signature": license_data["signature"]
            }

        # ✅ Check IP match
        ip_address = license_data["data"].get("authorized_ip")

        ip_status, ip_message = self.check_ip_address(ip_address)
        if not ip_status:
            return False, ip_message

        # ✅ Decode signature
        try:
            digital_sign = base64.b64decode(license_data["digital_signature"])
        except Exception as e:
            return False, f"Error decoding digital signature: {e}"

        # ✅ Hash data for signature validation
        data = license_data["data"]
        print(data, '---- license content ----')
        constants.license_metadata = data
        hash_status, json_hash = self.hash_json(data)
        if not hash_status:
            return False, json_hash

        # ✅ Verify digital signature
        signature_status, signature_message = self.verify_signature(
            public_key, digital_sign, json_hash
        )

        if signature_status:
            return True, license_data
        else:
            return False, signature_message

    def verify_signature(self, public_key_str, signature, data_hash):
        """
        Verify a digital signature using the public key.

        Parameters
        ----------
        public_key_str : str
            The PEM-encoded public key as a string.
        signature : bytes
            The digital signature to verify.
        data_hash : bytes
            The hash of the data being verified.

        Returns
        -------
        tuple
            A tuple containing a boolean (success status) and a message indicating the result.
        """
        try:
            public_key = serialization.load_pem_public_key(
                public_key_str.encode(), backend=default_backend()
            )
            public_key.verify(signature, data_hash, padding.PKCS1v15(), hashes.SHA256())
            return True, "Signature is valid."
        except Exception as e:
            return False, f"Signature verification failed: {str(e)}"

    def generate_key_from_password(self, password: str, salt: bytes):
        """
        Generate a secure AES key from a password and salt.

        Parameters
        ----------
        password : str
            The password to derive the key from.
        salt : bytes
            The salt value used for key derivation.

        Returns
        -------
        tuple
            A tuple containing a boolean (success status) and the derived AES key or an error message.
        """
        try:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend(),
            )
            return True, kdf.derive(password.encode())
        except Exception as e:
            return False, f"Error generating key from password: {str(e)}"

    def decrypt_and_load_file(self, file_path, password):
        """
        Decrypt and load the contents of a file as JSON.

        Parameters
        ----------
        file_path : str
            The path to the file to decrypt.
        password : str
            The password used to decrypt the file.

        Returns
        -------
        tuple
            A tuple containing a boolean (success status) and the decrypted JSON data or an error message.
        """
        try:
            if not os.path.exists(file_path):
                return False, f"File not found: {file_path}"

            with open(file_path, "rb") as f:
                content = f.read()

            salt, iv, encrypted_data = content[:16], content[16:32], content[32:]

            key_status, key = self.generate_key_from_password(password, salt)
            if not key_status:
                return False, key

            cipher = Cipher(
                algorithms.AES(key), modes.CBC(iv), backend=default_backend()
            )
            decryptor = cipher.decryptor()

            padded_data = decryptor.update(encrypted_data) + decryptor.finalize()

            unpadder = PKCS7(128).unpadder()
            data = unpadder.update(padded_data) + unpadder.finalize()

            return True, json.loads(data.decode("utf-8"))
        except Exception as e:
            return False, f"Error decrypting and loading file: {str(e)}"
