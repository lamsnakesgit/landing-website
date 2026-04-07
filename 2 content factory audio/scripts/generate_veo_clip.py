import os
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv(".env")
api_key = os.environ.get("GOOGLE_API_KEY")

def generate_veo_clip(prompt, output_path="outputs/veo_clip_1.mp4"):
    if not api_key:
        print("Error: GOOGLE_API_KEY not found in .env")
        return

    client = genai.Client(api_key=api_key)
    
    print(f"Generating video with prompt: {prompt}")
    
    try:
        # Using the veo-3.1-lite-generate-preview model with generate_videos method
        print("Starting video generation (this may take a few minutes)...")
        operation = client.models.generate_videos(
            model="veo-3.1-lite-generate-preview",
            prompt=prompt,
            config=types.GenerateVideosConfig(
                number_of_videos=1,
            )
        )
        
        # Wait for the operation to complete
        while not operation.done:
            print(f"Waiting for video generation (Operation: {operation.name})...", end="\r")
            time.sleep(10)
            # The SDK's operations.get expects the operation object or name. 
            # It seems to access .name on the input, so we pass the object.
            operation = client.operations.get(operation)
        
        if operation.error:
            print(f"\nGeneration failed: {operation.error}")
            return

        # The result should contain the video data or a reference
        print("\nGeneration complete! Saving video...")
        
        # Based on typical GenAI SDK patterns for LROs
        result = operation.result
        if result and result.generated_videos:
            video_file = result.generated_videos[0]
            # If it's a file reference, we might need to download it
            # If it's raw data, we write it
            if hasattr(video_file, 'video') and hasattr(video_file.video, 'data'):
                with open(output_path, "wb") as f:
                    f.write(video_file.video.data)
                print(f"Video saved to {output_path}")
            elif hasattr(video_file, 'video') and hasattr(video_file.video, 'uri'):
                # If it's a URI, we need to download it. 
                # The URI looks like: https://generativelanguage.googleapis.com/v1beta/files/file_id:download?alt=media
                uri = video_file.video.uri
                print(f"Downloading video from URI: {uri}")
                
                # Extract file ID from URI if possible to use SDK
                # Example: .../files/fppg3sldmuw5:download...
                file_id = None
                if '/files/' in uri:
                    file_id = uri.split('/files/')[1].split(':')[0]
                
                try:
                    if file_id:
                        print(f"Using SDK to download file: {file_id}")
                        # The SDK download method might expect the name as a positional argument or 'file_name'
                        try:
                            file_content = client.files.download(file_id)
                        except:
                            # Fallback to urllib if SDK fails
                            print("SDK download failed, falling back to urllib...")
                            import urllib.request
                            req = urllib.request.Request(uri)
                            req.add_header('X-Goog-Api-Key', api_key)
                            with urllib.request.urlopen(req) as response:
                                file_content = response.read()
                        
                        with open(output_path, "wb") as f:
                            f.write(file_content)
                    else:
                        import urllib.request
                        req = urllib.request.Request(uri)
                        req.add_header('X-Goog-Api-Key', api_key)
                        with urllib.request.urlopen(req) as response:
                            with open(output_path, "wb") as f:
                                f.write(response.read())
                    print(f"Video saved to {output_path}")
                except Exception as download_error:
                    print(f"Failed to download video: {download_error}")
                    print("Note: Ensure 'Generative Language API' is enabled in your Google Cloud Console.")
        else:
            print("No video found in the operation result.")
            print(f"Result: {result}")
            
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Refined dynamic prompt based on VEO_3_1_MASTER_GUIDE.md
    dynamic_prompt = "Dynamic high-speed macro shot: A sleek black 'sen sulu' cosmetic tube aggressively enters the frame with a whip-pan motion, stopping abruptly with high inertia. Metallic gold embossed letters catch sharp rim lighting. The camera then performs a rapid 180-degree orbit around the tube. High contrast, premium beauty commercial style, 4k, 60fps look, Unreal Engine 5.4 render style."
    generate_veo_clip(dynamic_prompt, output_path="outputs/veo_clip_1_dynamic.mp4")
