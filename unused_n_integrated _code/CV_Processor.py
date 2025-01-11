import pdfplumber
import sqlite3
import requests

class CVProcessor:
    def __init__(self, db_path, llm_api_url, llm_api_key):
        self.db_path = db_path
        self.llm_api_url = llm_api_url
        self.llm_headers = {
            "Authorization": f"Bearer {llm_api_key}",
            "Content-Type": "application/json"
        }

    def process_cv_from_pdf(self, file_path):
        """
        Extracts text from a PDF file.
        """
        try:
            with pdfplumber.open(file_path) as pdf:
                text = ''.join(page.extract_text() + '\n' for page in pdf.pages)
            return text.strip()
        except Exception as e:
            raise Exception(f"Error reading PDF file: {e}")

    def classify_cv_data_with_llm(self, cv_text):
        """
        Classifies CV data into skills, experience, and projects using an LLM.
        """
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
        response = requests.post(self.llm_api_url, headers=self.llm_headers, json=payload)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            raise Exception(f"API Error: {response.status_code}, {response.text}")

    def extract_and_save_cv_data(self, file_path):
        """
        Processes a CV file, classifies its information, and saves it to the database.
        """
        cv_text = self.process_cv_from_pdf(file_path)
        if not cv_text:
            raise Exception("CV text extraction failed.")
        
        classified_data = self.classify_cv_data_with_llm(cv_text)
        self.save_to_cv_table(cv_text, classified_data)
        return classified_data

    def save_to_cv_table(self, raw_text, classified_data):
        """
        Saves the raw and classified CV data to the database.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO cv_data (raw_text, classified_data)
                VALUES (?, ?)
            ''', (raw_text, classified_data))
            conn.commit()

    def interviewer(self, classified_data, interview_responses):
        """
        Generates the next interview question based on the classified CV data
        and the interview responses so far.
        """
        if not interview_responses:
            return "Talk about yourself."
        else:
            all_responses = " ".join(interview_responses)
            prompt = (
                f"Based on the resume:\n{classified_data}\n\n"
                f"And the interview responses so far:\n{all_responses}\n\n"
                f"Generate a single short and concise interview question. "
                f"The question should be one sentence and focus on the applicant's skills or experience."
            )
            payload = {
                "model": "llama3-8b-8192",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 50,
                "temperature": 0.7,
            }
            response = requests.post(self.llm_api_url, headers=self.llm_headers, json=payload)
            if response.status_code == 200:
                question = response.json()['choices'][0]['message']['content'].strip()
                return question
            else:
                raise Exception(f"API Error: {response.status_code}, {response.text}")

    def summarize_interview(self, interview_responses):
        """
        Summarizes the interview responses and provides feedback on strengths and areas for improvement.
        """
        try:
            raw_transcription = " ".join(interview_responses)
            prompt = (
                f"Summarize the following interview responses:\n\n{raw_transcription}\n\n"
                f"Provide feedback on strengths and areas for improvement."
            )
            payload = {
                "model": "llama3-8b-8192",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 300,
                "temperature": 0.6,
            }
            response = requests.post(self.llm_api_url, headers=self.llm_headers, json=payload)
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content'].strip()
            else:
                raise Exception(f"API Error: {response.status_code}, {response.text}")
        except Exception as e:
            raise Exception(f"Error summarizing interview: {e}")
