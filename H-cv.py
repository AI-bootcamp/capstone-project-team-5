import streamlit as st
import cv2
import sounddevice as sd
import wave
import pyttsx3
import whisper
import requests
import pdfplumber

# STTProcessor Class
class STTProcessor:
    def __init__(self, db_path):
        self.model = whisper.load_model("tiny")  # Whisper model
        self.db_path = db_path
        self.engine = pyttsx3.init()  # Initialize text-to-speech engine

    def start_camera_and_record_audio(self, duration_minutes, audio_output_path, video_output_path):
        # Start Camera
        cap = cv2.VideoCapture(0)  # 0 is the default camera
        if not cap.isOpened():
            print("Error: Could not access camera.")
            return

        # Set video frame size
        cap.set(3, 640)  # Set frame width
        cap.set(4, 480)  # Set frame height

        out = cv2.VideoWriter(video_output_path, cv2.VideoWriter_fourcc(*'XVID'), 20.0, (640, 480))

        # Record audio
        duration_seconds = duration_minutes * 60  # Convert minutes to seconds
        fs = 44100  # Sample rate
        audio_data = sd.rec(int(duration_seconds * fs), samplerate=fs, channels=2, dtype='int16')
        sd.wait()  # Wait for the recording to finish

        with wave.open(audio_output_path, 'wb') as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(fs)
            wf.writeframes(audio_data.tobytes())

        # Capture video for the specified duration
        frames = int(duration_seconds * 20)  # Assuming 20 frames per second
        for _ in range(frames):
            ret, frame = cap.read()
            if ret:
                out.write(frame)
                cv2.imshow('Recording Interview', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to quit early
                break

        cap.release()
        out.release()
        cv2.destroyAllWindows()

    def transcribe_audio(self, audio_path):
        result = self.model.transcribe(audio_path)
        return result['text']

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def process_and_answer(self, audio_path):
        # Convert audio to text using Whisper
        transcript = self.transcribe_audio(audio_path)
        print(f"Transcript: {transcript}")
        response = f"Based on your answer, {transcript}, the next question is..."
        self.speak(response)
        return response


# Function to process CV
def process_cv_from_pdf(file_path):
    try:
        with pdfplumber.open(file_path) as pdf:
            text = ''
            for page in pdf.pages:
                text += page.extract_text() + '\n'
        return text.strip()
    except Exception as e:
        st.error(f"Error reading PDF file: {e}")
        return None

# Function to classify CV data using LLM
def classify_cv_data_with_llm(cv_text):
    API_URL = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer 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",
        "Content-Type": "application/json"
    }
    prompt = (
        f"Here is a CV extracted from a PDF file. Please classify the key information "
        f"into skills, experience, and projects:\n\n{cv_text}\n\nClassified Information:"
    )
    payload = {
            "model": "llama3-8b-8192",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 400,
            "temperature": 0.6,
        }
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        st.error(f"API Error: {response.status_code}, {response.text}")
        return None

# Streamlit page to upload CV
def upload_cv_page():
    st.title("CV Classifier and Interview")
    uploaded_file = st.file_uploader("Upload your CV (PDF)", type="pdf")
    if uploaded_file is not None:
        with open("uploaded_cv.pdf", "wb") as f:
            f.write(uploaded_file.getbuffer())
        cv_text = process_cv_from_pdf("uploaded_cv.pdf")
        if cv_text:
            classified_data = classify_cv_data_with_llm(cv_text)
            st.subheader("Summary of your CV:")
            st.write(classified_data)
            if st.button("Start the Interview"):
                st.session_state.step = "interview"
                st.rerun()

# Streamlit page for interview
def interview_page():
    st.title("Interview")

    # Create two columns for the layout
    col1, col2 = st.columns([1, 2])  # Column 1: Video, Column 2: Questions and Actions

    # Column 1: Camera Feed
    with col1:
        st.subheader("Your Camera Feed")
        cap = cv2.VideoCapture(0)  # Default camera
        if not cap.isOpened():
            st.error("Error: Could not access the camera.")
        else:
            ret, frame = cap.read()
            if ret:
                st.image(frame, channels="BGR")
            cap.release()

    # Column 2: Questions and Actions
    with col2:
        st.subheader("Interview Questions")

        # Display first question
        st.write("Question: What are your strengths?")
        
        # Button to start recording and ask the next question
        if st.button("Start Recording Audio"):
            audio_path = "interview_audio.wav"
            video_path = "interview_video.avi"
            stt_processor = STTProcessor(db_path="your_db_path")  # Specify your database path
            stt_processor.start_camera_and_record_audio(1, audio_path, video_path)  # Record for 1 minute
            st.write("Audio recorded successfully.")
            
            # Step 2: Transcribe audio to text using Whisper
            transcript = stt_processor.transcribe_audio(audio_path)
            st.write("Transcribed Text:")
            st.write(transcript)
            
            # Step 3: Send the text to LLM to get a response
            response = stt_processor.process_and_answer(audio_path)
            st.write("LLM Response:")
            st.write(response)

        # Add button to end the interview
        if st.button("End Interview"):
            st.subheader("Summary of the Interview")
            st.write("Here is a summary of the interview based on your responses:")
            st.write("Summary: Based on your responses, we found you have good communication skills and experience in Python.")

# Main function
def main():
    if 'step' not in st.session_state:
        st.session_state.step = "upload"

    if st.session_state.step == "upload":
        upload_cv_page()
    elif st.session_state.step == "interview":
        interview_page()

if __name__ == "__main__":
    main()
