from flask import Flask, render_template, request
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from youtube_transcript_api.formatters import TextFormatter
import re

app = Flask(__name__)

def extract_video_id(url):
    """
    Robust function to extract Video ID from URL
    """
    regex = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(regex, url)
    if match:
        return match.group(1)
    return None

def get_transcript(video_id, target_language='en'):
    """
    Advanced Logic: Finds best transcript and translates if needed.
    """
    try:
        # 1. Available Transcripts ki list nikalein
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # 2. Best available transcript dhundhein
        try:
            # Koshish karein ki target language (English) direct mil jaye
            transcript_obj = transcript_list.find_transcript([target_language])
        except NoTranscriptFound:
            try:
                # Agar direct nahi mili, to Manually Created dhundhein
                transcript_obj = transcript_list.find_manually_created_transcript()
            except:
                # Agar wo bhi nahi, to Auto-generated le lein (koi bhi language)
                transcript_obj = list(transcript_list)[0] 
        
        # 3. Translate karein (Agar language match nahi karti)
        if transcript_obj.language_code != target_language:
            try:
                # Translate to English
                final_transcript = transcript_obj.translate(target_language).fetch()
            except Exception as e:
                # Agar translation fail ho jaye, to original return karein
                print(f"Translation failed: {e}")
                final_transcript = transcript_obj.fetch()
        else:
            final_transcript = transcript_obj.fetch()

        # Format transcript to plain text
        formatter = TextFormatter()
        formatted_text = formatter.format_transcript(final_transcript)
        
        return {
            'success': True,
            'transcript': formatted_text
        }
        
    except TranscriptsDisabled:
        return {'success': False, 'error': 'Subtitles are disabled for this video.'}
    except NoTranscriptFound:
        return {'success': False, 'error': 'No transcript found for this video.'}
    except Exception as e:
        return {'success': False, 'error': f'Error fetching transcript: {str(e)}'}

@app.route('/', methods=['GET', 'POST'])
def index():
    transcript_text = None
    error_message = None

    if request.method == 'POST':
        video_url = request.form.get('url')
        
        if video_url:
            video_id = extract_video_id(video_url)
            
            if video_id:
                # Advanced function call karein
                result = get_transcript(video_id, target_language='en')
                
                if result['success']:
                    transcript_text = result['transcript']
                else:
                    error_message = result['error']
            else:
                error_message = "Invalid YouTube URL. Please check the link."
        else:
            error_message = "Please enter a URL."

    return render_template('index.html', transcript=transcript_text, error=error_message)

if __name__ == '__main__':
    app.run(debug=True)
