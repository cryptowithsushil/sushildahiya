from youtube_transcript_api import YouTubeTranscriptApi

def get_best_transcript(video_id):
    """
    Tries to get transcript in this order:
    1. Hindi (manual)
    2. English (manual)
    3. Hindi (auto-generated)
    4. English (auto-generated)
    5. Any available transcript
    """
    try:
        # This returns a TranscriptList object with all available transcripts
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # Priority 1 & 2: Manually created Hindi or English
        try:
            transcript = transcript_list.find_manually_created_transcript(['hi', 'en'])
            print(f"Found manual transcript: {transcript.language} ({transcript.language_code})")
            return transcript.fetch()
        except:
            pass

        # Priority 3: Auto-generated Hindi
        try:
            transcript = transcript_list.find_generated_transcript(['hi'])
            print(f"Found auto-generated Hindi transcript")
            return transcript.fetch()
        except:
            pass

        # Priority 4: Auto-generated English
        try:
            transcript = transcript_list.find_generated_transcript(['en'])
            print(f"Found auto-generated English transcript")
            return transcript.fetch()
        except:
            pass

        # Priority 5: Any first available transcript (manual or auto)
        transcript = next(iter(transcript_list))
        print(f"Fallback: Using {transcript.language} ({transcript.language_code}) - {'auto' if transcript.is_generated else 'manual')")
        return transcript.fetch()

    except Exception as e:
        print("No transcript available for this video:", e)
        return None

# —————— HOW TO USE ——————
video_id = "dQw4w9WgXcQ"   # Change this to your YouTube video ID

transcript_data = get_best_transcript(video_id)

if transcript_data:
    print("\nTranscript:\n")
    for line in transcript_data:
        print(line['text'])
else:
    print("Could not retrieve any transcript.")
