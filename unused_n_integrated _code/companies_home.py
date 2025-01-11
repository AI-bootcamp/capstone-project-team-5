import streamlit as st
import subprocess

def main():
    st.title("Company Portal Home Page")

    # Display buttons for navigation
    if st.button("Sign Up"):
        # Redirect to the Sign Up functionality
        subprocess.run(["streamlit", "run", "companies_signup_login.py", "--", "signup"])

    if st.button("Login with Representative ID"):
        # Redirect to the Login with Representative ID functionality
        subprocess.run(["streamlit", "run", "companies_signup_login.py", "--", "login-rep-id"])

    if st.button("Login with Email"):
        # Redirect to the Login with Email functionality
        subprocess.run(["streamlit", "run", "companies_signup_login.py", "--", "login-email"])

if __name__ == "__main__":
    main()
