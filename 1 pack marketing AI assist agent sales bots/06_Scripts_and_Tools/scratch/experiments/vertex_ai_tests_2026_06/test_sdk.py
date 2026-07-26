import os
import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'vertex_sa.json'
PROJECT_ID = "my-project-28666-8-5-26-0-crm"  # Grabbed from the error message earlier
LOCATION = "us-central1"

vertexai.init(project=PROJECT_ID, location=LOCATION)

try:
    model = GenerativeModel("gemini-3.1-flash-image")
    response = model.generate_content("A robot holding a sign saying HELLO WORLD")
    print("SUCCESS!")
    print(response)
except Exception as e:
    print("Error:", e)
