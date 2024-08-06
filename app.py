import os
import logging
from flask import Flask, request, jsonify
from pydub import AudioSegment
import imageio_ffmpeg as ffmpeg
import requests

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/upload', methods=['POST'])
def upload_file():
    if not request.data:
        app.logger.error("No file part in the request")
        return jsonify({"error": "No file part"}), 400

    try:
        # Save the uploaded raw binary data as a .caf file
        caf_path = '/tmp/uploaded_audio.caf'
        with open(caf_path, 'wb') as f:
            f.write(request.data)

        # Set the path to the ffmpeg executable
        AudioSegment.converter = ffmpeg.get_ffmpeg_exe()

        # Convert .caf to .target
        format = 'mp3'
        audio = AudioSegment.from_file(caf_path, format='caf')
        target_path = caf_path.replace('.caf', '.' + format)
        audio.export(target_path, format=format)

        # Prepare the file for sending
        with open(target_path, 'rb') as f:
            files = {
                'blob': (os.path.basename(target_path), f, 'audio/' + format)
            }
            response = requests.post(
                'https://agbdejlfalbotcufcjia.supabase.co/functions/v1/speak',
                files=files
            )

        # Clean up temporary files
        os.remove(caf_path)
        os.remove(target_path)

        return jsonify({"status": "File sent", "response": response.json()}), response.status_code

    except Exception as e:
        app.logger.error(f"Exception occurred: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)