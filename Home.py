import streamlit as st
import subprocess

# Homepage
def home_page():
    # Display the logo
    st.image("surelogo.jpg", width=1000)  # Adjust the width as needed

    st.title("Welcome to SURE | شُور")
    st.markdown("### Revolutionizing Recruitment with AI-Powered Features")
    st.markdown("---")
    st.subheader("Choose")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Train for an Interview"):
            # Redirect to Job Seeker Signup/Login page
            subprocess.run(["streamlit", "run", "applicant_side_og.py"])

    with col2:
        if st.button("Applicant Portal"):
            # Redirect to HR Representative Signup/Login page
            subprocess.run(["streamlit", "run", "applicant_side.py"])

    with col3:
        if st.button("HR Portal"):
            # Redirect to Company Signup/Login page
            subprocess.run(["streamlit", "run", "companies_signup.py"])

if __name__ == "__main__":
    home_page()