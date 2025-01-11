import streamlit as st
import subprocess

def main():
    st.title("Job Seeker Home Page")

    # Display buttons for navigation
    if st.button("Sign Up"):
        # Redirect to the Sign Up functionality
        subprocess.run(["streamlit", "run", "jobseeker_signup_login.py", "--", "signup"])

    if st.button("Login with Credentials"):
        # Redirect to the Login with Credentials functionality
        subprocess.run(["streamlit", "run", "jobseeker_signup_login.py", "--", "login-credentials"])

    if st.button("Login with Face ID"):
        # Redirect to the Login with Face ID functionality
        subprocess.run(["streamlit", "run", "jobseeker_signup_login.py", "--", "login-face"])

if __name__ == "__main__":
    main()
#