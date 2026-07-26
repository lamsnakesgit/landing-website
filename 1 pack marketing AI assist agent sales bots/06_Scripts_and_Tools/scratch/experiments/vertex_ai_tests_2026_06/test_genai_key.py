import google.generativeai as genai
import sys

api_key = "AQ.Ab8RN6K5ssAcNr8kU8asQysWhqtc8NiFNVevK-p_VDciOL3hfA"
genai.configure(api_key=api_key)

try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Напиши ровно два слова: Ключ работает!")
    print("SUCCESS: ", response.text.strip())
except Exception as e:
    print(f"Error testing key: {e}")
    sys.exit(1)
