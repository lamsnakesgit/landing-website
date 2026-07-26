import google.generativeai as genai
genai.configure(api_key="AIzaSyACWHFb9ud11-0_XFaeFWDVw9Iyg-KTS9k")
models = genai.list_models()
for m in models:
    if 'veo-3.1-lite' in m.name:
        print(f"Name: {m.name}")
        print(f"Supported methods: {m.supported_generation_methods}")

