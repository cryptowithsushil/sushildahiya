# app.py - पूरी फाइल (Python 3.10 के लिए बिल्कुल सही)

from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
import re

app = Flask(__name__)

# यूट्यूब video_id निकालने के लिए
def extract_video_id(url):
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

# सबसे अच्छा ट्रांसक्रिप्ट लाने का फंक्शन (Python 3.10 friendly)
def get_best_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # 1. पहले मैन्युअल हिंदी या इंग्लिश ट्रांसक्रिप्ट
        try:
            transcript = transcript_list.find_manually_created_transcript(['hi', 'en'])
            lang = transcript.language
            code = transcript.language_code
            print("Manual transcript मिला:", lang, f"({code})")
            return transcript.fetch(), f"{lang} ({code}) - Manual"
        except:
            pass

        # 2. ऑटो-जेनरेटेड हिंदी
        try:
            transcript = transcript_list.find_generated_transcript(['hi'])
            print("Auto-generated हिंदी ट्रांसक्रिप्ट मिला")
            return transcript.fetch(), "Hindi - Auto-generated"
        except:
            pass

        # 3. ऑटो-जेनरेटेड इंग्लिश
        try:
            transcript = transcript_list.find_generated_transcript(['en'])
            print("Auto-generated इंग्लिश ट्रांसक्रिप्ट मिला")
            return transcript.fetch(), "English - Auto-generated"
        except:
            pass

        # 4. जो भी मिल जाए (फॉलबैक)
        transcript = next(iter(transcript_list))
        typ = "Auto-generated" if transcript.is_generated else "Manual"
        print(f"फॉलबैक: {transcript.language} - {typ}")
        return transcript.fetch(), f"{transcript.language} - {typ}"

    except Exception as e:
        print("कोई ट्रांसक्रिप्ट नहीं मिला:", str(e))
        return None, str(e)

# होम पेज
@app.route('/')
def home():
    return '''
    <h1>YouTube Transcript API (हिंदी + English)</h1>
    <p>उदाहरण: <code>/transcript?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ</code></p>
    <p>या शॉर्ट लिंक भी चलेगा: <code>https://youtu.be/dQw4w9WgXcQ</code></p>
    '''

# मुख्य API रूट
@app.route('/transcript')
def transcript():
    url = request.args.get('url')
    
    if not url:
        return jsonify({"error": "url पैरामीटर जरूरी है!"}), 400

    video_id = extract_video_id(url)
    if not video_id:
        return jsonify({"error": "वैलिड यूट्यूब लिंक नहीं है"}), 400

    transcript_data, info = get_best_transcript(video_id)

    if transcript_data is None:
        return jsonify({
            "video_id": video_id,
            "error": info,
            "message": "इस वीडियो में कोई सबटाइटल/ट्रांसक्रिप्ट उपलब्ध नहीं है"
        }), 404

    # पूरा टेक्स्ट बनाओ
    full_text = " ".join([item['text'] for item in transcript_data])

    return jsonify({
        "video_id": video_id,
        "language": info,
        "total_segments": len(transcript_data),
        "full_text": full_text,
        "transcript": transcript_data
    })

# चलाओ
if __name__ == '__main__':
    app.run(debug=True)

