import sqlite3

class JobListingLogic:
    def __init__(self, db_path):
        self.db_path = db_path

    def create_job_listing(self, job_id, company_id, job_title, description, requirements, hr_questions):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO Job_Listing (company_id, job_title, description, requirements, HR_questions)
                VALUES (?, ?, ?, ?, ?)
            ''', (company_id, job_title, description, requirements, hr_questions))

            # Get the last inserted row id (job_key)
            job_key = cursor.lastrowid

            conn.commit()
            conn.close()
            return True, "Job listing created successfully!", job_key

        except Exception as e:
            return False, f"Error creating job listing: {str(e)}", None
        
    def get_all_job_listings(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM Job_Listing')
            job_listings = cursor.fetchall()

            conn.close()
            return job_listings

        except Exception as e:
            return None, f"Error retrieving job listings: {str(e)}"

    def delete_job_listing(self, job_id):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('DELETE FROM Job_Listing WHERE job_key = ?', (job_id,))
            conn.commit()
            conn.close()
            return True, "Job listing deleted successfully!"

        except Exception as e:
            return False, f"Error deleting job listing: {str(e)}"