import sqlite3
from deepface import DeepFace
import cv2
import numpy as np
import base64
import io
import os
import shutil

def image_to_blob(image_path):
    # Read image and convert to blob
    img = cv2.imread(image_path)
    _, buffer = cv2.imencode('.jpg', img)
    return buffer.tobytes()

def blob_to_temp_file(blob_data):
    # Convert blob back to image and save temporarily
    nparr = np.frombuffer(blob_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    temp_path = f"temp_{os.urandom(4).hex()}.jpg"
    cv2.imwrite(temp_path, img)
    return temp_path

def register_face(image_path, person_name, jobseeker_id, password, bootcamp, resume):
    try:
        # Use a consistent model name
        model_name = "GhostFaceNet"  # Ensure this is the same in both functions

        # Change detector_backend to a faster option like 'opencv'
        face = DeepFace.extract_faces(image_path, detector_backend='opencv')

        # Get embedding for the image
        embedding = DeepFace.represent(
            image_path,
            model_name=model_name,  # Use the consistent model name
            detector_backend='opencv',
            enforce_detection=False,
            align=True
        )[0]['embedding']

        # Convert embedding to a blob
        embedding_blob = base64.b64encode(np.array(embedding, dtype=np.float64)).decode('utf-8')

        # Store information in the jobseeker table
        conn = sqlite3.connect('recruitment_platform.db')  # Path to the shared database
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO jobseeker (jobseeker_id, name, password, bootcamp, resume, embedding)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (jobseeker_id, person_name, password, bootcamp, resume, embedding_blob))

        conn.commit()
        conn.close()

        return True, "Face registered successfully!"

    except Exception as e:
        return False, f"Error registering face: {str(e)}"

def cosine_distance(embedding1, embedding2):
    """Calculate cosine distance between two embeddings"""
    dot_product = np.dot(embedding1, embedding2)
    norm1 = np.linalg.norm(embedding1)
    norm2 = np.linalg.norm(embedding2)
    return 1 - (dot_product / (norm1 * norm2))

def verify_face(image_path):
    try:
        # Use a consistent model name
        model_name = "GhostFaceNet"  # Ensure this is the same in both functions

        # Change detector_backend to a faster option like 'opencv'
        detector_backend = 'opencv'

        conn = sqlite3.connect('recruitment_platform.db')  # Path to the shared database
        cursor = conn.cursor()

        # Check if there are any registered users
        cursor.execute('SELECT COUNT(*) FROM jobseeker')
        count = cursor.fetchone()[0]

        if count == 0:
            conn.close()
            return False, "No faces in database"

        # Create a temporary file from the uploaded image
        temp_input_path = f"temp_input_{os.urandom(4).hex()}.jpg"

        try:
            # If image_path is a file-like object (UploadFile)
            if hasattr(image_path, 'file'):
                with open(temp_input_path, 'wb') as f:
                    shutil.copyfileobj(image_path.file, f)
            # If image_path is a string path
            elif isinstance(image_path, str):
                if os.path.isfile(image_path):
                    shutil.copy(image_path, temp_input_path)
                else:
                    return False, "Invalid image path"
            else:
                return False, "Unsupported image format"

            # Get embedding for the input image
            input_embedding = DeepFace.represent(
                temp_input_path,
                model_name=model_name,  # Use the consistent model name
                detector_backend=detector_backend,
                enforce_detection=False,
                align=True
            )[0]['embedding']

            # Get all stored embeddings
            cursor.execute('SELECT jobseeker_id, name, embedding FROM jobseeker')
            registered_faces = cursor.fetchall()

            best_match = None
            min_distance = float('inf')

            for jobseeker_id, name, embedding_blob in registered_faces:
                # Convert stored embedding back to numpy array
                db_embedding = np.frombuffer(
                    base64.b64decode(embedding_blob), 
                    dtype=np.float64
                )

                # Calculate cosine distance
                distance = cosine_distance(input_embedding, db_embedding)

                print(f"Distance for {name}: {distance}")

                if distance < min_distance:
                    min_distance = distance
                    best_match = (jobseeker_id, name, 1 - distance)

        finally:
            # Clean up input temp file
            if os.path.exists(temp_input_path):
                os.remove(temp_input_path)

        conn.close()

        # Threshold for GhostFaceNet (may need adjustment)
        threshold = 0.45
        if best_match and min_distance < threshold:
            confidence = best_match[2]
            return True, f"Match found! Jobseeker ID: {best_match[0]}, Name: {best_match[1]} (Confidence: {confidence:.2%})"
        else:
            return False, f"No match found in database (Best distance: {min_distance:.2f})"

    except Exception as e:
        print(f"Verification error: {str(e)}")  # Debug print
        return False, f"Error during verification: {str(e)}"

def capture_image():
    """Capture image from webcam"""
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        cv2.imshow('Capture Image (Press SPACE to capture, Q to quit)', frame)

        key = cv2.waitKey(1)
        if key == 32:  # SPACE key
            img_path = f"temp_{os.urandom(4).hex()}.jpg"
            cv2.imwrite(img_path, frame)
            cap.release()
            cv2.destroyAllWindows()
            return img_path
        elif key == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            return None

def get_all_users():
    conn = sqlite3.connect('recruitment_platform.db')  # Path to the shared database
    cursor = conn.cursor()

    cursor.execute('''
        SELECT jobseeker_id, name, bootcamp, resume 
        FROM jobseeker 
        ORDER BY jobseeker_id DESC
    ''')

    users = []
    for row in cursor.fetchall():
        users.append({
            'jobseeker_id': row[0],
            'name': row[1],
            'bootcamp': row[2],
            'resume': row[3]
        })

    conn.close()
    return users

def main():
    while True:
        print("\n1. Register new jobseeker")
        print("2. Verify face")
        print("3. Exit")
        choice = input("Enter your choice (1-3): ")

        if choice == "1":
            jobseeker_id = input("Enter jobseeker ID: ")
            name = input("Enter name: ")
            password = input("Enter password: ")
            bootcamp = input("Enter bootcamp: ")
            resume = input("Enter resume (link or details): ")
            print("1. Upload image")
            print("2. Capture from webcam")
            img_choice = input("Enter choice (1-2): ")

            if img_choice == "1":
                image_path = input("Enter image path: ")
            else:
                image_path = capture_image()
                if not image_path:
                    continue

            success, message = register_face(image_path, name, jobseeker_id, password, bootcamp, resume)
            print(message)

            # Clean up temporary capture file
            if img_choice == "2" and os.path.exists(image_path):
                os.remove(image_path)

        elif choice == "2":
            print("1. Upload image")
            print("2. Capture from webcam")
            img_choice = input("Enter choice (1-2): ")

            if img_choice == "1":
                image_path = input("Enter image path: ")
            else:
                image_path = capture_image()
                if not image_path:
                    continue

            success, message = verify_face(image_path)
            print(message)

            # Clean up temporary capture file
            if img_choice == "2" and os.path.exists(image_path):
                os.remove(image_path)

        elif choice == "3":
            break

if __name__ == "__main__":
    main()