import os
import sys

def log(msg):
    print(msg, flush=True)

log("Python version: " + sys.version)
log("GOOGLE_APPLICATION_CREDENTIALS: " + str(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")))

try:
    import google.generativeai as google_genai
    log("google.generativeai is installed. Version: " + google_genai.__version__)
except ImportError:
    log("google.generativeai is NOT installed.")

try:
    from google import genai as new_genai
    log("google-genai (new SDK) is installed.")
except ImportError:
    log("google-genai (new SDK) is NOT installed.")

try:
    from google.cloud import aiplatform
    log("google-cloud-aiplatform is installed. Version: " + aiplatform.__version__)
except ImportError:
    log("google-cloud-aiplatform is NOT installed.")
