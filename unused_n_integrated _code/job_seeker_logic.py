import sqlite3
import hashlib

class JobSeekerLogic:
    def __init__(self, db_path):
        self.db_path = db_path

    def register_job_seeker(self, jobseeker_id, name, password, bootcamp, resume, image_path):
        try:
            # Hash the password for security
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            # Convert image to binary
            with open(image_path, "rb") as img_file:
                image_blob = img_file.read()

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO jobseeker (jobseeker_id, name, password, bootcamp, resume, image)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (jobseeker_id, name, hashed_password, bootcamp, resume, image_blob))

            conn.commit()
            conn.close()
            return True, "Jobseeker registered successfully!"

        except Exception as e:
            return False, f"Error registering job seeker: {str(e)}"

    def authenticate_job_seeker(self, jobseeker_id, password):
        try:
            # Hash the provided password for comparison
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Fetch the stored password and name for the jobseeker
            cursor.execute('SELECT password, name FROM jobseeker WHERE jobseeker_id = ?', (jobseeker_id,))
            result = cursor.fetchone()

            if not result:
                conn.close()
                return False, "Invalid Jobseeker ID or Password."

            stored_password, name = result

            # Check if the stored password is plain-text
            if len(stored_password) != 64:  # SHA-256 hash length is always 64 characters
                # The password is plain-text, so we hash it
                hashed_stored_password = hashlib.sha256(stored_password.encode()).hexdigest()

                # Update the database with the hashed password
                cursor.execute('UPDATE jobseeker SET password = ? WHERE jobseeker_id = ?', 
                            (hashed_stored_password, jobseeker_id))
                conn.commit()

                # Compare the hashed input password with the newly hashed stored password
                if hashed_password == hashed_stored_password:
                    conn.close()
                    return True, name
            else:
                # Compare the hashed input password with the stored hashed password
                if hashed_password == stored_password:
                    conn.close()
                    return True, name

            conn.close()
            return False, "Invalid Jobseeker ID or Password."

        except Exception as e:
            return False, f"Error during authentication: {str(e)}"
