import imaplib
import email
import os
from db import connect_db

def fetch_vendor_bills(user_email, app_password, save_folder="vendor_bills"):
    os.makedirs(save_folder, exist_ok=True)

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT email, name FROM vendors WHERE email IS NOT NULL")
    vendors = cursor.fetchall()
    conn.close()

    # Connect to Gmail
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(user_email, app_password)
    mail.select("inbox")

    for vendor_email, vendor_name in vendors:
        # Search emails from each vendor
        status, messages = mail.search(None, f'FROM "{vendor_email}"')
        if status != "OK":
            continue

        for num in messages[0].split():
            _, msg_data = mail.fetch(num, "(RFC822)")
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            for part in msg.walk():
                if part.get_content_maintype() == "multipart":
                    continue
                if part.get("Content-Disposition") is None:
                    continue

                filename = part.get_filename()
                if filename:
                    file_path = os.path.join(save_folder, filename)
                    with open(file_path, "wb") as f:
                        f.write(part.get_payload(decode=True))
                    print(f"✅ Saved {filename} from {vendor_email}")
    mail.logout()
