# شُور - AI-Powered Recruitment Platform

## Overview
شُور (Sure) is an AI-powered recruitment platform designed to streamline the hiring process for both job seekers and HR representatives. The platform leverages advanced technologies such as facial recognition, natural language processing (NLP), and machine learning to provide a seamless and efficient recruitment experience.

---

## Features

### For Job Seekers:
1. **Sign Up & Login**:
   - **Credentials**: Job seekers can sign up and log in using their credentials.
   - **Face ID**: Job seekers can log in using facial recognition for a secure and quick login experience.

2. **CV Upload & Parsing**:
   - Job seekers can upload their CVs in PDF format, and the platform will automatically extract key information such as name, phone number, and email using NLP and regex.

3. **Dynamic Interview**:
   - The platform conducts AI-powered interviews where job seekers can answer questions, and the system generates follow-up questions based on their responses.
   - The interview is transcribed, and feedback is provided to the job seeker.

4. **Job Applications**:
   - Job seekers can apply to job listings and track the status of their applications.

---

### For HR Representatives:
1. **Sign Up & Login**:
   - HR representatives can sign up and log in using their credentials or representative ID.

2. **Job Listing Management**:
   - HR representatives can create, view, and delete job listings.
   - Each job listing includes details such as job title, description, required skills, and if the HR want to ask about any specific questions.
    

3. **Scheduled Interviews**:
   - HR representatives can view all scheduled interviews and access interview transcripts and summaries.
   - All interviews are ranked based on the job requirement and the applicant compatibility to the job requirements

4. **Candidate Search**:
   - HR representatives can search for candidates based on skills, experience, and other criteria.

---

## Technical Details

### Backend:
- **Database**: SQLite is used to store all data, including job listings, job seekers, HR representatives, and interview data.
- **Facial Recognition**: The platform uses the `DeepFace` library for facial recognition, allowing representatives to log in using their face (GhostFaceNet).
- **NLP & Machine Learning**:
  - **CV Parsing**: The platform uses `pdfplumber` to extract text from PDFs and regex/NLP to extract key information.
  - **Dynamic Interview**: The platform uses Llama models to generate interview questions and provide feedback based on the job seeker's responses.
  - **CV classification**: Llama model is used to classify CV data into skills, experience, and projects.
  - **Whisper**: Used to perform speach to text 

### Frontend:
- **Streamlit**: The frontend is built using Streamlit, providing a simple and intuitive user interface for both job seekers and HR representatives.

---


### Prerequisites:
- Python 3.8 or higher
- Streamlit
- SQLite
- DeepFace
- pdfplumber
- TensorFlow
- Qrog API Key (for Llama and whisper models)
