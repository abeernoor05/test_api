from flask import Flask, request, jsonify, send_from_directory
import speech_recognition as sr
import requests
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'static/audios'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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

@app.route('/upload-audio', methods=['POST'])
def upload_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['audio']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    filename = secure_filename(file.filename)
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(save_path)

    host = request.host_url.rstrip('/')
    public_url = f"{host}/static/audios/{filename}"

    return jsonify({'url': public_url})

@app.route('/static/audios/<path:filename>')
def serve_audio(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
