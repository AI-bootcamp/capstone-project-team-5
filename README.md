![surelogo](https://github.com/user-attachments/assets/beba74e4-1db3-4d4c-8930-f05531999962)

# شُور - AI-Powered Recruitment Platform

## Overview

(Sure) شُور
is an AI-powered recruitment platform designed to streamline the hiring process for both job seekers and HR representatives. The platform leverages advanced technologies such as facial recognition, natural language processing (NLP), and machine learning to provide a seamless and efficient recruitment experience.

---
## Features

### For Job Seekers:
| Feature               | Description                                                                 |
|-----------------------|-----------------------------------------------------------------------------|
| **CV Upload & Parsing** | Upload CVs in PDF format; extract key details (name, phone, email) via NLP and regex. |
| **Dynamic Interview**  | AI-powered interviews with adaptive questions, automatic transcription, and feedback. |
| **Job Applications**   | Apply to jobs with interview id provided by recruiter.      |

### For HR Representatives:
| Feature                  | Description                                                                 |
|--------------------------|-----------------------------------------------------------------------------|
| **Sign Up & Login**      | Register and log in using credentials or Face ID.                |
| **Job Listing Management** | Create, view, and delete job postings.           |
| **Scheduled Interviews** | Access interview schedules, transcripts, summaries, and AI-driven candidate rankings. |



## Technical Details

### Backend:
- **Database**: SQLite is used to store all data, including job listings, job seekers, HR representatives, and interview data.
- **Facial Recognition**: The platform uses the `DeepFace` library for facial recognition, allowing representatives to log in using their face (GhostFaceNet).
- **NLP & Machine Learning**:
  - **CV Parsing**: The platform uses `pdfplumber` to extract text from PDFs and regex/NLP to extract key information.
  - **Dynamic Interview**: The platform uses Llama models to generate interview questions and provide feedback based on the job seeker's responses.
  - **CV classification**: Llama model is used to classify CV data into skills, experience, and projects.
  - **Whisper**: Used to perform speach to text
- **Recomendation System**: The platform uses Llama to exctract key skills from requirements and summary, then compares the two using bm25 to get a score of the matching rate ( the higher the better. 
### Frontend:
- **Streamlit**: The frontend is built using Streamlit, providing a simple and intuitive user interface for both job seekers and HR representatives.
---


## Prerequisites:
1. **Python 3.8+**: Install from [python.org](https://www.python.org/).
2. **FFMpeg**: Download from [ffmpeg.org](https://ffmpeg.org/) and add to `PATH`.
3. **Groq API Key**: Sign up at [groq.com](https://groq.com/) and replace key where applicable
4. **Install Dependencies**:
  ```
pip install -r requirements.txt
```
## Usage
  ```
streamlit run Home.py
```




