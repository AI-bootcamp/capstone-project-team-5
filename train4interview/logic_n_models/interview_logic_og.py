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
        try:
            with pdfplumber.open(file_path) as pdf:
                text = ''.join(page.extract_text() + '\n' for page in pdf.pages)
            return text.strip()
        except Exception as e:
            raise Exception(f"Error reading PDF file: {e}")

    def classify_cv_data_with_llm(self, cv_text):
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

    def interviewer(self, classified_data, interview_responses):
        if not interview_responses:
            return "Talk about yourself."
        else:
            all_responses = " ".join(interview_responses)
            prompt = (
                f"Based on the resume:\n{classified_data}\n\n"
                f"And the interview responses so far:\n{all_responses}\n\n"
                f"Generate a single short and concise interview question. "
                f"The question should be one sentence and focus on the applicant's skills or experience. (don't tell me what you did or say here's this or that. just print the question)"
            )
            payload = {
                "model": "llama3-8b-8192",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 50,
                "temperature": 0.7,
            }
            response = requests.post(self.llm_api_url, headers=self.llm_headers, json=payload)
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content'].strip()
            else:
                raise Exception(f"API Error: {response.status_code}, {response.text}")

    def summarize_interview(self, interview_responses):
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

    def save_to_interview_table(self, raw_transcript, summary):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO interview (raw_transcript, summary)
                VALUES (?, ?)
            ''', (raw_transcript, summary))
            conn.commit()