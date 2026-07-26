import json, sys

with open('main_workflow_remote.json', 'r') as f:
    data = json.load(f)

# Фиксим ноду HTTP Request2 image tool (id: a3ee88b9)
for n in data['nodes']:
    if n.get('id') == 'a3ee88b9-e568-4029-a60d-bddbce04f810':
        n['parameters'] = {
            "toolDescription": (
                "USE this tool when user asks to draw, generate, show photo or create an image. "
                "Pass detailed image description in 'query' parameter. "
                "Makes an HTTP request to GRSAI gpt-image-2 API and returns the generated image URL."
            ),
            "method": "POST",
            "url": "https://api.grsai.com/v1/images/generations",
            "sendHeaders": True,
            "headerParameters": {
                "parameters": [
                    {
                        "name": "Authorization",
                        "value": "Bearer sk-55b4bfc2dfdf48bc92678dab6aa679af"
                    },
                    {
                        "name": "Content-Type",
                        "value": "application/json"
                    }
                ]
            },
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": '={{ JSON.stringify({ "model": "gpt-image-2", "prompt": $fromAI("query", "Detailed image description prompt", "string"), "n": 1, "size": "1024x1024" }) }}',
            "options": {}
        }
        print(f"Fixed node: {n['name']}")
        break

with open('main_workflow_fixed.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False)

print("Done - saved to main_workflow_fixed.json")
