import speech_recognition as sr
from gtts import gTTS
import os
import uuid

def recognize_speech(audio_data):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_data) as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Speech recognition could not understand audio"
    except sr.RequestError as e:
        return f"Could not request results from speech recognition service; {e}"

def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    filename = f"response_{uuid.uuid4()}.mp3"
    tts.save(filename)
    return filename

def cleanup_audio_files():
    for file in os.listdir():
        if file.startswith("response_") and file.endswith(".mp3"):
            if os.path.getmtime(file) < time.time() - 300:  # 5 minutes old
                os.remove(file)