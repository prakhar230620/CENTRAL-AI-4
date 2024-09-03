from groq import Groq
import speech_recognition as sr
import pyttsx3

# Set the API key directly
api_key = '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'

# Initialize the Groq client with the API key
client = Groq(api_key=api_key)

# Initialize speech recognition
recognizer = sr.Recognizer()

# Initialize text-to-speech
engine = pyttsx3.init()

# Get the available voices
voices = engine.getProperty('voices')

# Set the voice to female (usually the second voice in the list)
engine.setProperty('voice', voices[1].id)

# Set the system prompt
system_prompt = {
    "role": "system",
    "content": "you are my personal AI assistant, your name is Jarvis. you are extremely genius in every field. you reply with very short and meaningful answers"
}

# Initialize the chat history
chat_history = [system_prompt]

def speak(text):
    print("Assistant:", text)
    engine.say(text)
    engine.runAndWait()

def listen():
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        print("Processing...")
        text = recognizer.recognize_google(audio, language="hi-IN")
        print("You said:", text)
        return text
    except sr.UnknownValueError:
        print("Sorry, I didn't catch that.")
        return ""
    except sr.RequestError:
        print("Sorry, there was an error with the speech recognition service.")
        return ""

while True:
    # Get user input from voice
    user_input = listen()
    if user_input:
        # Append the user input to the chat history
        chat_history.append({"role": "user", "content": user_input})

        # Create the chat completion response
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=chat_history,
            max_tokens=100,
            temperature=1.2
        )

        # Get the assistant's response
        assistant_response = response.choices[0].message.content

        # Append the response to the chat history
        chat_history.append({
            "role": "assistant",
            "content": assistant_response
        })

        # Speak the response
        speak(assistant_response)