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

        # --- 1. Video ID Nikalna ---
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

        # --- 2. Cookies Check ---
        cookie_file = "cookies.txt"
        cookies_path = cookie_file if os.path.exists(cookie_file) else None
        
        if not cookies_path:
            print("⚠ Warning: cookies.txt nahi mili! Server check karein.")

        # --- 3. Transcript Fetching (Modern Way) ---
        try:
            # Step A: Saare Transcripts ki list nikalo (Cookies ke sath)
            transcript_list_obj = YouTubeTranscriptApi.list_transcripts(video_id, cookies=cookies_path)

            # Step B: Hamein Hindi chahiye, agar wo na mile to English
            # Hum priority set kar rahe hain: Hindi > English India > English Global
            transcript = transcript_list_obj.find_transcript(['hi', 'en-IN', 'en'])

            # Step C: Ab data fetch karo
            final_data = transcript.fetch()

            # Step D: Text join karo
            # (Render par ye Dictionary return karega, isliye item['text'] use kiya)
            full_text = " ".join([item['text'] for item in final_data])

            return jsonify({"transcript": full_text})

        except Exception as yt_error:
            # Agar koi bhi dikkat aayi (jaise video me transcript hi na ho)
            print(f"YouTube API Error: {str(yt_error)}")
            return jsonify({"error": f"YouTube Error: {str(yt_error)}"}), 500

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error": f"System Error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
