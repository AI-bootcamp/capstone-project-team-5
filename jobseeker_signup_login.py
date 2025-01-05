import streamlit as st
import os
from Face_Reco import register_face, verify_face  # Import Face Recognition functions
from job_seeker_logic import JobSeekerLogic  # Logic class for handling database interactions

def sign_up(logic):
    st.subheader("Job Seeker Sign Up")

    jobseeker_id = st.text_input("Enter Jobseeker ID")
    name = st.text_input("Enter Full Name")
    password = st.text_input("Enter Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    bootcamp = st.text_input("Enter Bootcamp Attended")
    resume = st.text_area("Enter Resume Details or Upload Link")
    image_file = st.file_uploader("Upload Profile Image", type=["jpg", "jpeg", "png"])
    captured_image = st.camera_input("Capture Profile Image")

    if st.button("Register"):
        if jobseeker_id and name and password and confirm_password and bootcamp and resume and (image_file or captured_image):
            if password != confirm_password:
                st.error("Passwords do not match!")
                return

            if captured_image:
                image_file = captured_image

            temp_path = f"temp_{jobseeker_id}.jpg"
            with open(temp_path, "wb") as f:
                f.write(image_file.getbuffer())

            success, message = register_face(temp_path, name, jobseeker_id, password, bootcamp, resume)

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

    jobseeker_id = st.text_input("Enter Jobseeker ID")
    password = st.text_input("Enter Password", type="password")

    if st.button("Login with Credentials"):
        if jobseeker_id and password:
            success, message = logic.authenticate_job_seeker(jobseeker_id, password)

            if success:
                st.success(f"Login successful! Welcome, {message}.")
            else:
                st.error(f"Login failed: {message}")
        else:
            st.error("Please provide both Jobseeker ID and Password.")

def login_with_face_id():
    st.subheader("Login with Face ID")

    image_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    captured_image = st.camera_input("Capture an image")

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
            st.error("Please upload or capture an image.")

def main():
    db_path = "recruitment_platform.db"  # Path to your database
    logic = JobSeekerLogic(db_path=db_path)

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