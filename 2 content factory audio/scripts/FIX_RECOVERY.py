import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
API_KEY = os.environ.get("GOOGLE_API_KEY")

OPERATIONS = [
    "models/veo-3.1-generate-preview/operations/s2a8kyx4kgcs",
    "models/veo-3.1-generate-preview/operations/bwnvkbmhfymb",
    "models/veo-3.1-generate-preview/operations/8ffz13npuf87",
    "models/veo-3.1-generate-preview/operations/ts6q2jh9t5iy",
    "models/veo-3.1-generate-preview/operations/8hab3ndmrrj9",
    "models/veo-3.1-lite-generate-preview/operations/c6zoovip38vr",
    "models/veo-3.1-lite-generate-preview/operations/knpg1dep35pq",
    "models/veo-3.1-lite-generate-preview/operations/3f4qrdnptafw",
    "models/veo-3.1-lite-generate-preview/operations/p7hy9p8nzwsm",
    "models/veo-3.1-lite-generate-preview/operations/27xlzqyqjh96"
]

RECOVERY_DIR = Path("outputs/RECOVERED_STUFF")
RECOVERY_DIR.mkdir(parents=True, exist_ok=True)

def recover():
    if not API_KEY:
        print("ERROR: GOOGLE_API_KEY not found.")
        return
    client = genai.Client(api_key=API_KEY)
    for op_name in OPERATIONS:
        try:
            print(f"🔍 Checking {op_name}...")
            # Using types.Operation object as string failed
            op = client.operations.get(types.Operation(name=op_name))
            if op.done:
                if hasattr(op.response, "generated_videos") and op.response.generated_videos:
                    vid = op.response.generated_videos[0].video
                    op_id = op_name.split('/')[-1]
                    output_path = RECOVERY_DIR / f"recovered_{op_id}.mp4"
                    print(f"✅ Found! Downloading...")
                    # Download bytes if uri is available
                    # Note: in some versions client.files.download works with video object
                    video_data = client.files.download(file=vid)
                    output_path.write_bytes(video_data)
                    print(f"💾 Saved to {output_path}")
                else:
                    print(f"⚠️ Done but no videos found in response.")
            else:
                print(f"⏳ Still in progress.")
        except Exception as e:
            print(f"❌ Error for {op_name}: {e}")

if __name__ == "__main__":
    recover()
