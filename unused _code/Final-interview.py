import os
import datetime
import streamlit as st
import requests
import pdfplumber
from audio_recorder_streamlit import audio_recorder
from groq import Groq
from streamlit_webrtc import webrtc_streamer



# Initialize Whisper API client
client = Groq(api_key="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")

# Function to process CV from PDF
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

# Function: Generate a Follow-up Question
def generate_dynamic_question(previous_answer , cv_text):
    API_URL = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer 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",
        "Content-Type": "application/json"
    }
    prompt = f"Based on the following response, generate a follow-up question:\n\nResponse: {previous_answer}\n\nFollow-up Question: and {cv_text}"
    payload = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 100,
        "temperature": 0.6,
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        st.error(f"API Error: {response.status_code}, {response.text}")
        return None

# Function: Save Audio File
def save_audio_file(audio_bytes, file_extension="mp3"):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"audio_{timestamp}.{file_extension}"
    with open(file_name, "wb") as f:
        f.write(audio_bytes)
    return file_name

# Function: Transcribe Audio with Whisper
def audio_to_text(filepath):
    with open(filepath, "rb") as file:
        translation = client.audio.translations.create(
            file=(filepath, file.read()),
            model="whisper-large-v3",
        )
    return translation.text

# Function: Generate Feedback for the Interview
def generate_feedback(questions_and_answers):
    API_URL = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer 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",
        "Content-Type": "application/json"
    }
    prompt = (
        "Here is a summary of a mock interview session. Please analyze the answers and provide constructive feedback "
        "on how to improvement for future interviews and Strengths .\n\n"
        "Questions and Answers:\n\n" +
        questions_and_answers +
        "\n\nImprovement Tips:"
    )
    payload = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500,
        "temperature": 0.7,
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        st.error(f"API Error: {response.status_code}, {response.text}")
        return None

# Page 1: CV Upload and Classification
def upload_cv_page():
    st.title("Welcome to the Sure platform!")
    uploaded_file = st.file_uploader("# Upload your CV (PDF)", type="pdf")
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
                st.session_state.classified_data = classified_data
                st.rerun()

def interview_page():
    st.title("Your interview has started with Sure")

    # Initialize session state variables
    if "questions" not in st.session_state:
        st.session_state.questions = ["Tell me about yourself."]
    if "answers" not in st.session_state:
        st.session_state.answers = []
    if "current_question" not in st.session_state:
        st.session_state.current_question = st.session_state.questions[0]

    # Display current question
    st.write(f"## Current Question: {st.session_state.current_question}")

    # Input field for user's answer
    st.write("### Record your answer:")
    audio_bytes = audio_recorder()

    user_answer = None
    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")
        file_path = save_audio_file(audio_bytes)
        transcription = audio_to_text(file_path)
        user_answer = transcription

    # Save the answer and generate a new question
    if st.button("Submit Answer"):
        if user_answer:
            st.session_state.answers.append(user_answer)
            st.session_state.questions.append(st.session_state.current_question)

            # Use the last provided answer as `previous_answer`
            previous_answer = st.session_state.answers[-1]
            cv_text = st.session_state.classified_data  # Ensure `cv_text` is available in session_state

            # Generate a new question
            new_question = generate_dynamic_question(previous_answer, cv_text)
            if new_question:
                st.session_state.current_question = new_question
        else:
            st.warning("Please provide an answer.")

    # End the interview session
    if st.button("End Interview"):
        # Compile all questions and answers
        questions_and_answers = "\n".join(
            f"Q: {q}\nA: {a}" for q, a in zip(st.session_state.questions, st.session_state.answers)
        )
        st.write("### Interview Summary")
        st.write(questions_and_answers)

        # Generate feedback
        feedback = generate_feedback(questions_and_answers)
        st.write("### Feedback for Improvement")
        st.write(feedback)

        # Reset session state
        st.session_state.questions = []
        st.session_state.answers = []
        st.session_state.current_question = "Tell me about yourself."

# # Page 2: Dynamic Interview
# def interview_page():
#     st.title("Your interview has started with Sure")

#     # Initialize session state variables
#     if "questions" not in st.session_state:
#         st.session_state.questions = ["Tell me about yourself."]
#     if "answers" not in st.session_state:
#         st.session_state.answers = []
#     if "current_question" not in st.session_state:
#         st.session_state.current_question = st.session_state.questions[0]

#     # Display current question
#     st.write(f"## Current Question: {st.session_state.current_question}")

#     # Input field for user's answer
#     st.write("### record your answer:")
#     # webrtc_streamer(
#     #         key="webcam",
#     #         media_stream_constraints={"video": True, "audio": False},)
#     audio_bytes = audio_recorder()

#     if audio_bytes:
#         st.audio(audio_bytes, format="audio/wav")
#         file_path = save_audio_file(audio_bytes)
#         transcription = audio_to_text(file_path)
#         # st.write("### Transcription:")
#         user_answer = transcription

#     # Save the answer and generate a new question
#     if st.button("Submit Answer"):
#         if user_answer:
#             st.session_state.answers.append(user_answer)
#             st.session_state.questions.append(st.session_state.current_question)
#             new_question = generate_dynamic_question(previous_answer , cv_text)
#             if new_question:
#                 st.session_state.current_question = new_question
#         else:
#             st.warning("Please provide an answer.")

#     # End the interview session
#     if st.button("End Interview"):
#         # Compile all questions and answers
#         questions_and_answers = "\n".join(
#             f"Q: {q}\nA: {a}" for q, a in zip(st.session_state.questions, st.session_state.answers)
#         )
#         st.write("### Interview Summary")
#         st.write(questions_and_answers)

#         # Generate feedback
#         feedback = generate_feedback(questions_and_answers)
#         st.write("### Feedback for Improvement")
#         st.write(feedback)

#         # Reset session state
#         st.session_state.questions = []
#         st.session_state.answers = []
#         st.session_state.current_question = "Tell me about yourself."

# Main Application
def main():
    if 'step' not in st.session_state:
        st.session_state.step = "upload"

    if st.session_state.step == "upload":
        upload_cv_page()
    elif st.session_state.step == "interview":
        interview_page()

if __name__ == "__main__":
    main()
