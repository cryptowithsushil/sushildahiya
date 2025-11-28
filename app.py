from flask import Flask, request, jsonify, render_template
from youtube_transcript_api import YouTubeTranscriptApi
import traceback
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/transcript', methods=['GET'])
def get_transcript_api():
    try:
        url = request.args.get('url')
        if not url:
            return jsonify({"error": "URL nahi mila"}), 400

        # Video ID nikalna
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

        # --- ✅ COOKIE CHECK ---
        cookie_file = "cookies.txt"
        
        # Check karein ki file server par exist karti hai ya nahi
        if os.path.exists(cookie_file):
            print(f"✅ Success: '{cookie_file}' server par mil gayi!")
            cookies_path = cookie_file
        else:
            print(f"❌ Error: '{cookie_file}' server par nahi mili!")
            cookies_path = None
            return jsonify({"error": "Server Error: cookies.txt file gayab hai!"}), 500

        # --- TRANSCRIPT FETCHING ---
        try:
            # Hum seedha get_transcript use karenge (Backup wala hataya taaki asli error dikhe)
            transcript_list = YouTubeTranscriptApi.get_transcript(
                video_id, 
                languages=['hi', 'en', 'en-IN'], 
                cookies=cookies_path
            )
            
            # Text join karna
            full_text = " ".join([item['text'] for item in transcript_list])
            return jsonify({"transcript": full_text})

        except Exception as yt_error:
            # Yahan hume asli error pata chalega
            print(f"YouTube API Error: {str(yt_error)}")
            return jsonify({"error": f"YouTube ne roka: {str(yt_error)}"}), 500

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error": f"System Error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
