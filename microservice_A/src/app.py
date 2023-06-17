import os
from flask import Flask, request, jsonify

from helper import *

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def create_upload_folder():
    path = Path(
        Path(__file__).resolve().parents[1], UPLOAD_FOLDER
    ).as_posix()
    if not path:
        os.makedirs(app.config['UPLOAD_FOLDER'])


@app.route(f"{API_PREFIX}/upload-audio", methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part in the request'

    file = request.files['file']
    if file.filename == '':
        return 'No selected file'

    create_upload_folder()

    if file:
        filename = "assignment_audio.wav"
        file_path = Path(Path(__file__).resolve().parents[1], f"{UPLOAD_FOLDER}/{filename}").as_posix()
        file.save(file_path)

        # Convert the audio file to 16-bit PCM format
        audio = AudioSegment.from_file(file_path, format="wav")

        # Validate the audio file
        is_valid, error_message = validate_audio(audio)
        if not is_valid:
            return {'message': error_message}

        response = {'message': 'Request received. Splitting your file in the background.'}
        threading.Thread(target=process_audio).start()
        return jsonify(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
