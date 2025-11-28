from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

video_id = 'pxiP-HJLCx0'

try:
    # 1. Transcript List प्राप्त करें
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

    # 2. English transcript ढूंढें (चाहे Manual हो या Auto-generated)
    # यह सबसे पहले Manual ढूंढेगा, नहीं मिला तो Auto-generated लेगा
    transcript = transcript_list.find_transcript(['en'])
    
    # Transcript data fetch करें
    transcript_data = transcript.fetch()

    print(f"Transcript found in language: {transcript.language}")

    # 3. फाइल में सेव करें (सिर्फ टेक्स्ट)
    with open("subtitles.txt", "w", encoding="utf-8") as f:
        for line in transcript_data:
            # line एक dictionary है: {'text': '...', 'start': ..., 'duration': ...}
            
            # सिर्फ टेक्स्ट सेव करने के लिए:
            f.write(f"{line['text']}\n") 
            
            # अगर Time के साथ सेव करना है तो नीचे वाली लाइन use करें:
            # f.write(f"{line['start']} - {line['text']}\n")

    print("File 'subtitles.txt' saved successfully.")

except NoTranscriptFound:
    print("Error: इस वीडियो के लिए English subtitles उपलब्ध नहीं हैं।")
except TranscriptsDisabled:
    print("Error: इस वीडियो पर Subtitles बंद (disabled) हैं।")
except Exception as e:
    print(f"कोई अन्य गड़बड़ी हुई: {e}")
