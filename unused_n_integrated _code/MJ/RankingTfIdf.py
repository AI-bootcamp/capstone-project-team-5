import os
import datetime
import streamlit as st
import requests
from audio_recorder_streamlit import audio_recorder
from groq import Groq
import bm25s
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import re
from sklearn.metrics.pairwise import cosine_similarity


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
    
def Extract_skills_JobRequirements(Job_Req):
    API_URL = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer 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",
        "Content-Type": "application/json"
    }
    prompt = fprompt = f"Extract only the names of required skills from the following job requirements. List them directly,use numbers to sort them, one per line, without any additional text or descriptions:\n\nJob Requirements: {Job_Req}\n\nResponse:here are the required skills mentioned in the job requirements:\n"
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

def Extract_skills_InterviewSummary(interview_summary):
    API_URL = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer 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",
        "Content-Type": "application/json"
    }
    prompt = fprompt = f"Extract only the specific names of skills mentioned in the following interview summary and the applicant has stated in the questions and answers that he gave and is good at. List them directly,use numbers to sort them, one per line, without any additional text or descriptions:\n\nInterview Summary: {interview_summary}\n\nResponse:here are the specific names of skills mentioned':\n"
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


def preprocess_skills(skills):
    cleaned_skills = []
    for skill in skills:
        # Remove phrases like "Here are the skills mentioned in the interview summary:"
        if "here are the skills mentioned" in skill.lower() or "here are the names of required skills" in skill.lower():
            continue
        # Remove numbers and bullet points (e.g., "1. English" -> "English")
        skill = re.sub(r'^\d+\.\s*', '', skill)  # Remove numbered prefixes
        skill = re.sub(r'^[\*\+\-]\s*', '', skill)  # Remove bullet points
        skill = re.sub(r'\W+', ' ', skill).lower().strip()  # Remove non-alphanumeric characters
        if skill:  # Only add non-empty skills
            cleaned_skills.append(skill)
    return cleaned_skills

def calculate_tfidf(job_skills, interview_skills):
    vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(1, 2))
    
    # Preprocess skills
    job_skills = preprocess_skills(job_skills)
    interview_skills = preprocess_skills(interview_skills)
    
    # Combine skills into a single list for vectorization
    combined_skills = job_skills + interview_skills
    
    # Fit and transform the combined skills
    tfidf_matrix = vectorizer.fit_transform(combined_skills)
    
    # Split the matrix back into job and interview skills
    job_tfidf = tfidf_matrix[:len(job_skills)]
    interview_tfidf = tfidf_matrix[len(job_skills):]
    
    # Calculate cosine similarity between job and interview skills
    cosine_similarities = cosine_similarity(job_tfidf, interview_tfidf)
    
    return tfidf_matrix, cosine_similarities


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
    if "JobDescriptionSkills" not in st.session_state:

        Job_description = """
        Complete fluency in the English language is required. You should be able to describe code and abstract information in a clear way.
        Proficiency working with any of the following:
        Python, Java, JavaScript / TypeScript, SQL, C/C++/C# and/or HTML
        """
        st.session_state.JobDescriptionSkills = Extract_skills_JobRequirements(Job_description)

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

    # Display the skills extracted from the job description
    st.write("### Skills given from job description")
    st.write(st.session_state.JobDescriptionSkills)

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

        # Extract skills from the feedback summary
        InterviewSkills = Extract_skills_InterviewSummary(feedback)
        st.write("### Skills Extracted from Feedback")
        st.write(InterviewSkills)

        # Calculate TF-IDF scores
        job_skills_list = [skill for skill in st.session_state.JobDescriptionSkills.split('\n') if skill.strip()]
        interview_skills_list = [skill for skill in InterviewSkills.split('\n') if skill.strip()]

        # Clean the skills lists
        job_skills_list = preprocess_skills(job_skills_list)
        interview_skills_list = preprocess_skills(interview_skills_list)

        # Debugging: Print the cleaned skills lists
        print("Job Skills List (Cleaned):", job_skills_list)
        print("Interview Skills List (Cleaned):", interview_skills_list)

        # Get TF-IDF matrix and cosine similarities
        tfidf_matrix, cosine_similarities = calculate_tfidf(job_skills_list, interview_skills_list)

        # Debugging: Print the TF-IDF matrix
        print("TF-IDF Matrix:", tfidf_matrix.toarray())

        # Debugging: Print the cosine similarity matrix
        print("Cosine Similarity Matrix:", cosine_similarities) 

        # Display the scores and calculate the total score
        total_score = 0
        st.write("### TF-IDF Scores for Skills Comparison")
        for i, score in enumerate(cosine_similarities[0]):  # Use the first row for comparison
            st.write(f"Skill: {interview_skills_list[i]}, Score: {score:.2f}")
            total_score += score

        # Display the total score
        st.write(f"### Total Score: {total_score:.2f}")

        # Reset session state
        st.session_state.questions = []
        st.session_state.answers = []
        st.session_state.current_question = "Tell me about yourself."

if __name__ == "__main__":
    main()
