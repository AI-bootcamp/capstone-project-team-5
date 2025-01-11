import streamlit as st
from interview_logic import CVProcessor, AudioProcessor, InterviewManager
from streamlit_webrtc import webrtc_streamer
import sqlite3
import pdfplumber
import requests

# Configurations
DB_PATH = "../db/sure_platform.db"
LLM_API_URL = "https://api.groq.com/openai/v1/chat/completions"
LLM_API_KEY = "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"
AUDIO_FILE = "interview_audio.wav"

# Initialize processors
cv_processor = CVProcessor(DB_PATH, LLM_API_URL, LLM_API_KEY)
audio_processor = AudioProcessor()
interview_manager = InterviewManager(DB_PATH, LLM_API_URL, LLM_API_KEY)

# Initialize session state variables
if "step" not in st.session_state:
    st.session_state.step = "job_key"  # Start with the job key page
if "job_key" not in st.session_state:
    st.session_state.job_key = None
if "resume_text" not in st.session_state:
    st.session_state.resume_text = None
if "applicant_name" not in st.session_state:
    st.session_state.applicant_name = None
if "applicant_phone" not in st.session_state:
    st.session_state.applicant_phone = None
if "applicant_email" not in st.session_state:
    st.session_state.applicant_email = None
if "interview_responses" not in st.session_state:
    st.session_state.interview_responses = []
if "current_question" not in st.session_state:
    st.session_state.current_question = None

st.title("AI-Powered CV Classifier and Interview Platform")

# Step 0: Collect Job Key
def job_key_page():
    st.title("Welcome to the Sure Platform")
    st.write("Please enter your job key to proceed.")
    
    # Centered text input field
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        job_key_input = st.text_input("Insert your job key", key="job_key_input")
    
    # Submit button
    if st.button("Submit"):
        if job_key_input:
            try:
                # Convert to integer and validate the job key
                job_key = int(job_key_input)
                job_listing = interview_manager.fetch_job_listing(job_key)
                if job_listing:
                    # Store the job key in session state
                    st.session_state.job_key = job_key
                    st.session_state.step = "upload"  # Move to the next step (resume upload)
                    st.rerun()  # Refresh the page to load the next step
                else:
                    st.error(f"No job listing found for job key: {job_key}")
            except ValueError:
                st.error("Please enter a valid integer for the job key.")
        else:
            st.warning("Please enter a valid job key.")

# Step 1: Upload and Process Resume
if st.session_state.step == "upload":
    st.header("Upload Resume")
    uploaded_file = st.file_uploader("Upload your resume (PDF format)", type=["pdf"])

    if uploaded_file:
        with open("uploaded_resume.pdf", "wb") as f:
            f.write(uploaded_file.getbuffer())
        try:
            # Extract raw text from the resume
            resume_text = cv_processor.process_cv_from_pdf("uploaded_resume.pdf")
            st.session_state.resume_text = resume_text

            # Extract applicant information (name, phone, email) from the resume
            extracted_info = cv_processor.extract_basic_info_from_cv(resume_text)
            st.write("Extracted Information:")
            try:
                lines = extracted_info.splitlines()
                name = ""
                phone = ""
                email = ""

                for line in lines:
                    if "Name:" in line:
                        name = line.split("Name:")[1].strip()
                    elif "Phone:" in line:
                        phone = line.split("Phone:")[1].strip()
                    elif "Email:" in line:
                        email = line.split("Email:")[1].strip()

                # Allow the user to edit the extracted information
                st.session_state.applicant_name = st.text_input("Name:", value=name)
                st.session_state.applicant_phone = st.text_input("Phone:", value=phone)
                st.session_state.applicant_email = st.text_input("Email:", value=email)

                if st.button("Start Interview"):
                    if st.session_state.applicant_name and st.session_state.applicant_phone and st.session_state.applicant_email:
                        st.session_state.step = "interview"
                    else:
                        st.error("Please fill in all your details (name, phone, email).")
            except Exception as e:
                st.error(f"Error in processing the extracted information: {e}")
        except Exception as e:
            st.error(f"Error processing resume: {e}")

# Step 2: Conduct Interview
if st.session_state.step == "interview":
    st.header("Conduct Interview")

    col1, col2 = st.columns([2, 1])

    with col1:
        webrtc_streamer(
            key="webcam",
            media_stream_constraints={"video": True, "audio": False},
        )

    with col2:
        # Generate a question using the resume text and job key
        st.session_state.current_question = interview_manager.interviewer(
            st.session_state.resume_text,  # Raw resume text
            st.session_state.interview_responses,  # List of responses
            st.session_state.job_key  # Job key (job_key)
        )

        st.subheader("Interview Question")
        st.write(st.session_state.current_question)

        if st.button("Record Response"):
            st.info("Recording... Please wait.")
            try:
                audio_processor.record_audio(duration_minutes=18, output_path=AUDIO_FILE)
                response_text = audio_processor.transcribe_audio(AUDIO_FILE)
                st.success(f"Recorded response: {response_text}")
                st.session_state.interview_responses.append(response_text)
            except Exception as e:
                st.error(f"Error recording or processing response: {e}")

        if st.button("End Interview"):
            st.session_state.step = "summary"

# Step 3: Summarize Interview
if st.session_state.step == "summary":
    st.header("Analyze Interview")

    try:
        # Generate the interview summary
        summary = interview_manager.summarize_interview(st.session_state.interview_responses)
        st.success("Interview Summary and Analysis:")
        st.write(summary)

        # Combine all responses into a single raw transcription
        raw_transcription = " ".join(st.session_state.interview_responses)

        # Save interview data to the Interview table
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO Interview (applicant_name, applicant_phone, applicant_email, resume_text, audio_transcript, interview_summary, ranking_score, interview_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            st.session_state.applicant_name,  # Applicant_name
            st.session_state.applicant_phone,  # Applicant_phone
            st.session_state.applicant_email,  # Applicant_email
            st.session_state.resume_text,  # Resume_text
            raw_transcription,  # Audio_transcript
            summary,  # Interview_summary
            0,  # Default ranking score
            st.session_state.job_key  # Job key (job_key) stored as interview_id
        ))
        conn.commit()
        conn.close()

        st.info("Interview data saved to the database!")
    except Exception as e:
        st.error(f"Error saving interview data: {e}")

# Main Application Logic
if st.session_state.step == "job_key":
    job_key_page()