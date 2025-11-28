from flask import Flask, render_template, request
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import re

app = Flask(___name___)

def extract_video_id(url):
    """
    YouTube URL se Video ID nikalne ka robust function (Regex based).
    Ye normal videos, shorts, live streams, aur share links sabko handle karega.
    """
    # Regex pattern jo har tarah ke link se ID nikal leta hai
    regex = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(regex, url)
    if match:
        return match.group(1)
    return None

@app.route('/', methods=['GET', 'POST'])
def index():
    transcript_text = None
    error_message = None

    if request.method == 'POST':
        video_url = request.form.get('url')
        
        if video_url:
            video_id = extract_video_id(video_url)
            
            if video_id:
                try:
                    # Transcript fetch karna (English ya Hindi priority me)
                    transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'hi'])
                    
                    # Formatter ka use karke clean text banana
                    formatter = TextFormatter()
                    transcript_text = formatter.format_transcript(transcript_list)
                    
                except Exception as e:
                    # Agar subtitles off hain ya koi aur error hai
                    print(f"System Error: {e}")
                    error_message = "Error: Is video mein subtitles/captions available nahi hain ya restrict kiye gaye hain."
            else:
                error_message = "Invalid YouTube URL provided. Sahi link dalein."
        else:
            error_message = "Please enter a URL."

    return render_template('index.html', transcript=transcript_text, error=error_message)

if __name__ == '___main___':
    app.run(debug=True)

