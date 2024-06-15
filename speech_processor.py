import subprocess
import speech_recognition as sr
import pyttsx3

class SpeechProcessor:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        
        self.use_espeak = True
        try:
            subprocess.call(['which', 'espeak'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except FileNotFoundError:
            self.use_espeak = False

        if not self.use_espeak:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)  
            self.engine.setProperty('volume', 1.0)  

    def text_to_speech(self, text):
        if self.use_espeak:
            try:
                subprocess.call(['espeak', text])
            except Exception as e:
                print(f"Error using espeak: {e}")
                self.fallback_to_pyttsx3(text)
        else:
            self.fallback_to_pyttsx3(text)

    def fallback_to_pyttsx3(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def speech_to_text(self, prompt=None):
        while True:
            with sr.Microphone() as source:
                if prompt:
                    print(prompt)
                    self.text_to_speech(prompt)
                print("Listening...")
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source)
            try:
                print("Recognizing...")
                text = self.recognizer.recognize_google(audio)
                print("You said:", text)
                return text
            except sr.UnknownValueError:
                print("Sorry, I couldn't understand what you said. Please repeat.")
                self.text_to_speech("Sorry, I couldn't understand what you said. Please repeat.")
            except sr.RequestError as e:
                print(f"Sorry, I couldn't request results from Google Speech Recognition service; {e}")
                return None

