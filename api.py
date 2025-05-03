from flask import Flask, request, jsonify, send_from_directory
import speech_recognition as sr
import requests

import os
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'static/audios'
INDEX_FILE = 'audio_index.json'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load existing audio index or start fresh
if os.path.exists(INDEX_FILE):
    with open(INDEX_FILE, 'r') as f:
        audio_index = json.load(f)
else:
    audio_index = []

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

    entry = {"id": filename, "url": public_url}
    audio_index.append(entry)
    with open(INDEX_FILE, 'w') as f:
        json.dump(audio_index, f)

    return jsonify({'url': public_url})

@app.route('/list-audios', methods=['GET'])
def list_audios():
    return jsonify(audio_index)



@app.route('/speech-to-text-url', methods=['POST'])
def transcribe_audio_url():
    try:
        data = request.get_json()
        audio_url = data.get("url")

        if not audio_url:
            return jsonify({"error": "Missing URL"}), 400

        r = sr.Recognizer()
        response = requests.get(audio_url)

        # Save as .3gp
        with open("temp.3gp", "wb") as f:
            f.write(response.content)

        # Use ffmpeg to convert 3gp to wav
        os.system("ffmpeg -y -i temp.3gp temp.wav")

        with sr.AudioFile("temp.wav") as source:
            audio_data = r.record(source)

        text = r.recognize_google(audio_data)
        return jsonify({"text": text})

    except sr.UnknownValueError:
        return jsonify({"text": "Could not understand audio"}), 200
    except Exception as e:
        return jsonify({"text": f"Error: {str(e)}"}), 500




@app.route('/static/audios/<path:filename>')
def serve_audio(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
