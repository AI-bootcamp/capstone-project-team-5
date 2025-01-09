import sqlite3
import hashlib

class CompanyLogic:
    def __init__(self, db_path):
        self.db_path = db_path

    def register_company(self, comp_name, password, representative, image_path):
        try:
            # Hash the password for security
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            # Convert image to binary
            with open(image_path, "rb") as img_file:
                image_blob = img_file.read()

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO Company (comp_name, password, representative, image_data)
                VALUES (?, ?, ?, ?)
            ''', (comp_name, hashed_password, representative, image_blob))

            conn.commit()
            conn.close()
            return True, "Company registered successfully!"

        except Exception as e:
            return False, f"Error registering company: {str(e)}"

    def authenticate_company(self, comp_name, password):
        try:
            # Hash the provided password for comparison
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Fetch the stored password and name for the company
            cursor.execute('SELECT password, comp_name FROM Company WHERE comp_name = ?', (comp_name,))
            result = cursor.fetchone()

            if not result:
                conn.close()
                return False, "Invalid Company Name or Password."

            stored_password, company_name = result

            # Compare the hashed input password with the stored hashed password
            if hashed_password == stored_password:
                conn.close()
                return True, company_name

            conn.close()
            return False, "Invalid Company Name or Password."

        except Exception as e:
            return False, f"Error during authentication: {str(e)}"