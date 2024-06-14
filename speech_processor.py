import subprocess
import speech_recognition as sr

class SpeechProcessor:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def text_to_speech(self, text):
        subprocess.call(['espeak', text])

    def speech_to_text(self, prompt=None):
        while True:
            with sr.Microphone() as source:
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
                self.text_to_speech("Repeat what you said.")
            except sr.RequestError as e:
                print("Sorry, I couldn't request results from Google Speech Recognition service; {0}".format(e))
                return None


