import sqlite3
import hashlib

class CompanyLogic:
    def __init__(self, db_path):
        self.db_path = db_path

    def register_company(self, comp_name, phone_number, password, representative, image_path):
        try:
            # Hash the password for security
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            # Convert image to binary
            with open(image_path, "rb") as img_file:
                image_blob = img_file.read()

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO Company (comp_name, phone_number, password, representative, image_data)
                VALUES (?, ?, ?, ?, ?)
            ''', (comp_name, phone_number, hashed_password, representative, image_blob))

            # Fetch the last inserted company ID
            company_id = cursor.lastrowid

            conn.commit()
            conn.close()
            return True, f"Company registered successfully! Company ID: {company_id}"

        except Exception as e:
            return False, f"Error registering company: {str(e)}"

    def authenticate_company(self, phone_number, password):
        try:
            # Hash the provided password for comparison
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Fetch the stored password, name, and ID for the company using phone number
            cursor.execute('SELECT password, comp_name, company_id FROM Company WHERE phone_number = ?', (phone_number,))
            result = cursor.fetchone()

            if not result:
                conn.close()
                return False, "Invalid Phone Number or Password."

            stored_password, company_name, company_id = result

            # Compare the hashed input password with the stored hashed password
            if hashed_password == stored_password:
                conn.close()
                return True, f"Company Name: {company_name}, Company ID: {company_id}"

            conn.close()
            return False, "Invalid Phone Number or Password."

        except Exception as e:
            return False, f"Error during authentication: {str(e)}"