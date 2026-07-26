import sys
try:
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "youtube-transcript-api"])
    from youtube_transcript_api import YouTubeTranscriptApi

video_id = "FioRTWz7WMQ"
try:
    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ru', 'en'])
    text = " ".join([t['text'] for t in transcript])
    print(text)
except Exception as e:
    print(f"Error: {e}")
