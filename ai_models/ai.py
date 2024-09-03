import os
import openai
import google.generativeai as genai
import requests
from groq import Groq
from langdetect import detect

class AIAssistant:
    def __init__(self):
        # API keys setup
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.genai_api_key = os.getenv('GENAI_API_KEY')
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        self.google_api_key = os.getenv('GOOGLE_API_KEY')  # Google API key
        self.google_cse_id = os.getenv('GOOGLE_CSE_ID')  # Google Custom Search Engine ID

        if self.openai_api_key:
            openai.api_key = self.openai_api_key

        if self.genai_api_key:
            genai.configure(api_key=self.genai_api_key)

        if self.groq_api_key:
            self.groq_client = Groq(api_key=self.groq_api_key)

        # AI models
        self.models = {
            "gpt-3.5-turbo": self.use_openai,
            "gemini-pro": self.use_gemini,
            "llama3-70b-8192": self.use_groq
        }

        # Initial system prompt to define assistant's role
        self.system_prompt = {
            "role": "system",
            "content": "You are my personal AI assistant. Your way of talking and behavior is smart and efficient. You are extremely genius in every field. You reply with very short and meaningful answers in default Hinglish language. You can't change language until told to. You will answer in the same language in which you were asked the question and you can provide real-time information using the internet."
        }

        # Conversation history
        self.conversation_history = [self.system_prompt]
        self.max_history_length = 300  # Extended to handle 24-hour long conversations
        self.current_language = None

    def select_ai(self, query):
        if "creative" in query.lower():
            return "gpt-3.5-turbo" if self.openai_api_key else None
        elif "factual" in query.lower():
            return "gemini-pro" if self.genai_api_key else None
        elif any(keyword in query.lower() for keyword in ["weather", "news", "search", "real-time"]):
            return "google-realtime" if self.google_api_key else None
        else:
            return "llama3-70b-8192" if self.groq_api_key else None

    def use_openai(self, messages):
        if not self.openai_api_key:
            return "OpenAI API key is missing."
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        return response.choices[0].message.content

    def use_gemini(self, messages):
        if not self.genai_api_key:
            return "Gemini API key is missing."
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content([m['content'] for m in messages])
        return response.text

    def use_groq(self, messages):
        if not self.groq_api_key:
            return "Groq API key is missing."
        response = self.groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=messages
        )
        return response.choices[0].message.content

    def use_google_realtime(self, query):
        if not self.google_api_key:
            return "Google API key is missing."

        search_url = f"https://cse.google.com/cse?q={query}&key={self.google_api_key}&cx={self.google_cse_id}"
        response = requests.get(search_url).json()
        if 'items' in response:
            top_results = response['items'][:3]  # Get top 3 search results
            result_summary = "Search Results:\n" + "\n".join(
                [f"{i + 1}. {item['title']} - {item['link']}" for i, item in enumerate(top_results)])
            return result_summary
        else:
            return "No results found."

    def process_query(self, query):
        # Detect language of the query
        self.current_language = detect(query)

        # Add user query to conversation history
        self.conversation_history.append({"role": "user", "content": query})

        # Limit conversation history
        if len(self.conversation_history) > self.max_history_length:
            self.conversation_history = [self.conversation_history[0]] + self.conversation_history[
                                                                         -(self.max_history_length - 1):]

        selected_ai = self.select_ai(query)
        if not selected_ai:
            return "No suitable AI model found due to missing API keys."

        if selected_ai == "google-realtime":
            response = self.use_google_realtime(query)
        else:
            response = self.models[selected_ai](self.conversation_history)

        # Verify response language
        response_lang = detect(response)
        if response_lang != self.current_language:
            # If language doesn't match, request again with explicit instruction
            self.conversation_history.append({"role": "system",
                                              "content": f"Your last response was not in {self.current_language}. Please respond in {self.current_language}."})
            response = self.models[selected_ai](self.conversation_history)

        # Add AI response to conversation history
        self.conversation_history.append({"role": "assistant", "content": response})

        return response

    def get_info(self):
        return {
            "description": "A versatile AI assistant capable of handling various tasks and communicating in multiple languages.",
            "capabilities": [
                "Natural language processing",
                "Multi-language support",
                "Context-aware responses",
                "Integration with multiple AI models (OpenAI, Gemini, Groq)",
                "Real-time information retrieval (Weather, News, Search)"
            ],
            "input_format": "Text",
            "output_format": "Text"
        }

# This function will be called by the main program
def create_assistant():
    return AIAssistant()
