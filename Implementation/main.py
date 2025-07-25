import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton
from PyQt5.QtCore import Qt, QTimer, QCoreApplication
from PyQt5.QtGui import QPixmap, QFont, QFontDatabase, QPainter
from components.logger_config import setup_logging
from License_panel.License_panel.controller.license_validation import ValidateLicense
from constants import license_metadata  # ensure constants.license_metadata is writable
import uuid
from Home.views import NameLabel

from datetime import datetime, timedelta, timezone
QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
ENABLE_LICENSE_CHECK = False 
try:
    logger = setup_logging()
except Exception as e:
    print(f"Logging setup failed: {e}")
    sys.exit(1)

def main():
    app = QApplication(sys.argv)

    font_id = QFontDatabase.addApplicationFont("styles/Poppins-Regular.ttf")
    if font_id != -1:
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        app.setFont(QFont(font_family, 12))

    # Prepare splash background
    splash_pix = QPixmap(700, 450)
    splash_pix.fill(Qt.black)

    right_background = QPixmap(350, 450)
    right_background.fill(Qt.white)

    image_pix = QPixmap("assets/Images/SPLASH Image.png").scaled(340, 450, Qt.KeepAspectRatio)
    painter = QPainter(splash_pix)
    painter.drawPixmap(350, 0, right_background)
    painter.drawPixmap(350, 50, image_pix)
    painter.end()

    # Custom splash QWidget instead of QSplashScreen
    splash = QWidget()
    splash.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
    splash.setAttribute(Qt.WA_TranslucentBackground)
    splash.setFixedSize(splash_pix.width(), splash_pix.height())

    # Background label
    bg_label = QLabel(splash)
    bg_label.setPixmap(splash_pix)
    bg_label.setGeometry(0, 0, splash_pix.width(), splash_pix.height())

    # Logo
    logo_label = QLabel(splash)
    logo_pixmap = QPixmap("assets/Images/SPLASH Logo.png").scaled(150, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    logo_label.setPixmap(logo_pixmap)
    logo_label.move(20, 20)

    # Tool title
    tool_name = QLabel("Cyphera", splash)
    tool_name.setStyleSheet("color: #12BCBB; font-family: arial; font-size: 54px; font-weight: bold;")
    tool_name.move(20, 60)

    # Default splash message
    message_info = QLabel(
        "Cyphera is your premier solution for unparalleled product security Threat Analysis.\n"
        "Whether you’re crafting an entire vehicle or a single component, Cyphera has you covered.",
        splash
    )
    message_info.setFixedWidth(300)
    message_info.setWordWrap(True)
    message_info.setStyleSheet("color: white; font-size: 13px;")
    message_info.move(20, 150)

    message_right = QLabel("All rights reserved ©", splash)
    message_right.setStyleSheet("color: white; font-size: 13px;")
    message_right.move(20, 320)

    message_company = QLabel("Ettiksoft Technologies Private Limited", splash)
    message_company.setStyleSheet("color: white; font-size: 13px;")
    message_company.move(20, 340)

    message_loading = QLabel("Loading", splash)
    message_loading.setStyleSheet("color: white; font-size: 13px;")
    message_loading.setFixedWidth(300)
    message_loading.move(20, 390)

    dots = ["", ".", "..", "..."]
    current_dot = 0

    def update_message():
        nonlocal current_dot
        message_loading.setText(f"Loading{dots[current_dot]}")
        current_dot = (current_dot + 1) % len(dots)

    timer = QTimer()
    timer.timeout.connect(update_message)
    timer.start(500)

    splash.show()
    validate_license = ValidateLicense()

    def close_splash_and_show_main():
        if not ENABLE_LICENSE_CHECK:
            logger.warning(" License check is bypassed via config flag. Loading dummy license metadata.")
            
            from constants import license_metadata
            license_metadata.update({
                "user_id": str(uuid.uuid4()),
                "organization_id": str(uuid.uuid4()),
                "authorized_ip": "127.0.0.1",
                "purchase_id": "TEST-PURCHASE-001",
                "product_id": "org tool",
                "invoice_number": "INV-00001",
                "product_plan_id": "TRIAL-PLAN",
                "expiry_date": (datetime.now(timezone.utc) + timedelta(days=365)).isoformat(),
                "issued_on": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                "license_version": "1.0.0",
                "organization_name": "org name",
                "organization_email": "dev@org.com",
                "organization_gst": "N/A",
                "organization_phone": "9999999999",
                "product_name": "org tool",
                "product_plan_name": "Developer Mode",
                "account_manager": "Developer Team"
            })

            from views.TARA_Tool import Application
            main_window = Application()
            splash.close()
            main_window.show()
            return


        validate_license = ValidateLicense()
        status, message = validate_license.check_license()
        print(f"License status: {status}, message: {message}")
        
        if status:
            logger.info("License valid. Opening Home Panel...")
            from views.TARA_Tool import Application
            main_window = Application()
            splash.close()
            main_window.show()
        else:
            logger.critical("License check failed: " + message)
            timer.stop()

            # Hide previous splash texts
            for label in [message_info, message_company, message_right, message_loading]:
                label.hide()

            # Info icon
            info_icon = QLabel(splash)
            info_pix = QPixmap("assets/Icons/info_icon.svg").scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            info_icon.setPixmap(info_pix)
            info_icon.move(20, 140)
            info_icon.show()

            # Headline

            if message == "license_expired":
                err_title = QLabel("Plan validity expired", splash)
            elif "IP address does not match" in message:
                err_title = QLabel("Access denied", splash)
            else:
                err_title = QLabel("License invalid", splash)
                    
      
            err_title.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
            err_title.setWordWrap(True)
            err_title.setFixedWidth(260)
            err_title.move(50, 140)
            err_title.adjustSize()
            err_title.show()

            # Subtext based on error reason
            next_y = err_title.y() + err_title.height() + 10
            if message == "license_expired":
                subtext_msg = "Upgrade your plan. Please contact your administrator."
            elif "IP address does not match" in message:
                subtext_msg = "Cannot access Cyphera outside your organization."
            else:
                subtext_msg = "Cyphera license file is missing or unsupported. Please contact your administrator."

            err_detail = QLabel(subtext_msg, splash)
            err_detail.setStyleSheet("color: white; font-size: 16px;")
            err_detail.setWordWrap(True)
            err_detail.setFixedWidth(340)
            err_detail.move(20, next_y)
            err_detail.adjustSize()
            err_detail.show()

            # Close Button
            btn_y = err_detail.y() + err_detail.height() + 20
            close_button = QPushButton("Close", splash)
            close_button.setStyleSheet("""
                QPushButton {
                    background-color: #0A66C2;
                    color: white;
                    padding: 6px 18px;
                    font-size: 14px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #004A99;
                }
            """)
            close_button.move(20, btn_y)
            close_button.clicked.connect(app.quit)
            close_button.show()

    QTimer.singleShot(5000, close_splash_and_show_main)
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
