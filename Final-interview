import os
import datetime
import streamlit as st
import requests
from audio_recorder_streamlit import audio_recorder
from groq import Groq

# Initialize Whisper API client
client = Groq(api_key="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")

# Function: Generate a Follow-up Question
def generate_dynamic_question(previous_answer):
    API_URL = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer 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",
        "Content-Type": "application/json"
    }
    prompt = f"Based on the following response, generate a follow-up question:\n\nResponse: {previous_answer}\n\nFollow-up Question:"
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
        "on how to improve for future interviews.\n\n"
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

# Streamlit Application
def main():
    st.title("Dynamic Interview System with Whisper")

    # Initialize session state variables
    if "questions" not in st.session_state:
        st.session_state.questions = ["Tell me about yourself."]
    if "answers" not in st.session_state:
        st.session_state.answers = []
    if "current_question" not in st.session_state:
        st.session_state.current_question = st.session_state.questions[0]

    # Display current question
    st.write(f"### Current Question: {st.session_state.current_question}")

    # Input field for user's answer
    st.write("#### Answer Options:")
    user_answer = st.text_input("Type your answer:")
    st.write("OR record your answer:")
    audio_bytes = audio_recorder()

    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")
        file_path = save_audio_file(audio_bytes)
        transcription = audio_to_text(file_path)
        st.write("### Transcription:")
        st.write(transcription)
        user_answer = transcription

    # Save the answer and generate a new question
    if st.button("Submit Answer"):
        if user_answer:
            st.session_state.answers.append(user_answer)
            st.session_state.questions.append(st.session_state.current_question)
            new_question = generate_dynamic_question(user_answer)
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

if __name__ == "__main__":
    main()
