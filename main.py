import sys
from PyQt6.QtWidgets import QApplication
from auth import LoginWindow  # Import the login window

if __name__ == "__main__":  
    app = QApplication(sys.argv)
    login_window = LoginWindow()  # Start with login
    login_window.showMaximized()
    sys.exit(app.exec())  # Run event loop
