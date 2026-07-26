import os
import google.auth
from google.auth.transport.requests import Request
import requests
import json
import base64
from pathlib import Path

# Vertex AI Project details (you might need to extract the project ID from the SA if not hardcoded)
PROJECT_ID = "YOUR_PROJECT_ID" # Will be fetched dynamically from the SA
LOCATION = "us-central1"

def generate_image_vertex(prompt: str, output_filename: str):
    # 1. Set the env var to point to the local service account file
    workspace_root = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots"
    sa_path = os.path.join(workspace_root, "vertex_sa.json")
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = sa_path

    if not os.path.exists(sa_path):
        print(f"Error: Service account file not found at {sa_path}")
        return False

    # Extract Project ID from SA file
    with open(sa_path, 'r') as f:
        sa_data = json.load(f)
        project_id = sa_data.get("project_id")

    # 2. Get credentials
    credentials, _ = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
    credentials.refresh(Request())

    # 3. Call Vertex AI Imagen API (imagegeneration@006)
    url = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{LOCATION}/publishers/google/models/imagegeneration@006:predict"
    
    headers = {
        "Authorization": f"Bearer {credentials.token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    
    data = {
        "instances": [
            {
                "prompt": prompt
            }
        ],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": "1:1" # Or 4:5 for Instagram carousels
        }
    }

    print(f"Calling Vertex AI for prompt: {prompt}")
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        resp_json = response.json()
        if "predictions" in resp_json and len(resp_json["predictions"]) > 0:
            # The image is returned as a base64 encoded string
            encoded_image = resp_json["predictions"][0]["bytesBase64Encoded"]
            image_data = base64.b64decode(encoded_image)
            
            with open(output_filename, "wb") as f:
                f.write(image_data)
            print(f"✅ Image saved to {output_filename}")
            return True
        else:
            print("Error: No predictions found in response.")
            print(resp_json)
            return False
    else:
        print(f"Error {response.status_code}: {response.text}")
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        test_prompt = sys.argv[1]
        generate_image_vertex(test_prompt, "output_test.png")
    else:
        print("Please provide a prompt. Usage: python generate_vertex.py 'prompt text'")
