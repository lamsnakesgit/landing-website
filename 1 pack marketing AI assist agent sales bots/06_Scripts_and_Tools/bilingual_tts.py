import os
import re
import asyncio
import argparse
import tempfile
import edge_tts
from pydub import AudioSegment

# Default Voices
DEFAULT_RU_VOICE = "ru-RU-DmitryNeural"
DEFAULT_EN_VOICE = "en-US-ChristopherNeural"

def split_text_by_language(text):
    """
    Splits text into Russian and English segments.
    Uses regex to identify contiguous blocks of English words.
    """
    segments = []
    # Pattern to match words containing English letters (can include numbers, spaces, hyphens)
    pattern = r"([A-Za-z0-9]+(?:[ \-\'][A-Za-z0-9]+)*)"
    
    parts = re.split(pattern, text)
    for p in parts:
        if not p.strip():
            continue
        # Check if it's an English segment
        if re.search(r'[A-Za-z]', p):
            segments.append({"lang": "en", "text": p})
        else:
            segments.append({"lang": "ru", "text": p})
            
    # Merge consecutive segments of the same language
    merged = []
    for s in segments:
        if merged and merged[-1]["lang"] == s["lang"]:
            merged[-1]["text"] += s["text"]
        else:
            merged.append(s)
            
    return merged

async def generate_segment_audio(text, voice, output_path):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

async def generate_bilingual_audio(text, output_file, ru_voice, en_voice):
    segments = split_text_by_language(text)
    
    temp_files = []
    tasks = []
    
    for i, seg in enumerate(segments):
        voice = en_voice if seg["lang"] == "en" else ru_voice
        tmp_path = f"temp_segment_{i}.mp3"
        temp_files.append(tmp_path)
        
        print(f"[{seg['lang'].upper()}] -> '{seg['text']}' (Voice: {voice})")
        tasks.append(generate_segment_audio(seg["text"], voice, tmp_path))
        
    # Generate all audio files concurrently
    await asyncio.gather(*tasks)
    
    print("Concatenating audio segments...")
    combined = AudioSegment.empty()
    
    for tmp_path in temp_files:
        if os.path.exists(tmp_path):
            segment_audio = AudioSegment.from_mp3(tmp_path)
            combined += segment_audio
            os.remove(tmp_path) # Cleanup
            
    combined.export(output_file, format="mp3")
    print(f"Successfully saved bilingual audio to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate bilingual TTS (RU + EN)")
    parser.add_argument("--text", type=str, required=True, help="Mixed language text to synthesize")
    parser.add_argument("--output", type=str, default="output_bilingual.mp3", help="Output MP3 file path")
    parser.add_argument("--ru-voice", type=str, default=DEFAULT_RU_VOICE, help="Russian edge-tts voice")
    parser.add_argument("--en-voice", type=str, default=DEFAULT_EN_VOICE, help="English edge-tts voice")
    
    args = parser.parse_args()
    
    asyncio.run(generate_bilingual_audio(args.text, args.output, args.ru_voice, args.en_voice))
