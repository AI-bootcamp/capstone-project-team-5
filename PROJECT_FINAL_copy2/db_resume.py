import sqlite3

def initialize_database(db_path):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cv_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                raw_text TEXT,
                classified_data TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interview (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                raw_transcript TEXT,
                processed_transcript TEXT,
                summary TEXT
            )
        ''')
        conn.commit()
        print("Database initialized successfully.")

if __name__ == "__main__":
    DB_PATH = "interview_data.db"
    initialize_database(DB_PATH)