from flask import Flask, render_template, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import re

app = Flask(__name__)

def extract_video_id(url):
    """
    YouTube URL se Video ID nikalne ka robust function.
    Ab ye Shorts aur alag-alag formats ko behtar handle karega.
    """
    # Updated Regex: Ye Shorts, Watch, Embed, aur youtu.be sabko cover karega
    regex = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:watch\?v=|embed\/|v\/|shorts\/|)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    
    match = re.search(regex, url)
    if match:
        return match.group(1)
    return None

# --- Route 1: Website ka Home Page dikhane ke liye ---
@app.route('/', methods=['GET', 'POST'])
def index():
    transcript_text = None
    error_message = None

    # Agar normal form submit ho raha hai (Backup ke liye)
    if request.method == 'POST':
        video_url = request.form.get('url')
        if video_url:
            video_id = extract_video_id(video_url)
            if video_id:
                try:
                    transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'hi'])
                    formatter = TextFormatter()
                    transcript_text = formatter.format_transcript(transcript_list)
                except Exception as e:
                    error_message = "Error: Subtitles not found or video is restricted."
            else:
                error_message = "Invalid YouTube URL."
        else:
            error_message = "Please enter a URL."

    return render_template('index.html', transcript=transcript_text, error=error_message)

# --- Route 2: API Request Handle karne ke liye ---
@app.route('/api/transcript', methods=['GET'])
def api_transcript():
    video_url = request.args.get('url') # URL query parameter se lena
    
    if not video_url:
        return jsonify({'error': 'URL is required'}), 400

    video_id = extract_video_id(video_url)
    if not video_id:
        return jsonify({'error': 'Invalid YouTube URL'}), 400

    try:
        # Transcript fetch karna
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'hi'])
        
        # Text convert karna
        formatter = TextFormatter()
        transcript_text = formatter.format_transcript(transcript_list)
        
        # JSON response bhejna (Frontend ke liye)
        return jsonify({'transcript': transcript_text})

    except Exception as e:
        return jsonify({'error': 'Transcript not available for this video.'}), 404

if __name__ == '__main__':
    app.run(debug=True)
