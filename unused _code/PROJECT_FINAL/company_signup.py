import streamlit as st
import os
from FaceRecognition import register_face, verify_face
from company_logic import CompanyLogic
import job_listing_app

# Initialize session state keys
if 'comp_name' not in st.session_state:
    st.session_state['comp_name'] = None
if 'company_id' not in st.session_state:
    st.session_state['company_id'] = None

def sign_up(logic):
    st.subheader("Company Sign Up")

    comp_name = st.text_input("Enter Company Name")
    phone_number = st.text_input("Enter Phone Number")
    representative = st.text_input("Enter Representative Name")
    password = st.text_input("Enter Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    image_file = st.file_uploader("Upload Personal Photo", type=["jpg", "jpeg", "png"])
    captured_image = st.camera_input("Capture Personal Photo")

    if st.button("Register"):
        if comp_name and phone_number and representative and password and confirm_password and (image_file or captured_image):
            if password != confirm_password:
                st.error("Passwords do not match!")
                return

            if captured_image:
                image_file = captured_image

            temp_path = f"temp_{comp_name}.jpg"
            with open(temp_path, "wb") as f:
                f.write(image_file.getbuffer())

            success, message = logic.register_company(comp_name, phone_number, password, representative, temp_path)

            if success:
                st.success("Registration successful! You can now log in.")
                company_id = message.split('ID: ')[-1]  # Extract company ID
                st.session_state['comp_name'] = comp_name
                st.session_state['company_id'] = company_id
                st.info(f"Your Company ID is: {company_id}. Use it to log in.")
                job_listing_app.main()  # Open job listing app
            else:
                st.error(f"Registration failed: {message}")

            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
        else:
            st.error("All fields are required!")

def login_with_credentials(logic):
    st.subheader("Login with Credentials")

    phone_number = st.text_input("Enter Phone Number")
    password = st.text_input("Enter Password", type="password")

    if st.button("Login with Credentials"):
        if phone_number and password:
            success, message = logic.authenticate_company(phone_number, password)

            if success:
                st.success(f"Login successful! Welcome, {message}.")
                comp_name, company_id = message.split('ID: ')[-2], message.split('ID: ')[-1]
                st.session_state['comp_name'] = comp_name
                st.session_state['company_id'] = company_id
                st.info(f"Your Company ID is: {company_id}.")
                job_listing_app.main()  # Open job listing app
            else:
                st.error(f"Login failed: {message}")
        else:
            st.error("Please provide both Phone Number and Password.")

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

            success, message = verify_face(temp_path)

            if success:
                st.success(message)
                comp_name, company_id = message.split('ID: ')[-2], message.split('ID: ')[-1]
                st.session_state['comp_name'] = comp_name
                st.session_state['company_id'] = company_id
                st.info(f"Your Company ID is: {company_id}.")
                job_listing_app.main()  # Open job listing app
            else:
                st.error(message)

            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
        else:
            st.error("Please upload or capture yourself!")

def main():
    db_path = "sure_platform.db"  # Path to your database
    logic = CompanyLogic(db_path=db_path)

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