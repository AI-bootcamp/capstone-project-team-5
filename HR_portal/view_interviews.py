import streamlit as st
import sqlite3

def get_interviews_for_job(job_key):
    conn = sqlite3.connect('../db/sure_platform.db')
    cursor = conn.cursor()

    # Fetch interviews for the specific job listing and sort by Ranking_score in descending order
    cursor.execute('''
        SELECT Applicant_name, Applicant_phone, Applicant_email, Audio_transcript, Interview_summary, Ranking_score
        FROM Interview
        WHERE interview_id = ?
        ORDER BY Ranking_score DESC
    ''', (job_key,))

    interviews = cursor.fetchall()
    conn.close()
    return interviews

def main():
    st.title("Job Listing Interviews")
    st.subheader("The Applicants are sorted based on their compatibility with the job requirements")
    # Check if a job listing is selected
    if 'current_job_key' not in st.session_state:
        st.error("No job listing selected.")
        return

    job_key = st.session_state['current_job_key']
    st.write(f"**Job Key**: {job_key}")

    # Add a "Go Back" button to return to the job listings page
    if st.button("Go Back to Job Listings"):
        # Clear the current job key from the session state
        del st.session_state['current_job_key']
        st.rerun()  # Rerun the app to go back to the job listings page

    # Fetch and display interviews for the selected job listing, sorted by Ranking_score
    interviews = get_interviews_for_job(job_key)

    if interviews:
        st.write("### Interviews (Sorted by Ranking Score)")
        for interview in interviews:
            st.write(f"**Applicant Name**: {interview[0]}")
            st.write(f"**Applicant Phone**: {interview[1]}")
            st.write(f"**Applicant Email**: {interview[2]}")
            # st.write(f"**Ranking Score**: {interview[5]}")
            
            # Add a button to show the transcript and summary in a pop-up-like expander
            with st.expander("View Transcript and Summary"):
                st.write("**Audio Transcript:**")
                st.write(interview[3])  # Display Audio_transcript
                st.write("**Interview Summary:**")
                st.write(interview[4])  # Display Interview_summary
            
            st.write("---")
    else:
        st.info("No interviews found for this job listing.")

if __name__ == "__main__":
    main()