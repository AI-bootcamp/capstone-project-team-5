import streamlit as st
import os
import sqlite3
from FaceRecognition import register_face, verify_face
from company_logic import CompanyLogic
import job_listing_page  # Import the job listing page
import view_interviews  # Import the view interviews page


def sign_up(logic):
    st.subheader("Company Sign Up")

    comp_name = st.text_input("Enter Company Name")
    representative = st.text_input("Enter Representative Name")
    password = st.text_input("Enter Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    image_file = st.file_uploader("Upload Personal Photo", type=["jpg", "jpeg", "png"])
    captured_image = st.camera_input("Capture Personal Photo")

    if st.button("Register"):
        if comp_name and representative and password and confirm_password and (image_file or captured_image):
            if password != confirm_password:
                st.error("Passwords do not match!")
                return

            if captured_image:
                image_file = captured_image

            temp_path = f"temp_{comp_name}.jpg"
            with open(temp_path, "wb") as f:
                f.write(image_file.getbuffer())

            success, message = register_face(temp_path, comp_name, password, representative)

            if success:
                st.success("Registration successful! You can now log in.")
            else:
                st.error(f"Registration failed: {message}")

            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
        else:
            st.error("All fields are required!")

def login_with_credentials(logic):
    st.subheader("Login with Credentials")

    comp_name = st.text_input("Enter Company Name")
    password = st.text_input("Enter Password", type="password")

    if st.button("Login with Credentials"):
        if comp_name and password:
            success, message = logic.authenticate_company(comp_name, password)

            if success:
                # Fetch the company_id after successful login
                conn = sqlite3.connect(logic.db_path)
                cursor = conn.cursor()
                cursor.execute('SELECT company_id FROM Company WHERE comp_name = ?', (comp_name,))
                result = cursor.fetchone()
                conn.close()

                if result:
                    company_id = result[0]
                    st.session_state['company_id'] = company_id  # Store company_id in session state
                    st.session_state['is_logged_in'] = True  # Set login status to True
                    st.success(f"Login successful! Welcome, {message}.")
                else:
                    st.error("Company ID not found.")
            else:
                st.error(f"Login failed: {message}")
        else:
            st.error("Please provide both Company Name and Password.")

def login_with_face_id():
    st.subheader("Login with Face ID")

    image_file = st.file_uploader("Upload Personal Photo", type=["jpg", "jpeg", "png"])
    captured_image = st.camera_input("Capture Personal Photo")

    if st.button("Login with Face ID"):
        if image_file or captured_image:
            if captured_image:
                image_file = captured_image

            temp_path = f"temp_face_login_{os.urandom(4).hex()}.jpg"
            with open(temp_path, "wb") as f:
                f.write(image_file.getbuffer())

            success, message, company_id = verify_face(temp_path)

            if success:
                st.session_state['company_id'] = company_id  # Store company_id in session state
                st.session_state['is_logged_in'] = True  # Set login status to True
                st.success(message)
            else:
                st.error(message)

            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
        else:
            st.error("Please upload or capture yourself!")

def main():
    db_path = "sure_platform.db"  # Path to your database
    logic = CompanyLogic(db_path=db_path)

    # Initialize session state for navigation
    if 'is_logged_in' not in st.session_state:
        st.session_state['is_logged_in'] = False

    # If logged in, show the job listing page or the interviews page
    if st.session_state['is_logged_in']:
        if 'current_job_key' in st.session_state:
            view_interviews.main()  # Call the view interviews page
        else:
            job_listing_page.main()  # Call the job listing page
        return  # Stop further execution of the login/signup page

    # If not logged in, show the login/signup page
    st.sidebar.title("Navigation")
    functionality = st.sidebar.radio("Go to", ["Sign Up", "Login with Credentials", "Login with Face ID"])

    if functionality == "Sign Up":
        sign_up(logic)
    elif functionality == "Login with Credentials":
        login_with_credentials(logic)
    elif functionality == "Login with Face ID":
        login_with_face_id()

if __name__ == "__main__":
    main()