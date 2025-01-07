import streamlit as st
from interview_logic import CVProcessor, AudioProcessor, InterviewManager
from streamlit_webrtc import webrtc_streamer

# Configurations
DB_PATH = "interview_data.db"
LLM_API_URL = "https://api.groq.com/openai/v1/chat/completions"
LLM_API_KEY = "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"
AUDIO_FILE = "interview_audio.wav"

# Initialize processors
cv_processor = CVProcessor(DB_PATH, LLM_API_URL, LLM_API_KEY)
audio_processor = AudioProcessor()
interview_manager = InterviewManager(DB_PATH, LLM_API_URL, LLM_API_KEY)

# Initialize session state variables
if "step" not in st.session_state:
    st.session_state.step = "upload"
if "classified_data" not in st.session_state:
    st.session_state.classified_data = None
if "interview_responses" not in st.session_state:
    st.session_state.interview_responses = []
if "current_question" not in st.session_state:
    st.session_state.current_question = None

st.title("AI-Powered CV Classifier and Interview Platform")

# Step 1: Upload and Classify Resume
if st.session_state.step == "upload":
    st.header("Upload Resume")
    uploaded_file = st.file_uploader("Upload your resume (PDF format)", type=["pdf"])

    if uploaded_file:
        with open("uploaded_resume.pdf", "wb") as f:
            f.write(uploaded_file.getbuffer())
        try:
            cv_text = cv_processor.process_cv_from_pdf("uploaded_resume.pdf")
            classified_data = cv_processor.classify_cv_data_with_llm(cv_text)
            cv_processor.save_to_cv_table(cv_text, classified_data)
            st.session_state.classified_data = classified_data
            st.success("Resume successfully classified!")
            st.write("Classified Resume Data:")
            st.write(classified_data)

            if st.button("Start Interview"):
                st.session_state.step = "interview"
        except Exception as e:
            st.error(f"Error processing resume: {e}")

# Step 2: Conduct Interview
if st.session_state.step == "interview":
    st.header("Conduct Interview")
    classified_data = st.session_state.classified_data

    col1, col2 = st.columns([4, 1])

    with col1:
        webrtc_streamer(
            key="webcam",
            media_stream_constraints={"video": True, "audio": False},
        )

    with col2:
        st.session_state.current_question = interview_manager.interviewer(
            classified_data, st.session_state.interview_responses
        )

        st.subheader("Interview Question")
        st.write(st.session_state.current_question)

        if st.button("Record Response"):
            st.info("Recording... Please wait.")
            try:
                audio_processor.record_audio(duration_minutes=1, output_path=AUDIO_FILE)
                response_text = audio_processor.transcribe_audio(AUDIO_FILE)
                st.success(f"Recorded response: {response_text}")
                st.session_state.interview_responses.append(response_text)
            except Exception as e:
                st.error(f"Error recording or processing response: {e}")

        if st.button("End Interview"):
            st.session_state.step = "summary"

# Step 3: Summarize Interview
if st.session_state.step == "summary":
    st.header("Analyze Interview")

    try:
        summary = interview_manager.summarize_interview(st.session_state.interview_responses)
        st.success("Interview Summary and Analysis:")
        st.write(summary)

        raw_transcription = " ".join(st.session_state.interview_responses)
        interview_manager.save_to_interview_table(
            raw_transcript=raw_transcription, summary=summary
        )
        st.info("Interview data saved to the database!")
    except Exception as e:
        st.error(str(e))
