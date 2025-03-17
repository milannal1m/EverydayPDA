from gtts import gTTS
import speech_recognition as gSTT
from  pydub import AudioSegment
import os

def texToSpeech(text):
    tts = gTTS(text=text, lang="de") 
    tts.save("./frontend/output.mp3")

def speechToText(path):
    recognizer = gSTT.Recognizer()

    with gSTT.AudioFile(path) as source:
        audio = recognizer.record(source)

    text = recognizer.recognize_google(audio, language="de-DE")
    print(text)

def convertToWav(path):
    audio = AudioSegment.from_mp3(path)
    audio.export("./frontend/output.wav", format="wav")

if __name__ == "__main__":
    texToSpeech("Hallo Test. Aktien, Wetter und Nachrichten für dich.")
    convertToWav("./frontend/output.mp3")
    speechToText("./frontend/output.wav")