import streamlit as st
import sqlite3

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('sure_platform.db')  # Updated database name
    return conn

# Function to create a job listing and return the job_key
def create_job_listing(company_id, job_title, description, requirements, hr_questions):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT INTO Job_Listing (company_id, job_title, description, requirements, HR_questions)
        VALUES (?, ?, ?, ?, ?)
        ''', (company_id, job_title, description, requirements, hr_questions))
        conn.commit()

        # Get the last inserted job_key
        job_key = cursor.lastrowid
        st.success("Job listing created successfully!")
        return job_key  # Return the job_key
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None
    finally:
        conn.close()

# Streamlit app
def main():
    st.title("Create Job Listing")

    # Check if company is logged in
    if 'company_id' not in st.session_state:
        st.error("You must log in to create a job listing.")
        return

    # Display company name
    st.write(f"Logged in as: {st.session_state['comp_name']}")

    # Input fields for job listing
    job_title = st.text_input("Job Title")
    description = st.text_area("Job Description")
    requirements = st.text_area("Requirements")
    hr_questions = st.text_area("HR Questions")

    if st.button("Create Job Listing"):
        if job_title and description and requirements and hr_questions:
            job_key = create_job_listing(
                st.session_state['company_id'],
                job_title,
                description,
                requirements,
                hr_questions
            )
            if job_key:
                st.success(f"Job listing created successfully! Job Key: {job_key}")
        else:
            st.error("Please fill out all fields.")

# Run the app
if __name__ == "__main__":
    main()
