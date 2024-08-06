import os
from flask import Flask, request, jsonify
from pydub import AudioSegment
import imageio_ffmpeg as ffmpeg
import requests

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/upload', methods=['POST'])
def upload_file():
    if not request.data:
        return jsonify({"error": "No file part"}), 400

    try:
        # Save the uploaded raw binary data as a .caf file
        caf_path = '/tmp/uploaded_audio.caf'
        with open(caf_path, 'wb') as f:
            f.write(request.data)

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

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)