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
    regex = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:watch\?v=|embed\/|v\/|shorts\/|)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(regex, url)
    if match:
        return match.group(1)
    return None

def get_best_transcript(video_id):
    """
    Smart function jo pehle English/Hindi dhundta hai,
    Agar wo na mile to JO BHI transcript available ho use le leta hai.
    """
    try:
        # Step 1: Available transcripts ki list nikalo
        transcript_list_obj = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Step 2: Try to find English or Hindi
        try:
            transcript = transcript_list_obj.find_transcript(['en', 'hi'])
        except:
            # Step 3: Fallback - Agar En/Hi nahi mila, to jo pehla available hai wo utha lo
            # (Chahe wo Spanish ho, German ho, ya Auto-generated English variant ho)
            transcript = next(iter(transcript_list_obj))
            
        # Step 4: Text fetch karke return karo
        return transcript.fetch()
        
    except Exception as e:
        # Agar transcript poori tarah disabled hai
        print(f"Transcript Error: {e}")
        return None

# --- Route 1: Website ka Home Page ---
@app.route('/', methods=['GET', 'POST'])
def index():
    transcript_text = None
    error_message = None

    if request.method == 'POST':
        video_url = request.form.get('url')
        if video_url:
            video_id = extract_video_id(video_url)
            if video_id:
                # Naya smart function use kar rahe hain
                transcript_data = get_best_transcript(video_id)
                
                if transcript_data:
                    formatter = TextFormatter()
                    transcript_text = formatter.format_transcript(transcript_data)
                else:
                    error_message = "Error: Is video mein koi bhi transcript/caption available nahi hai."
            else:
                error_message = "Invalid YouTube URL."
        else:
            error_message = "Please enter a URL."

    return render_template('index.html', transcript=transcript_text, error=error_message)

# --- Route 2: API Request Handle karne ke liye ---
@app.route('/api/transcript', methods=['GET'])
def api_transcript():
    video_url = request.args.get('url')
    
    if not video_url:
        return jsonify({'error': 'URL is required'}), 400

    video_id = extract_video_id(video_url)
    if not video_id:
        return jsonify({'error': 'Invalid YouTube URL'}), 400

    # Naya smart function use kar rahe hain
    transcript_data = get_best_transcript(video_id)

    if transcript_data:
        formatter = TextFormatter()
        transcript_text = formatter.format_transcript(transcript_data)
        return jsonify({'transcript': transcript_text})
    else:
        return jsonify({'error': 'Transcript not available for this video.'}), 404

if __name__ == '__main__':
    app.run(debug=True)
