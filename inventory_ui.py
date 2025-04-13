import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from inventory_manager import InventoryManager  # ✅ Importing from the parent folder

from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QTableWidget, QTableWidgetItem, QMessageBox
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHeaderView

class InventoryUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Medical Shop Inventory Management")
        self.setGeometry(100, 100, 900, 500)

        self.inventory = InventoryManager()
        
        self.initUI()

    def initUI(self):
        # Main Layout
        main_layout = QVBoxLayout()
        
        # Heading Label
        self.heading = QLabel("Inventory Management")
        self.heading.setStyleSheet("font-size: 22px; font-weight: bold;")
        main_layout.addWidget(self.heading, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Form Layout
        self.entries = {}
        fields = ["Name", "Category", "Manufacturer", "Batch No", "Expiry Date (YYYY-MM-DD)", "Price", "Stock Quantity", "GST %"]
        form_layout = QVBoxLayout()
        
        for field in fields:
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
        
        main_layout.addLayout(form_layout)
        
        # Buttons Layout
        btn_layout = QHBoxLayout()
        button_style = "font-size: 15px; padding: 6px 12px; max-width: 200px;"
        
        self.add_btn = QPushButton("Add Medicine")
        self.add_btn.setStyleSheet(f"background-color: green; color: white; {button_style}")
        self.add_btn.clicked.connect(self.add_medicine)

        self.update_btn = QPushButton("Update Medicine")
        self.update_btn.setStyleSheet(f"background-color: blue; color: white; {button_style}")
        self.update_btn.clicked.connect(self.update_medicine)

        self.delete_btn = QPushButton("Delete Medicine")
        self.delete_btn.setStyleSheet(f"background-color: red; color: white; {button_style}")
        self.delete_btn.clicked.connect(self.delete_medicine)

        self.clear_btn = QPushButton("Clear Fields")
        self.clear_btn.setStyleSheet(f"background-color: gray; color: white; {button_style}")
        self.clear_btn.clicked.connect(self.clear_fields)

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.update_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.clear_btn)
        
        main_layout.addLayout(btn_layout)
        
        # Table Layout
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Category", "Manufacturer", "Batch", "Expiry", "Price", "Stock", "GST"])
        self.table.cellClicked.connect(self.select_medicine)
        self.table.setStyleSheet("width: 100%;")
        
        # Make columns expand to take full width
        self.table.horizontalHeader().setStretchLastSection(True)  # Stretch last column
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)  # Stretch all columns

        # Remove unnecessary width restriction
        self.table.setStyleSheet("border: none;") 
        
        main_layout.addWidget(self.table)
        self.load_medicines()
        
        # Main Widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
    
    def add_medicine(self):
        data = self.get_form_data()
        if data:
            self.inventory.add_medicine(*data)
            self.load_medicines()
            self.clear_fields()
    
    def update_medicine(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Error", "Please select a medicine to update")
            return
        
        medicine_id = int(self.table.item(selected_row, 0).text())
        data = self.get_form_data()
        if data:
            self.inventory.update_medicine(medicine_id, *data)
            self.load_medicines()
            self.clear_fields()
    
    def delete_medicine(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Error", "Please select a medicine to delete")
            return
        
        medicine_id = int(self.table.item(selected_row, 0).text())
        self.inventory.delete_medicine(medicine_id)
        self.load_medicines()
        self.clear_fields()
    
    def load_medicines(self):
        self.table.setRowCount(0)
        medicines = self.inventory.fetch_all_medicines()
        for row_num, medicine in enumerate(medicines):
            self.table.insertRow(row_num)
            for col_num, value in enumerate(medicine):
                self.table.setItem(row_num, col_num, QTableWidgetItem(str(value)))
    
    def select_medicine(self, row, _):
        for i, field in enumerate(list(self.entries.keys())):
            self.entries[field].setText(self.table.item(row, i+1).text())
    
    def get_form_data(self):
        try:
            name = self.entries["Name"].text().strip()
            category = self.entries["Category"].text().strip()
            manufacturer = self.entries["Manufacturer"].text().strip()
            batch_no = self.entries["Batch No"].text().strip()
            expiry_date = self.entries["Expiry Date (YYYY-MM-DD)"].text().strip()
            price = float(self.entries["Price"].text().strip())
            stock_quantity = int(self.entries["Stock Quantity"].text().strip())
            gst_percentage = float(self.entries["GST %"].text().strip())
            
            if not all([name, category, manufacturer, batch_no, expiry_date]):
                raise ValueError("All fields must be filled!")
            
            return name, category, manufacturer, batch_no, expiry_date, price, stock_quantity, gst_percentage
        except ValueError as e:
            QMessageBox.warning(self, "Input Error", str(e))
            return None
    
    def clear_fields(self):
        for entry in self.entries.values():
            entry.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InventoryUI()
    window.show()
    sys.exit(app.exec())
