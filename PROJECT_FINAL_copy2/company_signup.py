import streamlit as st
import os
from FaceRecognition import register_face, verify_face 
from company_logic import CompanyLogic

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
                st.success(f"Login successful! Welcome, {message}.")
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

            success, message = verify_face(temp_path)

            if success:
                st.success(message)
            else:
                st.error(message)

            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
        else:
            st.error("Please upload or capture yourself!")

def main():
    db_paths = "sure_platform.db"  # Path to your database
    logic = CompanyLogic(db_path=db_paths)

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
