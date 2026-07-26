import json
import urllib.request
import os
import base64

def get_access_token():
    from google.oauth2 import service_account
    import google.auth.transport.requests
    
    creds = service_account.Credentials.from_service_account_file(
        'vertex_sa.json',
        scopes=['https://www.googleapis.com/auth/cloud-platform']
    )
    request = google.auth.transport.requests.Request()
    creds.refresh(request)
    return creds.token

def generate_image(prompt, output_filename):
    token = get_access_token()
    
    with open('vertex_sa.json', 'r') as f:
        sa_data = json.load(f)
    project_id = sa_data['project_id']
    
    # Nano Banana Pro
    model_id = "gemini-3-pro-image"
    url = f"https://aiplatform.googleapis.com/v1/projects/{project_id}/locations/global/publishers/google/models/{model_id}:generateContent"
    
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["IMAGE"]
        }
    }
    
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'))
    req.add_header('Content-Type', 'application/json')
    req.add_header('Authorization', f'Bearer {token}')
    
    try:
        with urllib.request.urlopen(req) as response:
            resp_data = json.loads(response.read().decode('utf-8'))
            
            part = resp_data['candidates'][0]['content']['parts'][0]
            if 'inlineData' in part:
                b64_data = part['inlineData']['data']
                img_data = base64.b64decode(b64_data)
                with open(output_filename, 'wb') as f:
                    f.write(img_data)
                print(f"Image successfully saved to {output_filename}")
            else:
                print("No image data found in the response:")
                print(json.dumps(resp_data, indent=2))
                
    except Exception as e:
        print(f"Error during API call: {e}")
        if hasattr(e, 'read'):
            print(e.read().decode('utf-8'))

if __name__ == "__main__":
    prompt = 'A digital illustration showing the exact official original ChatGPT logo (the recognizable OpenAI flower symbol with its exact shapes) in the center. To the left of it, a glowing 3D icon of the scales of justice (court symbol). To the right of it, a stylized logo representing the government portal eGov of Kazakhstan (blue and yellow colors, eagle or sun motif). The three distinct icons are connected to each other by glowing neon data streams and fiber optic wires, symbolizing a direct server integration. The background is a dark, high-tech cybersecurity server environment. Cinematic lighting, photorealistic icons, highly detailed, 8k resolution.'
    generate_image(prompt, "ai_lawyer_vertex.png")
