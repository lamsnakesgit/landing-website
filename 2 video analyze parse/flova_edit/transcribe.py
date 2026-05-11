import whisper
import sys
import os
import glob

def main():
    print("Loading whisper model (base)...")
    model = whisper.load_model("base")
    
    files = glob.glob(os.path.expanduser("~/Downloads/flova_Shot*.mp4"))
    files.sort()
    
    print(f"Found {len(files)} files to process.")
    
    results = []
    
    for f in files:
        print(f"Processing {os.path.basename(f)}...")
        try:
            result = model.transcribe(f)
            text = result["text"].strip()
            print(f"--> {text}")
            results.append((os.path.basename(f), text))
        except Exception as e:
            print(f"Error processing {f}: {e}")
            
    print("\n--- FINAL RESULTS ---")
    for name, text in results:
        print(f"{name}: {text}")

if __name__ == "__main__":
    main()
