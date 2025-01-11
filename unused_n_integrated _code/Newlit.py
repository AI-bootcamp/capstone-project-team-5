import streamlit as st
from deepface import DeepFace
import cv2
import numpy as np
import base64
import sqlite3
import os
import shutil
from FaceRecognition import init_database, register_face, verify_face, get_all_users

def main():
    st.title("مُيسِّر")

    # Initialize the database
    init_database()

    # Sidebar for navigation
    st.sidebar.title("Navigation")
    choice = st.sidebar.radio("Go to", ["Register Face", "Verify Face"])

    if choice == "Register Face":
        st.subheader("Register a New Face")
        name = st.text_input("Enter person's name")
        image_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
        captured_image = st.camera_input("Capture an image")

        if st.button("Register"):
            if name and (image_file or captured_image):
                # Determine which image to use
                if captured_image:
                    image_file = captured_image

                # Save the uploaded or captured file temporarily
                temp_path = f"temp_{os.urandom(4).hex()}.jpg"
                with open(temp_path, "wb") as f:
                    f.write(image_file.getbuffer())

                success, message = register_face(temp_path, name)
                
                # Ensure message is a string
                if not isinstance(message, str):
                    message = str(message)
                
                # Display success or error message
                if success:
                    st.success(message)
                else:
                    st.error(message)

                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            else:
                st.error("Please provide a name and an image.")

    elif choice == "Verify Face":
        st.subheader("Verify a Face")
        image_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
        captured_image = st.camera_input("Capture an image")

        if st.button("Verify"):
            if image_file or captured_image:
                # Determine which image to use
                if captured_image:
                    image_file = captured_image

                # Save the uploaded or captured file temporarily
                temp_path = f"temp_{os.urandom(4).hex()}.jpg"
                with open(temp_path, "wb") as f:
                    f.write(image_file.getbuffer())

                success, message = verify_face(temp_path)
                
                # Ensure message is a string
                if not isinstance(message, str):
                    message = str(message)
                
                # Display success or error message
                if success:
                    st.success(message)
                else:
                    st.error(message)

                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            else:
                st.error("Please upload or capture an image.")

if __name__ == "__main__":
    main()
