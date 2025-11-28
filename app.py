from flask import Flask, request, render_template_string
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import re

# FIX: Double underscore correct kiya hai (_name_)
app = Flask(__name__)

# Aapki di hui API Key ko yahan Secure Key bana diya hai
app.secret_key = "6929ca86c8b7375deae07c5c"

# HTML Template
HTML = '''
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YouTube to Transcript (हिंदी + English)</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #667eea, #764ba2); color: white; text-align: center; padding: 50px; }
        h1 { font-size: 3rem; margin-bottom: 10px; }
        p { font-size: 1.3rem; }
        input { padding: 15px; width: 70%; max-width: 600px; font-size: 1.1rem; border-radius: 10px; border: none; margin: 20px 0; }
        button { padding: 15px 40px; font-size: 1.2rem; background: #ff4757; color: white; border: none; border-radius: 10px; cursor: pointer; }
        button:hover { background: #ff3742; }
        .result { margin-top: 40px; background: rgba(0,0,0,0.3); padding: 30px; border-radius: 15px; text-align: left; display: inline-block; width: 80%; max-width: 800px; }
        textarea { width: 100%; height: 400px; background: #222; color: #0f0; padding: 20px; border-radius: 10px; font-size: 1.1rem; margin-top: 20px; }
        .footer { margin-top: 50px; font-size: 0.9rem; opacity: 0.8; }
    </style>
</head>
<body>
    <h1>YouTube to Transcript</h1>
    <p>कोई भी यूट्यूब वीडियो का लिंक डालो – हिंदी, इंग्लिश या कोई भी भाषा में ट्रांसक्रिप्ट मिलेगा</p>
     
    <form method="POST">
        <input type="text" name="url" placeholder="https://youtu.be/..." required>
        <br>
        <button type="submit">ट्रांसक्रिप्ट निकालो</button>
    </form>

    {% if transcript %}
    <div class="result">
        <h2>ट्रांसक्रिप्ट मिल गया!</h2>
        <p><strong>भाषा:</strong> {{ language }}</p>
        <p><strong>वीडियो ID:</strong> {{ video_id }}</p>
        <textarea readonly>{{ transcript }}</textarea>
        <p>Copy कर लो ↑</p>
    </div>
    {% endif %}

    {% if error %}
    <div class="result" style="background: rgba(255,0,0,0.3);">
        <h2>{{ error }}</h2>
    </div>
    {% endif %}

    <div class="footer">
        Made with ❤ by Sushil Dahiya | Free Forever
    </div>
</body>
</html>
'''

def extract_video_id(url):
    if not url or not isinstance(url, str):
        return None
    # Improved Regex for better matching
    regex = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:watch\?v=|embed\/|v\/|shorts\/|)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(regex, url)
    return match.group(1) if match else None

def get_transcript(video_id):
    try:
        # Koshish 1: Naya Tarika (Advanced - list_transcripts)
        # Ye tabhi chalega agar library updated hai
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

            # Priority: Manual Hindi -> Manual English
            for lang in ['hi', 'en']:
                try:
                    t = transcript_list.find_manually_created_transcript([lang])
                    texts = [item['text'] for item in t.fetch()]
                    return " ".join(texts).replace("  ", "\n"), f"{t.language} (Manual)"
                except: pass

            # Priority: Auto Hindi -> Auto English
            for lang in ['hi', 'en']:
                try:
                    t = transcript_list.find_generated_transcript([lang])
                    texts = [item['text'] for item in t.fetch()]
                    return " ".join(texts).replace("  ", "\n"), f"{t.language} (Auto)"
                except: pass

            # Fallback: First available
            t = next(iter(transcript_list))
            texts = [item['text'] for item in t.fetch()]
            typ = "Auto" if t.is_generated else "Manual"
            return " ".join(texts).replace("  ", "\n"), f"{t.language} ({typ})"

        except AttributeError:
            # Koshish 2: Purana Tarika (Agar 'list_transcripts' error de raha hai)
            print("Falling back to old method...")
            data = YouTubeTranscriptApi.get_transcript(video_id, languages=['hi', 'en'])
            
            # Simple Text formatting
            formatter = TextFormatter()
            formatted_text = formatter.format_transcript(data)
            return formatted_text, "Hindi/English (Old Lib)"

    except Exception as e:
        return None, str(e)

@app.route("/", methods=["GET", "POST"])
def index():
    transcript = None
    language = None
    video_id = None
    error = None

    if request.method == "POST":
        url = request.form.get("url")
        
        if not url:
            error = "कृपया यूट्यूब लिंक डालें।"
        else:
            video_id = extract_video_id(url)
            if not video_id:
                error = "गलत यूट्यूब लिंक डाला है भाई"
            else:
                transcript, error_or_language = get_transcript(video_id)
                
                if transcript:
                    language = error_or_language
                else:
                    if "No transcripts were found" in error_or_language:
                        error = "इस वीडियो में ट्रांसक्रिप्ट नहीं है।"
                    elif "is a private video" in error_or_language:
                        error = "यह वीडियो प्राइवेट है।"
                    elif "disabled" in error_or_language:
                        error = "इस वीडियो के लिए ट्रांसक्रिप्ट अक्षम (disabled) है।"
                    else:
                        error = f"Error: {error_or_language}"

    return render_template_string(HTML, transcript=transcript, language=language, video_id=video_id, error=error)

# FIX: Double underscore correct kiya hai (_name, __main_)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
