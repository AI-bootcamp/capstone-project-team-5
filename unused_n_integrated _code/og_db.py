import sqlite3

# Connect to SQLite database (or create it)
conn = sqlite3.connect('recruitment_platform.db')  # Change the filename as needed
cursor = conn.cursor()

# Create the Representative table (with password)
cursor.execute('''
CREATE TABLE IF NOT EXISTS Representative (
    rep_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    rep_name TEXT NOT NULL,
    rep_email TEXT NOT NULL UNIQUE,
    rep_phone TEXT NOT NULL,
    password TEXT NOT NULL,
    FOREIGN KEY (company_id) REFERENCES Company(company_id)
);
''')

# Create the Company table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Company (
    company_id INTEGER PRIMARY KEY AUTOINCREMENT,
    comp_name TEXT NOT NULL UNIQUE,
    representative INTEGER,
    FOREIGN KEY (representative) REFERENCES Representative(rep_id)
);
''')

# Create the Job_Listing table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Job_Listing (
    job_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    job_title TEXT NOT NULL,
    description TEXT NOT NULL,
    skills TEXT NOT NULL,
    openings INTEGER NOT NULL,
    targeted_bootcamp TEXT,
    FOREIGN KEY (company_id) REFERENCES Company(company_id)
);
''')

# Create the Jobseeker table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Jobseeker (
    jobseeker_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    image_data BLOB,
    embedding BLOB,
    password TEXT NOT NULL,
    bootcamp TEXT,
    resume TEXT
);
''')

# Create the Interview table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Interview (
    interview_id INTEGER PRIMARY KEY AUTOINCREMENT,
    jobseeker_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL,
    transcript_raw TEXT,
    transcript TEXT,
    summary TEXT,
    FOREIGN KEY (jobseeker_id) REFERENCES Jobseeker(jobseeker_id),
    FOREIGN KEY (job_id) REFERENCES Job_Listing(job_id)
);
''')

# Create the Job_Application table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Job_Application (
    application_id INTEGER PRIMARY KEY AUTOINCREMENT,
    jobseeker_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL,
    application_date TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    notes TEXT,
    FOREIGN KEY (jobseeker_id) REFERENCES Jobseeker(jobseeker_id),
    FOREIGN KEY (job_id) REFERENCES Job_Listing(job_id)
);
''')

# Commit and close the connection
conn.commit()
conn.close()

print("Database created successfully!")
