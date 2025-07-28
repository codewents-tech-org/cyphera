
personal_data = {}
billing_details = {}
product_id = "f54d17a5-58f9-4d55-853a-e5c3d3700674"
license_metadata = {}
class ImmutableKeys:
    def __init__(self):
        self._license_password = "tara@123#321@arat"
        self._public_key = """-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEApzuoLvBXmZS+AjajzWT5\n5DeTZRSz60+DY7jAlfdq6ZMPN9zpR/xiGRsBYPoNZ+jXPMrEOi/L0PjLuEcAdSk1\nq4+22d8ncWg09/DexUHifOiwX19eO2i3WJOHmNEMxAMCtMI+TXyWzeGhIpw4ORGv\nWe6EDZ2EwbAo9rRGz9xXStvhNJkW6e61rSFue3LJ5oAvOuX8ZeAbtybbHZfkzoE3\nOZBAZ+ZvmOJfr+x+f2gHcv5ogsukXLhI4szUaWKXz4ecO0dtPBkGRr6Z74UMmo7Z\nkg+s0uNBLKucNJos00IW72lPAbtl+t7VinABk8G/MP6k6c8NVcKGB0ZwxK8pOZwf\nNwIDAQAB\n-----END PUBLIC KEY-----"""
        self._private_key = """-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCnO6gu8FeZlL4C\nNqPNZPnkN5NlFLPrT4NjuMCV92rpkw833OlH/GIZGwFg+g1n6Nc8ysQ6L8vQ+Mu4\nRwB1KTWrj7bZ3ydxaDT38N7FQeJ86LBfX147aLdYk4eY0QzEAwK0wj5NfJbN4aEi\nnDg5Ea9Z7oQNnYTBsCj2tEbP3FdK2+E0mRbp7rWtIW57csnmgC865fxl4Bu3Jtsd\nl+TOgTc5kEBn5m+Y4l+v7H5/aAdy/miCy6RcuEjizNRpYpfPh5w7R208GQZGvpnv\nhQyajtmSD6zS40Esq5w0mizTQhbvaU8Bu2X63tWKcAGTwb8w/qTpzw1VwoYHRnDE\nryk5nB83AgMBAAECggEASGnCp6CWrgAETr0OLLAerL2L62cNiUUC5bloWwepmb5+\nBnh34x3b9HcHH9Dm4SmnmcFLOs7beH9i50aHYjQX81Pln23LjIXM+deo/s1Knz+6\nr3GCQkNTsN0hCADtgCq1j0PU6oSaYEflGDGA/uUzgsOPFr4wcBYxhrIFP5hvjA/6\nn7IfwlBV4qc76nOJ1671gDXFTeWxwrk1hgZ+FUpKMKJm20DuJqb218Csh2MCu2Wx\nxKN1obfkCBQ1h8IZ/wdvmEkhN70faCn6zWSAlfRmABaZtWjAUPs+Azvj8OrNQ5Gl\nqVMb9yJdBGUV3a3xmQ1XLCzCfGfuMawMV+/AmFcucQKBgQDXDNVArEpyxQkNtjas\nWyGdllIR/zvVnslb6kandL6EBsCOBKBaA3vN1SziB2liatEfjACgH+erxs9KWBxU\nzlgA+g1ezRtdU28kpkPlcDumPhHfEArgA41o3AtFfWPLLzF2919ech/qQ4gm8Tz5\nJRCzlRbsYJqYa0QdyhY2DVqzbQKBgQDHE9uV042QAoRRrAjtXGFkDtEHXJCu4VPz\nSmAD42szRXYog0hPEdPIjUMHFEeo/15UwrZbGZCaOQ3aWvY/Pd3n77lP5pI1ajtQ\nfF/J61342V8f+qU7hvDsgheUkZ4Cliv2CSlo2e62GZU3+l4ZCA9az0e4X/Yy1zih\nf5pxTf8SswKBgQCZSrCIlUfMX9+AQq7eVWe06X4/De0c7T8jofATVgioHBgOJAYZ\no/oQUzDXPelFGldPYYDgo12E+QayO/SWDzB0Icp+FT64W80SFuK3HjWm3v/mPY1C\n+cVHRfNS6XrFTzK3VsZIkJlnaBQZjkSkZGNvX4sjnAkXNP8tLOyAQyywUQKBgAxu\n3A7uaG/vCE6FfQU9+MMj/cAE8vBJGFIgegCkKmTIWMnM8S4nAeALmn0NsjAGyuBm\nTLdB0HshRxE1Dx4CAiLjIOKxlr4JRW0QZ3cX4QWSpdM8dydRlShgM5LOyVyF/nbe\nOZzXx4XN8TjOxSOxEixst6D3NUwVju7fJkkfQufrAoGBAMMwCq4PG5a3MBKr0o6+\nqENnrdlDswy78460PZy00kCvFgdGENNK/0dugnIPQnhbk60ONl/eD8/BebmdajtX\n5w9sQlHft8AdFngFSSPWORDJmBfpYRbJVVi98lkmTxyXGOh4+KjwRXx99NdO4Xkw\ncDuR7RDaoEy0m8l/ZROU5KpW\n-----END PRIVATE KEY-----"""
        self.product_id = "f54d17a5-58f9-4d55-853a-e5c3d3700674"

    @property
    def license_password(self):
        return self._license_password

    @property
    def public_key(self):
        return self._public_key

    @property
    def private_key(self):
        return self._private_key

    def __setattr__(self, name, value):
        if name in ("_license_password", "_public_key", "_private_key") and hasattr(self, name):
            raise AttributeError(f"Cannot modify immutable attribute: {name}")
        super().__setattr__(name, value)
