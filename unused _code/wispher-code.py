from groq import Groq
import os
import pandas as pd
import numpy as np
from pydub import AudioSegment



client = Groq(api_key="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")
model = 'whisper-large-v3'

filepath = "final\audio_20250107_064158.mp3"
def audio_to_text(filepath):
    with open(filepath, "rb") as file:
        translation = client.audio.translations.create(
            file=(filepath, file.read()),
            model="whisper-large-v3",
        )
    return translation.text
    
translation_text = audio_to_text(filepath)

# Show just the beginning of the transcription
print(translation_text[:2000])
