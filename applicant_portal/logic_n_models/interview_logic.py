import pdfplumber
import sqlite3
import requests
import wave
import sounddevice as sd
import whisper

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
        Extract raw text from a PDF resume.

        Parameters:
            file_path (str): Path to the PDF file.

        Returns:
            str: Extracted text from the PDF.
        """
        try:
            with pdfplumber.open(file_path) as pdf:
                text = ''
                for page in pdf.pages:
                    text += page.extract_text() + '\n'
            return text.strip()
        except Exception as e:
            print(f"Error reading PDF file: {e}")
            return None

    def extract_basic_info_from_cv(self, cv_text):
        """
        Extract basic information (name, phone, email) from the CV text using an LLM.

        Parameters:
            cv_text (str): The raw text of the CV.

        Returns:
            str: Extracted information in a structured format.
        """
        prompt = (
            f"Here is a CV extracted from a PDF file. Please extract the key information: "
            f"name, phone number, and email. If any information is missing, set its value to 'null'.\n\n"
            f"CV Content:\n\n{cv_text}"
        )
        payload = {
            "model": "llama3-8b-8192",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 200,
            "temperature": 0.2,
        }
        response = requests.post(self.llm_api_url, headers=self.llm_headers, json=payload)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            raise Exception(f"API Error: {response.status_code}, {response.text}")

    def classify_cv_data_with_llm(self, cv_text):
        """
        Classify CV data (skills, experience, projects) using an LLM.

        Parameters:
            cv_text (str): The raw text of the CV.

        Returns:
            str: Classified information in a structured format.
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

    def save_to_cv_table(self, raw_text, classified_data):
        """
        Save raw CV text and classified data to the cv_data table.

        Parameters:
            raw_text (str): The raw text of the CV.
            classified_data (str): The classified data from the CV.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO cv_data (raw_text, classified_data)
                VALUES (?, ?)
            ''', (raw_text, classified_data))
            conn.commit()

class AudioProcessor:
    def __init__(self):
        self.model = whisper.load_model("tiny")

    def record_audio(self, duration_minutes, output_path):
        """
        Record audio for a specified duration and save it to a file.

        Parameters:
            duration_minutes (int): Duration of the recording in minutes.
            output_path (str): Path to save the recorded audio file.
        """
        duration_seconds = duration_minutes
        fs = 44100
        audio_data = sd.rec(int(duration_seconds * fs), samplerate=fs, channels=2, dtype='int16')
        sd.wait()
        with wave.open(output_path, 'wb') as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(fs)
            wf.writeframes(audio_data.tobytes())

    def transcribe_audio(self, audio_path):
        """
        Transcribe audio to text using Whisper.

        Parameters:
            audio_path (str): Path to the audio file.

        Returns:
            str: Transcribed text.
        """
        result = self.model.transcribe(audio_path)
        return result['text']

class InterviewManager:
    def __init__(self, db_path, llm_api_url, llm_api_key):
        self.db_path = db_path
        self.llm_api_url = llm_api_url
        self.llm_headers = {
            "Authorization": f"Bearer {llm_api_key}",
            "Content-Type": "application/json"
        }

    def interviewer(self, resume_text, interview_responses, job_key):
        """
        Generate a short and concise interview question based on the resume, interview responses,
        and job listing details (title, description, requirements, and HR questions) fetched using the job key.

        Parameters:
            resume_text (str): The raw text of the applicant's resume.
            interview_responses (list): List of the applicant's interview responses so far.
            job_key (int): The job key (interview_id) used to fetch job listing details from the Job_Listing table.

        Returns:
            str: A single interview question.
        """
        # Fetch job listing details from the Job_Listing table using the job key
        job_listing = self.fetch_job_listing(job_key)
        if not job_listing:
            raise Exception(f"No job listing found for job key: {job_key}")

        # Extract job listing details
        job_title = job_listing.get("job_title", "Unknown Job Title")
        job_description = job_listing.get("description", "")
        job_requirements = job_listing.get("requirements", "")
        hr_questions = job_listing.get("HR_questions", "")

        # If no responses yet, start with a general question about the job role
        if not interview_responses:
            return f"Tell us how your experience aligns with the role of {job_title}."

        # Combine all interview responses into a single string
        all_responses = " ".join(interview_responses)

        # Construct the prompt for the LLM
        prompt = (
            f"Based on the resume:\n{resume_text}\n\n"
            f"The job listing:\n"
            f"Title: {job_title}\n"
            f"Description: {job_description}\n"
            f"Requirements: {job_requirements}\n"
            f"HR Questions: {hr_questions}\n\n"
            f"And the interview responses so far:\n{all_responses}\n\n"
            f"Generate a single short and concise interview question. "
            f"The question should focus on the applicant's skills, experience, and alignment with the job requirements. (don't tell me what you did or say here's this or that. just print the question)"
            )
        # Prepare the payload for the LLM API request
        payload = {
            "model": "llama3-8b-8192",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 50,
            "temperature": 0.7,
        }

        # Make the API request to the LLM
        response = requests.post(self.llm_api_url, headers=self.llm_headers, json=payload)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content'].strip()
        else:
            raise Exception(f"API Error: {response.status_code}, {response.text}")

    def fetch_job_listing(self, job_key):
        """
        Fetch job listing details (title, description, requirements, and HR questions) from the Job_Listing table
        using the job key.

        Parameters:
            job_key (int): The job key (interview_id) used to fetch job listing details.

        Returns:
            dict: A dictionary containing job_title, description, requirements, and HR_questions.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT job_title, description, requirements, HR_questions
                FROM Job_Listing
                WHERE job_key = ?
            ''', (job_key,))
            job_listing = cursor.fetchone()
            if job_listing:
                return {
                    "job_title": job_listing[0],
                    "description": job_listing[1],
                    "requirements": job_listing[2],
                    "HR_questions": job_listing[3]
                }
            else:
                return None

    def summarize_interview(self, interview_responses):
        """
        Summarize the interview responses and provide feedback.

        Parameters:
            interview_responses (list): List of the applicant's interview responses.

        Returns:
            str: Summary and feedback of the interview.
        """
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

    def save_to_interview_table(self, applicant_name, applicant_phone, applicant_email, audio_transcript, interview_summary, ranking_score, interview_id):
 
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO Interview (applicant_name, applicant_phone, applicant_email, audio_transcript, interview_summary, ranking_score, interview_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (applicant_name, applicant_phone, applicant_email, audio_transcript, interview_summary, ranking_score, interview_id))
            conn.commit()