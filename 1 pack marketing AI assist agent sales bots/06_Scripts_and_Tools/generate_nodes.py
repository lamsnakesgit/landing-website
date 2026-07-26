import json

nodes = [
  {
    "parameters": {
      "method": "POST",
      "url": "https://api.grsai.com/v1/chat/completions",
      "sendHeaders": True,
      "headerParameters": {
        "parameters": [
          {
            "name": "Authorization",
            "value": "=Bearer sk-55b4bfc2dfdf48bc92678dab6aa679af"
          },
          {
            "name": "Content-Type",
            "value": "application/json"
          }
        ]
      },
      "sendBody": True,
      "specifyBody": "json",
      "jsonBody": "={{ JSON.stringify({\n  \"model\": \"gemini-3.1-flash-lite\",\n  \"messages\": [\n    {\n      \"role\": \"user\",\n      \"content\": [\n        {\n          \"type\": \"text\",\n          \"text\": \"Что ты видишь на фото? Пожалуйста, извлеки весь текст с афиши.\"\n        },\n        {\n          \"type\": \"image_url\",\n          \"image_url\": {\n            \"url\": \"data:\" + $binary.data.mimeType + \";base64,\" + $binary.data.data\n          }\n        }\n      ]\n    }\n  ],\n  \"max_tokens\": 1500,\n  \"temperature\": 0.2\n}) }}",
      "options": {
        "timeout": 60000
      }
    },
    "id": "16c063d0-4160-4535-89f0-d689a0c4284e",
    "name": "Analyze image AI h1",
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 4.2,
    "position": [640, 976]
  },
  {
    "parameters": {
      "mode": "manual",
      "duplicateItem": False,
      "assignments": {
        "assignments": [
          {
            "id": "51ab2ff4-de65-4a3d-bbaa-b008c7351fb5",
            "name": "text",
            "value": "={{ $json.choices[0].message.content }}",
            "type": "string"
          }
        ]
      },
      "includeOtherFields": False,
      "options": {}
    },
    "id": "5755df94-5b70-4c35-aa70-da151b462b56",
    "name": "TextImage1",
    "type": "n8n-nodes-base.set",
    "typeVersion": 3.4,
    "position": [864, 976]
  }
]

connections = {
  "Analyze image AI h1": {
    "main": [
      [
        {
          "node": "TextImage1",
          "type": "main",
          "index": 0
        }
      ]
    ]
  }
}

print(json.dumps({"nodes": nodes, "connections": connections}, indent=2))
