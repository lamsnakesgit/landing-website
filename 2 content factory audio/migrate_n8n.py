import json
import os

original_path = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/2 content factory audio/MediaFactorry 1.2.json"
output_path = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/2 content factory audio/MediaFactorry_Vertex_Final.json"

with open(original_path, 'r') as f:
    wf = json.load(f)

# 1. Add Config Node
config_node = {
    "parameters": {
        "assignments": {
            "assignments": [
                {"id": "p-id", "name": "projectId", "value": "YOUR_PROJECT_ID", "type": "string"},
                {"id": "r-id", "name": "region", "value": "us-central1", "type": "string"}
            ]
        }
    },
    "type": "n8n-nodes-base.set",
    "typeVersion": 3.4,
    "position": [1100, -200],
    "name": "Config"
}
wf["nodes"].append(config_node)

# 2. Modify Nodes
for node in wf["nodes"]:
    # Replace OpenAI GPT with Gemini
    if "openAi" in node["type"] or "lmChatOpenAi" in node["type"]:
        node["type"] = "@n8n/n8n-nodes-langchain.lmChatGoogleVertexAi"
        node["typeVersion"] = 1
        # Preserve original prompt
        prompt = node["parameters"].get("text", "")
        node["parameters"] = {
            "modelName": "gemini-1.5-pro-001",
            "options": {"temperature": 0.7}
        }
        # If it was a chain node
        if "chainLlm" in node["type"]:
            node["type"] = "@n8n/n8n-nodes-langchain.chainLlm"
            # Keep langchain logic
            pass
            
    # Replace Kie.ai Video with Vertex AI Veo
    if node["type"] == "n8n-nodes-base.httpRequest" and "kie.ai" in node["parameters"].get("url", ""):
        node["name"] = "Generate Video (Veo 3.1)"
        node["parameters"]["url"] = "https://{{ $node[\"Config\"].json.region }}-aiplatform.googleapis.com/v1/projects/{{ $node[\"Config\"].json.projectId }}/locations/{{ $node[\"Config\"].json.region }}/publishers/google/models/veo-001:predictLongRunning"
        node["parameters"]["method"] = "POST"
        node["parameters"]["sendBody"] = True
        node["parameters"]["specifyBody"] = "json"
        
    # Clear credentials to avoid import ID conflicts
    if "credentials" in node:
        del node["credentials"]

# 3. Save
with open(output_path, 'w') as f:
    json.dump(wf, f, indent=2)
