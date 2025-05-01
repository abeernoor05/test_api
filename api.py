from flask import Flask, request, jsonify
import speech_recognition as sr
import requests

app = Flask(__name__)

@app.route('/speech-to-text-url', methods=['POST'])
def transcribe_audio_url():
    data = request.get_json()
    audio_url = data.get("url")

    r = sr.Recognizer()
    response = requests.get(audio_url)
    with open("temp.wav", "wb") as f:
        f.write(response.content)

    with sr.AudioFile("temp.wav") as source:
        audio = r.record(source)
        try:
            text = r.recognize_google(audio)
            return jsonify({"text": text})
        except:
            return jsonify({"text": "Could not transcribe"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
