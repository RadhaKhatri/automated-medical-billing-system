import pdfkit
import mysql.connector
from datetime import datetime
from db import connect_db  # Ensure db.py contains connect_db()

# Configure wkhtmltopdf path
config = pdfkit.configuration(wkhtmltopdf=r"D:\Mydownlod\wkhtmltopdf\bin\wkhtmltopdf.exe")

# Define options to prevent rendering issues
options = {
    'enable-local-file-access': '',  # Required for loading local resources
    'disable-smart-shrinking': '',   # Fix scaling issues
    'no-stop-slow-scripts': '',      # Prevents timeouts on JavaScript
    'load-error-handling': 'ignore', # Ignores errors
    'load-media-error-handling': 'ignore'  # Ignores media loading issues
}

class BillingSystem:
    def __init__(self):
        self.conn = connect_db()
        self.cursor = self.conn.cursor()

    def fetch_medicine(self, medicine_id):
        """Fetch medicine details from the database."""
        self.cursor.execute(
            "SELECT name, price, stock_quantity, gst_percentage FROM medicines WHERE medicine_id = %s",
            (medicine_id,)
        )
        return self.cursor.fetchone()

    def generate_invoice(self, customer_name, items):
        """
        Generate a sales invoice and store sales data.
        items = [{'medicine_id': 1, 'quantity': 2}]
        """
        total_price = 0
        total_gst = 0
        invoice_items = []

        for item in items:
            medicine = self.fetch_medicine(item['medicine_id'])
            if medicine:
                name, price, stock, gst = medicine
                if item['quantity'] > stock:
                    return f"Not enough stock for {name}"

                gst_amount = (price * item['quantity']) * (gst / 100)
                total_gst += gst_amount
                subtotal = (price * item['quantity']) + gst_amount
                total_price += subtotal

                invoice_items.append((name, item['quantity'], price, gst, subtotal))

                # Deduct from stock
                new_stock = stock - item['quantity']
                self.cursor.execute(
                    "UPDATE medicines SET stock_quantity = %s WHERE medicine_id = %s",
                    (new_stock, item['medicine_id'])
                )

                # Insert sale record
                self.cursor.execute(
                    "INSERT INTO sales (medicine_id, quantity, total_price, gst_amount) VALUES (%s, %s, %s, %s)",
                    (item['medicine_id'], item['quantity'], subtotal, gst_amount)
                )

        self.conn.commit()

        # Generate PDF invoice
        invoice_path = self.create_invoice_pdf(customer_name, invoice_items, total_price, total_gst)
        return invoice_path

    def create_invoice_pdf(self, customer_name, items, total, gst):
        """Generate invoice PDF with wkhtmltopdf"""
        invoice_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        invoice_html = f"""
        <html>
        <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ border: 1px solid black; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
        </style>
        </head>
        <body>
            <h2>Siddhanth Medical Shop Invoice</h2>
            <p><strong>Customer:</strong> {customer_name}</p>
            <p><strong>Date:</strong> {invoice_date}</p>
            <table>
                <tr><th>Medicine</th><th>Qty</th><th>Price</th><th>GST%</th><th>Subtotal</th></tr>
        """

        for item in items:
            name, qty, price, gst, subtotal = item
            invoice_html += f"<tr><td>{name}</td><td>{qty}</td><td>{price}</td><td>{gst}%</td><td>{subtotal}</td></tr>"

        invoice_html += f"""
            </table>
            <p><strong>GST Amount:</strong> {gst:.2f}</p>
            <p><strong>Total Amount:</strong> {total:.2f}</p>
        </body>
        </html>
        """

        # Generate the PDF
        invoice_filename = f"invoices/invoice_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"

        try:
            pdfkit.from_string(invoice_html, invoice_filename, configuration=config, options=options)
            print(f"✅ Invoice saved at: {invoice_filename}")
        except Exception as e:
            print("❌ Error generating PDF:", str(e))

        return invoice_filename
