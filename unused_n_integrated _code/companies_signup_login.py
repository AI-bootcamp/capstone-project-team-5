import streamlit as st
from companies_logic import CompanyLogic
import subprocess

def sign_up(logic):
    st.subheader("Company Sign Up")

    company_name = st.text_input("Enter Company Name")
    company_id = st.text_input("Enter Company ID")
    rep_name = st.text_input("Enter Representative Name")
    email = st.text_input("Enter Representative Email")
    phone = st.text_input("Enter Representative Phone")
    password = st.text_input("Enter Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Register"):
        if company_name and company_id and rep_name and email and phone and password and confirm_password:
            if password != confirm_password:
                st.error("Passwords do not match!")
                return

            success, message = logic.register_company(company_name, company_id, rep_name, email, phone, password)

            if success:
                st.success("Registration successful! You can now log in.")
            else:
                st.error(f"Registration failed: {message}")
        else:
            st.error("All fields are required!")

def login_with_rep_id(logic):
    st.subheader("Login with Representative ID")

    representative_id = st.text_input("Enter Representative ID")
    password = st.text_input("Enter Password", type="password")

    if st.button("Login with Representative ID"):
        if representative_id and password:
            success, message = logic.authenticate_with_rep_id(representative_id, password)

            if success:
                st.success(f"Login successful! Welcome, {message}.")
                # Redirect to Company Dashboard
                subprocess.run(["streamlit", "run", "companies_dashboard.py"])
            else:
                st.error(f"Login failed: {message}")
        else:
            st.error("Please provide both Representative ID and Password.")

def login_with_email(logic):
    st.subheader("Login with Email")

    email = st.text_input("Enter Email")
    password = st.text_input("Enter Password", type="password")

    if st.button("Login with Email"):
        if email and password:
            success, message = logic.authenticate_with_email(email, password)

            if success:
                st.success(f"Login successful! Welcome, {message}.")
                # Redirect to Company Dashboard
                subprocess.run(["streamlit", "run", "companies_dashboard.py"])
            else:
                st.error(f"Login failed: {message}")
        else:
            st.error("Please provide both Email and Password.")

def main():
    db_path = "recruitment_platform.db"  # Path to your database
    logic = CompanyLogic(db_path=db_path)

    st.sidebar.title("Navigation")
    functionality = st.sidebar.radio("Go to", ["Sign Up", "Login with Representative ID", "Login with Email"])

    if functionality == "Sign Up":
        sign_up(logic)
    elif functionality == "Login with Representative ID":
        login_with_rep_id(logic)
    elif functionality == "Login with Email":
        login_with_email(logic)

if __name__ == "__main__":
    main()
