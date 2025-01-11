import streamlit as st
import subprocess

# Homepage
def home_page():
    st.title("Welcome to مُيسِّر")
    st.markdown("### Revolutionizing Recruitment with AI-Powered Features")
    st.markdown("---")
    st.subheader("Choose Your Role")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Job Seeker"):
            # Redirect to Job Seeker Signup/Login page
            subprocess.run(["streamlit", "run", "job_seeker_home.py"])

    with col2:
        if st.button("HR Representative"):
            # Redirect to HR Representative Signup/Login page
            subprocess.run(["streamlit", "run", "companies_home.py"])

if __name__ == "__main__":
    home_page()
