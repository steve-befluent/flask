from flask import Flask, request, jsonify
from pydub import AudioSegment
import requests
import os
import imageio_ffmpeg as ffmpeg

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.endswith('.caf'):
        # Save the uploaded .caf file
        caf_path = os.path.join('/tmp', file.filename)
        file.save(caf_path)

        # Set the path to the ffmpeg executable
        AudioSegment.converter = ffmpeg.get_ffmpeg_exe()

        # Convert .caf to .m4a
        audio = AudioSegment.from_file(caf_path, format='caf')
        m4a_path = caf_path.replace('.caf', '.m4a')
        audio.export(m4a_path, format='m4a')

        # Prepare the file for sending
        with open(m4a_path, 'rb') as f:
            files = {
                'blob': (os.path.basename(m4a_path), f, 'audio/m4a')
            }
            response = requests.post(
                'https://agbdejlfalbotcufcjia.supabase.co/functions/v1/speak',
                files=files
            )

        # Clean up temporary files
        os.remove(caf_path)
        os.remove(m4a_path)

        return jsonify({"status": "File sent", "response": response.json()}), response.status_code

    return jsonify({"error": "Invalid file type"}), 400

if __name__ == '__main__':
    app.run(debug=True)