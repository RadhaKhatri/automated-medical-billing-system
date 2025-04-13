import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QFormLayout, QWidget, QLabel, QLineEdit, QPushButton, 
    QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QHeaderView
sys.path.append(r"D:\TY\miniproject\medical_shop\venv\Lib\site-packages")
import pdfkit

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from billing import BillingSystem  # Import your BillingSystem class

class BillingUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.entries = {}  # Dictionary to store field entries
        
        self.setWindowTitle("Billing & Sales")
        self.setGeometry(200, 100, 800, 500)

        # Create Central Widget
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        
        # Main Layout
        self.main_layout = QVBoxLayout()

        # Heading Label
        self.heading = QLabel("Generate Bill")
        self.heading.setStyleSheet("font-size: 22px; font-weight: bold;")
        self.main_layout.addWidget(self.heading, alignment=Qt.AlignmentFlag.AlignCenter)

        # Fields for Customer Information
        customer_fields = ["Customer Name", "Medicine ID", "Quantity"]
        form_layout = QVBoxLayout()

        for field in customer_fields:
            label = QLabel(field)
            label.setFont(QFont("Arial", 14))
            label.setFixedWidth(280)
            entry = QLineEdit()
            entry.setFont(QFont("Arial", 14))
            entry.setStyleSheet("border-radius: 8px; padding: 5px; max-width: 200px;")     
            self.entries[field] = entry
            row_layout = QHBoxLayout()
            row_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            row_layout.addWidget(label)
            row_layout.addWidget(entry)
            form_layout.addLayout(row_layout)
        
        self.main_layout.addLayout(form_layout)
        
        # Buttons Layout
        btn_layout = QHBoxLayout()
        button_style = "font-size: 15px; padding: 6px 12px; max-width: 200px;"
        
        self.add_btn = QPushButton("Add Item")
        self.add_btn.setStyleSheet(f"background-color: green; color: white; {button_style}")
        self.add_btn.clicked.connect(self.add_item)
        btn_layout.addWidget(self.add_btn)
        self.main_layout.addLayout(btn_layout)

        # Table for Billing Items
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Medicine", "Quantity", "Price", "GST%", "Subtotal"])

        # Make columns stretch to fill the entire width
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Add table to layout
        self.main_layout.addWidget(self.table)


        # Generate Invoice Button
        self.generate_invoice_button = QPushButton("Generate Invoice")
        self.generate_invoice_button.setStyleSheet(f"background-color: blue; color: white; {button_style}")
        self.generate_invoice_button.clicked.connect(self.generate_invoice)

        # Centering the Button
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.generate_invoice_button, alignment=Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addLayout(button_layout)

        # Set Layout to Central Widget
        self.central_widget.setLayout(self.main_layout)

        # Store items in a list
        self.items = []  
        self.billing_system = BillingSystem()  # Instance of BillingSystem

    def add_item(self):
        """Handles adding a medicine item to the bill."""
        customer_name = self.entries["Customer Name"].text().strip()
        medicine_id = self.entries["Medicine ID"].text().strip()
        quantity_text = self.entries["Quantity"].text().strip()

        if not medicine_id or not quantity_text.isdigit():
            QMessageBox.critical(self, "Error", "Invalid input. Please enter valid data.")
            return

        medicine = self.billing_system.fetch_medicine(medicine_id)
        if medicine:
            name, price, stock, gst = medicine
            quantity = int(quantity_text)

            if quantity > stock:
                QMessageBox.critical(self, "Error", f"Not enough stock for {name}")
                return

            subtotal = (price * quantity) + ((price * quantity) * gst / 100)
            row_count = self.table.rowCount()
            self.table.insertRow(row_count)
            self.table.setItem(row_count, 0, QTableWidgetItem(name))
            self.table.setItem(row_count, 1, QTableWidgetItem(str(quantity)))
            self.table.setItem(row_count, 2, QTableWidgetItem(f"{price:.2f}"))
            self.table.setItem(row_count, 3, QTableWidgetItem(f"{gst}%"))
            self.table.setItem(row_count, 4, QTableWidgetItem(f"{subtotal:.2f}"))

            self.items.append({"medicine_id": int(medicine_id), "quantity": quantity})
        else:
            QMessageBox.critical(self, "Error", "Medicine not found.")

    def generate_invoice(self):
        """Handles invoice generation."""
        customer_name = self.entries["Customer Name"].text().strip()
        if not customer_name or not self.items:
            QMessageBox.critical(self, "Error", "Customer name and items are required!")
            return
        pdfkit_config = pdfkit.configuration(wkhtmltopdf="D:/Mydownlod/wkhtmltopdf/bin/wkhtmltopdf.exe")
        
        invoice_path = self.billing_system.generate_invoice(customer_name, self.items)
        QMessageBox.information(self, "Invoice Generated", f"Invoice saved at {invoice_path}")

# Run UI independently
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BillingUI()
    window.show()
    sys.exit(app.exec())


