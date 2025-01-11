import sqlite3

# Function to create a new company
def create_company():
    # Connect to the database
    conn = sqlite3.connect('Alawi_platform.db')
    cursor = conn.cursor()

    # Take user input for company details
    comp_name = input("Enter the company name: ")
    representative = input("Enter the representative's name: ")
    password = input("Enter the company's password: ")

    try:
        # Insert the new company into the Company table
        cursor.execute('''
        INSERT INTO Company (comp_name, representative, password)
        VALUES (?, ?, ?)
        ''', (comp_name, representative, password))

        # Commit the transaction
        conn.commit()
        print("Company created successfully!")

    except sqlite3.IntegrityError:
        print("Error: Company name must be unique. A company with this name already exists.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the connection
        conn.close()

# Run the function
if __name__ == "__main__":
    create_company()