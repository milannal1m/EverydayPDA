import subprocess
from gtts import gTTS
import os
import tempfile
import speech_recognition as gSTT

# Basisverzeichnis für Audio-Dateien
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def generate_voice_message(text: str) -> str:
    """
    Wandelt den gegebenen Text in eine OGG-Datei um und gibt den Dateipfad zurück.
    """
    if not text.strip():
        raise ValueError("Text darf nicht leer sein.")

    # Temporäre MP3-Datei erstellen
    temp_mp3 = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    temp_mp3.close()

    # Text in Sprache umwandeln
    tts = gTTS(text=text, lang="de")
    tts.save(temp_mp3.name)

    # OGG-Datei speichern mit subprocess und ffmpeg, und ohne Bestätigung durch -y
    ogg_path = os.path.join(BASE_DIR, "output.ogg")
    subprocess.run(['ffmpeg', '-y', '-i', temp_mp3.name, '-acodec', 'libvorbis', '-ar', '24000', '-ab', '64k', ogg_path])

    # Temporäre Datei löschen
    os.unlink(temp_mp3.name)

    return ogg_path

def convert_voice_to_text(file_path: str) -> str:
    """
    Konvertiert eine übergebene OGG-Datei in Text und gibt diesen zurück.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Die Datei {file_path} existiert nicht.")

    # OGG-Datei mit subprocess und ffmpeg in WAV umwandeln, Overhead vermeiden
    temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    temp_wav.close()
    
    subprocess.run(['ffmpeg', '-y', '-i', file_path, '-ac', '1', '-ar', '16000', '-vn', temp_wav.name])

    # WAV-Datei mit speech_recognition verarbeiten
    recognizer = gSTT.Recognizer()
    with open(temp_wav.name, "rb") as wav_file:
        audio_data = gSTT.AudioData(wav_file.read(), 16000, 2)
    
    # Temporäre WAV-Datei löschen
    os.unlink(temp_wav.name)

    # Sprache erkennen
    try:
        text = recognizer.recognize_google(audio_data, language="de-DE")
        return text
    except gSTT.UnknownValueError:
        return "Ich konnte die Sprache nicht verstehen."
    except gSTT.RequestError:
        return "Fehler: Ich kann die Spracherkennung gerade nicht erreichen."
