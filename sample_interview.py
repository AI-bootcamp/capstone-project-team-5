sample_interviews = [
    ("John Doe", "123-456-7890", "john.doe@example.com", "This is the transcript of John's interview.", "John demonstrated strong technical skills and good communication.", 85, 1000),
    ("Jane Smith", "234-567-8901", "jane.smith@example.com", "This is the transcript of Jane's interview.", "Jane showed excellent problem-solving abilities.", 90, 1000),
    ("Alice Johnson", "345-678-9012", "alice.johnson@example.com", "This is the transcript of Alice's interview.", "Alice has a good understanding of the required technologies.", 78, 1000),
    ("Bob Brown", "456-789-0123", "bob.brown@example.com", "This is the transcript of Bob's interview.", "Bob has relevant experience but needs improvement in communication.", 65, 1000),
    ("Charlie Davis", "567-890-1234", "charlie.davis@example.com", "This is the transcript of Charlie's interview.", "Charlie is a quick learner and fits well with the team culture.", 88, 1000)
]

import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('sure_platform.db')
cursor = conn.cursor()

# Insert sample rows into the Interview table
cursor.executemany('''
INSERT INTO Interview (Applicant_name, Applicant_phone, Applicant_email, Audio_transcript, Interview_summary, Ranking_score, interview_id)
VALUES (?, ?, ?, ?, ?, ?, ?)
''', sample_interviews)

# Commit the transaction and close the connection
conn.commit()
conn.close()

print("Sample rows inserted successfully!")