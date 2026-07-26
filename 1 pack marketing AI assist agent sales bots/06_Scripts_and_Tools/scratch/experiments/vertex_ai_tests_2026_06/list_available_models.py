import os
from google.cloud import aiplatform

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/2 accounts sub security/amocrm_wazzup_analytics/google_service_account.json'

aiplatform.init(project="gen-lang-client-0675220826", location="us-central1")

try:
    print("Listing models...")
    # List model deployments
    models = aiplatform.Model.list()
    print(f"Found {len(models)} models:")
    for model in models:
        print(f"Name: {model.name}, Display Name: {model.display_name}")
except Exception as e:
    print(f"Error listing custom models: {e}")

# Try listing publisher models (base models available to the project)
try:
    print("\nListing publisher models (via REST)...")
    import requests, google.auth
    from google.auth.transport.requests import Request
    
    credentials, project = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
    credentials.refresh(Request())
    
    # Vertex AI Model Garden/Publisher Models API
    url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{project}/locations/us-central1/publisherModels"
    headers = {'Authorization': f'Bearer {credentials.token}'}
    
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        models_data = res.json().get("publisherModels", [])
        print(f"Found {len(models_data)} publisher models:")
        for m in models_data[:20]: # Print first 20
            print(f"- {m.get('name')}: {m.get('displayName')}")
        
        # Check specifically if gemini-3.1-flash-image is in the list
        all_names = [m.get('name', '') for m in models_data]
        matches = [name for name in all_names if "gemini-3.1" in name or "image" in name or "banana" in name]
        print("\nMatching models:")
        for match in matches:
            print(match)
    else:
        print(f"Error: {res.status_code}")
        print(res.text[:500])
except Exception as e:
    print(f"Error listing publisher models: {e}")
