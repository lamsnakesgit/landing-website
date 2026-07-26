import google.generativeai as genai

API_KEY = "AIzaSyACWHFb9ud11-0_XFaeFWDVw9Iyg-KTS9k"
genai.configure(api_key=API_KEY)

try:
    models = genai.list_models()
    for m in models:
        print(m.name)
    print("Done checking models.")
except Exception as e:
    print("Error:", e)
