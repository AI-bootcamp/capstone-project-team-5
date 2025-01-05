### stt_app.py
import streamlit as st
from tempfile import NamedTemporaryFile
from stt_methods import STTProcessor

def main():
    st.title("Real-Time Speech-to-Text Transcription App")

    db_path = "recruitment_platform.db"
    processor = STTProcessor(db_path=db_path)
    duration_minutes = st.number_input("Recording Duration (minutes):", min_value=1, max_value=60, value=1)

    if st.button("Start Recording"):
        with NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            processor.record_audio(duration_minutes, temp_audio.name)
            temp_audio_path = temp_audio.name

        try:
            # Step 1: Transcribe audio
            raw_transcription = processor.transcribe_audio(temp_audio_path)
            st.text_area("Raw Transcription", raw_transcription, height=200)

            # Step 2: Process transcription
            processed_transcription = processor.process_transcription(raw_transcription)
            st.text_area("Processed Transcription", processed_transcription, height=200)

            # Step 3: Summarize transcription
            summary = processor.summarize_transcription(processed_transcription)
            st.text_area("Summary", summary, height=200)

            # Step 4: Save to interview table
            processor.save_to_interview_table(raw_transcription, processed_transcription, summary)
            st.success("Transcription, processing, and summary saved to interview table.")
        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()