import sqlite3

# Connect to SQLite database (or create it)
conn = sqlite3.connect('sure_platform.db')  # Change the filename as needed
cursor = conn.cursor()




# Create the Job_Listing table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Job_Listing (
    job_key INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    job_title TEXT NOT NULL,
    description TEXT NOT NULL,
    requirements TEXT NOT NULL,
    HR_questions INTEGER NOT NULL, # these will be text questions separated by commas
    FOREIGN KEY (company_id) REFERENCES Company(company_id)
);
''')

# Insert a dummy row to set the auto-increment starting point
try:
    cursor.execute('''
    INSERT INTO Job_Listing (job_key, company_id, job_title, description, requirements, HR_questions)
    VALUES (999, 0, 'Dummy Job', 'Dummy Description', 'Dummy Requirements', 0)
    ''')
    conn.commit()
except sqlite3.IntegrityError:
    # If the dummy row already exists, ignore the error
    pass

# Delete the dummy row
cursor.execute('DELETE FROM Job_Listing WHERE job_key = 999;')
conn.commit()

# Drop the existing Interview table if it exists
cursor.execute('DROP TABLE IF EXISTS Interview;')

# Create the new Interview table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Interview (
    Applicant_name TEXT NOT NULL,
    Applicant_phone TEXT PRIMARY KEY,
    Audio_transcript TEXT,
    Interview_summary TEXT,
    interview_id INTEGER NOT NULL,
    FOREIGN KEY (interview_id) REFERENCES Job_Listing(job_key)
);
''')

# Commit and close the connection
conn.commit()
conn.close()

print("Database updated successfully!")