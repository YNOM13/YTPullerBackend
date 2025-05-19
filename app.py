from flask import Flask, request, jsonify, send_from_directory, url_for
import yt_dlp
import os

app = Flask(__name__)

DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/convert', methods=['POST'])
def convert_video():
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(id)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')
            basename = os.path.basename(filename)

            file_url = url_for('download_file', filename=basename, _external=True)

        return jsonify({'message': 'Conversion successful', 'mp3_url': file_url})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/downloads/<filename>')
def download_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

@app.route('/tracks', methods=['GET'])
def get_all_tracks():
    files = []
    for filename in os.listdir(DOWNLOAD_FOLDER):
        if filename.endswith('.mp3'):
            files.append({
                "filename": filename,
                "url": url_for('download_file', filename=filename, _external=True)
            })
    return jsonify(files)

if __name__ == '__main__':
    app.run(debug=True)
