import sqlite3
import hashlib

class CompanyLogic:
    def __init__(self, db_path):
        self.db_path = db_path

    def register_company(self, company_name, company_id, rep_name, email, phone, password):
        try:
            # Hash the password for security
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Insert into Company table if not exists
            cursor.execute('''
                INSERT OR IGNORE INTO Company (company_id, comp_name)
                VALUES (?, ?)
            ''', (company_id, company_name))

            # Insert into Representative table
            cursor.execute('''
                INSERT INTO Representative (company_id, rep_name, rep_email, rep_phone, password)
                VALUES (?, ?, ?, ?, ?)
            ''', (company_id, rep_name, email, phone, hashed_password))

            conn.commit()
            conn.close()
            return True, "Company and representative registered successfully!"

        except Exception as e:
            return False, f"Error registering company: {str(e)}"

    def authenticate_with_rep_id(self, rep_id, password):
        try:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT rep_name FROM Representative WHERE rep_id = ? AND password = ?
            ''', (rep_id, hashed_password))
            result = cursor.fetchone()

            conn.close()
            return (True, result[0]) if result else (False, "Invalid Representative ID or Password.")

        except Exception as e:
            return False, f"Error during authentication: {str(e)}"

    def authenticate_with_email(self, email, password):
        try:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT rep_name FROM Representative WHERE rep_email = ? AND password = ?
            ''', (email, hashed_password))
            result = cursor.fetchone()

            conn.close()
            return (True, result[0]) if result else (False, "Invalid Email or Password.")

        except Exception as e:
            return False, f"Error during authentication: {str(e)}"