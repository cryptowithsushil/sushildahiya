from flask import Flask, request, jsonify, render_template
from youtube_transcript_api import YouTubeTranscriptApi
import traceback
import os

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

        # --- ? COOKIES SETUP (Render ke liye) ---
        cookie_file = "cookies.txt"
        
        # Check karein ki cookies.txt server par hai ya nahi
        cookies_path = cookie_file if os.path.exists(cookie_file) else None
        
        # Agar cookies file nahi mili to warning print karega (Console me)
        if not cookies_path:
            print("? Warning: cookies.txt nahi mili! YouTube block kar sakta hai.")

        # --- Transcript Fetching ---
        try:
            # Standard function use kar rahe hain jo cookies support karta hai
            transcript_list = YouTubeTranscriptApi.get_transcript(
                video_id, 
                languages=['hi', 'en-IN', 'en'], 
                cookies=cookies_path
            )
        except Exception:
            # Agar direct fetch fail ho, to list_transcripts try karein
            transcript_list = YouTubeTranscriptApi.list_transcripts(
                video_id, 
                cookies=cookies_path
            ).find_transcript(['hi', 'en-IN', 'en']).fetch()

        # --- Text Extract Karna ---
        # Note: Render par latest library install hogi, jo Dictionary return karti hai.
        # Isliye hum item['text'] use kar rahe hain.
        full_text = " ".join([item['text'] for item in transcript_list])

        return jsonify({"transcript": full_text})

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error": f"Error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)