import os
import sys
import time
from google import genai
from google.genai import types

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/2 accounts sub security/amocrm_wazzup_analytics/google_service_account.json"

client = genai.Client(vertexai=True, project="gen-lang-client-0675220826", location="us-central1")
operation_id = "projects/gen-lang-client-0675220826/locations/us-central1/publishers/google/models/veo-3.1-lite-generate-001/operations/4aabbd6b-ff54-43c6-a876-ab170a0e5111"

operation = client.operations.get(operation_id)
print("done:", operation.done)
if operation.done and operation.result and operation.result.generated_videos:
    video = operation.result.generated_videos[0].video
    print("uri:", video.uri)
    if hasattr(video, 'video_bytes') and video.video_bytes:
        print("video_bytes length:", len(video.video_bytes))
    else:
        print("no video_bytes")
    print("Attributes:", dir(video))
