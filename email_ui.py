from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QLabel, QPushButton, QMessageBox
)
import sys
import pymysql
from email_fetch import fetch_vendor_bills

class VendorEmailUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vendor Email Manager")
        self.setGeometry(200, 200, 400, 300)

        layout = QVBoxLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Vendor Name")
        layout.addWidget(QLabel("Name:"))
        layout.addWidget(self.name_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Vendor Email")
        layout.addWidget(QLabel("Email:"))
        layout.addWidget(self.email_input)

        self.gst_input = QLineEdit()
        self.gst_input.setPlaceholderText("GST Number")
        layout.addWidget(QLabel("GST No:"))
        layout.addWidget(self.gst_input)

        self.contact_input = QLineEdit()
        self.contact_input.setPlaceholderText("Contact Number")
        layout.addWidget(QLabel("Contact:"))
        layout.addWidget(self.contact_input)

        self.add_button = QPushButton("Add Vendor Email")
        self.add_button.clicked.connect(self.add_vendor)
        layout.addWidget(self.add_button)

        self.fetch_button = QPushButton("Fetch Bills from All Vendors")
        self.fetch_button.clicked.connect(self.fetch_vendor_bills)
        layout.addWidget(self.fetch_button)

        self.setLayout(layout)

    def add_vendor(self):
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        gst = self.gst_input.text().strip()
        contact = self.contact_input.text().strip()

        if not name or not email:
            QMessageBox.warning(self, "Input Error", "Name and Email are required.")
            return

        try:
            conn = pymysql.connect(host="localhost", user="root", password="Radha@1474", database="medical_shop")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO vendors (name, email, gst_no, contact)
                VALUES (%s, %s, %s, %s)
            """, (name, email, gst, contact))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Success", f"Vendor {name} added.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def fetch_vendor_bills(self):
        try:
            owner_email = "beactive1474@gmail.com"
            owner_app_password = "zrtr smiw bfvd droc"
            fetch_vendor_bills(owner_email, owner_app_password)
            QMessageBox.information(self, "Success", "Bills fetched for all vendors.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = VendorEmailUI()
    win.show()
    sys.exit(app.exec())
