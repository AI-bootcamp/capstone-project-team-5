### stt_methods.py
import sqlite3
import whisper
import requests
import wave
import sounddevice as sd

class STTProcessor:
    def __init__(self, db_path):
        self.model = whisper.load_model("tiny")
        self.db_path = db_path

    def record_audio(self, duration_minutes, output_path):
        duration_seconds = duration_minutes * 60  # Convert minutes to seconds
        fs = 44100  # Sample rate
        audio_data = sd.rec(int(duration_seconds * fs), samplerate=fs, channels=2, dtype='int16')
        sd.wait()  # Wait for the recording to finish

        with wave.open(output_path, 'wb') as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(fs)
            wf.writeframes(audio_data.tobytes())

    def transcribe_audio(self, audio_path):
        result = self.model.transcribe(audio_path)
        return result['text']

    def classify_sentence(self, sentence):
        API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
        headers = {"Authorization": f"Bearer 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"}
        payload = {"inputs": sentence}
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()

    def process_transcription(self, raw_transcription):
        sentences = raw_transcription.split(". ")
        current_speaker = "Speaker 1"
        labeled_transcription = []

        for sentence in sentences:
            if sentence.strip():
                self.classify_sentence(sentence)  # Simulate API call for demo purposes
                labeled_transcription.append(f"{current_speaker}: {sentence.strip()}")
                current_speaker = "Speaker 2" if current_speaker == "Speaker 1" else "Speaker 1"

        return "\n".join(labeled_transcription)

    def summarize_transcription(self, processed_transcription):
        API_URL = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer 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",
            "Content-Type": "application/json"
        }
        prompt = (
            f"The following is a transcription of a job interview. "
            f"Summarize the skills, expertise, and strengths of the interviewee based on the conversation:\n\n"
            f"{processed_transcription}\n\nSkills Summary:"
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
            raise Exception(f"API Error: {response.status_code}, {response.text}")

    def save_to_interview_table(self, raw_transcript, processed_transcript, summary):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO interview (raw_transcript, processed_transcript, summary)
                VALUES (?, ?, ?)
            ''', (raw_transcript, processed_transcript, summary))
            conn.commit()