import speech_recognition as sr
import speech_recognition as sr ##include speech recognition library
import tempfile  # for temporary file handling

def transcribe(audio):
 
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
        temp_audio_file.write(audio.getvalue())
        temp_audio_file_path = temp_audio_file.name
 
    #print("Audio: "+str(input_audio))
    r = sr.Recognizer()
    with sr.AudioFile(temp_audio_file_path) as source:
        audio = r.record(source)
    try:
        s = r.recognize_google(audio, language= 'es-US')
        print("Text: "+s)
    except Exception as e:
         print("Exception: "+str(e))
    return s