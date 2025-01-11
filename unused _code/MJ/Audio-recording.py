import os
import sys
import datetime
import streamlit as st

from audio_recorder_streamlit import audio_recorder




def save_audio_file(audio_bytes, file_extension):
    """
    Save audio bytes to a file with the specified extension.

    :param audio_bytes: Audio data in bytes
    :param file_extension: The extension of the output audio file
    :return: The name of the saved audio file
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"audio_{timestamp}.{file_extension}"

    with open(file_name, "wb") as f:
        f.write(audio_bytes)

    return file_name




def main():
    st.title("Interview")


    audio_bytes = audio_recorder()
    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")
        save_audio_file(audio_bytes, "mp3")


    # Transcribe button action
    if st.button("Transcribe"):
       '''
       here wispher
       
       
       '''

if __name__ == "__main__":
    # Set up the working directory
    working_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(working_dir)

    # Run the main function
    main()
