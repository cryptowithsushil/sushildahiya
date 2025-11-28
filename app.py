def get_transcript(video_id, target_language='en'):
    try:
        # 1. Available Transcripts की list निकालें
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # 2. Logic: सबसे पहले manually created ढूंढें, नहीं तो generated
        # हम सीधे target language नहीं ढूंढ रहे, हम "best available" ढूंढ रहे हैं
        try:
            # कोशिश करें कि user की मांगी हुई भाषा में direct मिल जाए
            transcript_obj = transcript_list.find_transcript([target_language])
            final_transcript = transcript_obj.fetch()
        except NoTranscriptFound:
            # अगर direct नहीं मिली, तो कोई भी available transcript लें
            # (Manually created को प्राथमिकता दें)
            try:
                transcript_obj = transcript_list.find_manually_created_transcript()
            except:
                # अगर manual नहीं है, तो auto-generated लें
                transcript_obj = list(transcript_list)[0] 
            
            # 3. अब उसे Target Language में Translate करें
            if transcript_obj.language_code != target_language:
                try:
                    final_transcript = transcript_obj.translate(target_language).fetch()
                except Exception as e:
                    # अगर translation fail हो जाए (rare case), तो original ही दे दें
                    final_transcript = transcript_obj.fetch()
            else:
                final_transcript = transcript_obj.fetch()

        # Format transcript
        formatted_transcript = '\n'.join([item['text'] for item in final_transcript])
        
        return {
            'success': True,
            'transcript': formatted_transcript,
            'segments': final_transcript,
            'video_id': video_id,
            'segment_count': len(final_transcript),
            'detected_language': transcript_obj.language_code  # यह भी return करना अच्छा है
        }
    
    except TranscriptsDisabled:
        return {'success': False, 'error': 'Transcripts are disabled for this video'}
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {'success': False, 'error': f'Error fetching transcript: {str(e)}'}
