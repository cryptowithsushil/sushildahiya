from flask import Flask, request, jsonify, render_template
from youtube_transcript_api import YouTubeTranscriptApi
import traceback

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html')

@app.route('/api/transcript', methods=['GET'])
def get_transcript_api():
    try:
        url = request.args.get('url')
        if not url:
            return jsonify({"error": "URL nahi mila (Missing)"}), 400

        # --- Video ID nikalne ka Logic ---
        video_id = None
        if "youtu.be" in url:
            video_id = url.split("youtu.be/")[1].split("?")[0]
        elif "v=" in url:
            video_id = url.split("v=")[1].split("&")[0]
        elif "/shorts/" in url:
            video_id = url.split("/shorts/")[1].split("?")[0]
        else:
            video_id = url

        if not video_id:
            return jsonify({"error": "Video ID detect nahi hui."}), 400

        # --- Transcript Fetching ---
        yt_api = YouTubeTranscriptApi()
        
        # Multiple Languages Check
        languages_list = ['hi', 'en-IN', 'en']
        transcript_list = yt_api.fetch(video_id, languages=languages_list)

        # --- ? FIX: Yahan 'item['text']' ki jagah 'item.text' kar diya ---
        # Kyunki aapka version objects return kar raha hai, dictionary nahi.
        full_text = " ".join([item.text for item in transcript_list])

        return jsonify({"transcript": full_text})

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error": f"System Error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)