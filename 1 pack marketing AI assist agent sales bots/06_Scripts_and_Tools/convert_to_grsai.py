import json

# Читаем оригинальный workflow
with open('/tmp/google_calendar_workflow.json', 'r') as f:
    workflow = json.load(f)

# Новые ID для OpenAI нод
new_llm_id_1 = "grsai-llm-01-aaaaaaaaaaaa"
new_llm_id_2 = "grsai-llm-02-bbbbbbbbbbbb"

# Заменяем ноды Gemini на OpenAI Chat Model с GRSai
for node in workflow['nodes']:
    if node['id'] == "b2a1e424-2152-4383-9117-fa318634975a":
        node['type'] = "@n8n/n8n-nodes-langchain.lmChatOpenAi"
        node['typeVersion'] = 1.3
        node['name'] = "GRSai Chat Model"
        node['parameters'] = {
            "model": {
                "__rl": True,
                "value": "claude-sonnet-4-6",
                "mode": "id"
            },
            "options": {}
        }
        node['credentials'] = {
            "openAiApi": {
                "id": "GRSAI_CREDENTIAL_PLACEHOLDER",
                "name": "GRSai API (OpenAI-compatible)"
            }
        }
        node['id'] = new_llm_id_1
        
    elif node['id'] == "e63ba007-f5e6-4647-9845-142d1dcd2ab5":
        node['type'] = "@n8n/n8n-nodes-langchain.lmChatOpenAi"
        node['typeVersion'] = 1.3
        node['name'] = "GRSai Chat Model 1"
        node['parameters'] = {
            "model": {
                "__rl": True,
                "value": "claude-sonnet-4-6",
                "mode": "id"
            },
            "options": {}
        }
        node['credentials'] = {
            "openAiApi": {
                "id": "GRSAI_CREDENTIAL_PLACEHOLDER",
                "name": "GRSai API (OpenAI-compatible)"
            }
        }
        node['id'] = new_llm_id_2

# Обновляем connections
connections_str = json.dumps(workflow['connections'])
connections_str = connections_str.replace("b2a1e424-2152-4383-9117-fa318634975a", new_llm_id_1)
connections_str = connections_str.replace("e63ba007-f5e6-4647-9845-142d1dcd2ab5", new_llm_id_2)
workflow['connections'] = json.loads(connections_str)

# Обновляем name
workflow['name'] = "03 - GOOGLE CALENDAR ASSISTENT (GRSai LLM)"

# Сохраняем
output_path = 'n8n_templates/google_calendar_assistant_grsai.json'
with open(output_path, 'w') as f:
    json.dump(workflow, f, indent=2, ensure_ascii=False)

print(f"Saved to {output_path}")
print(f"Nodes modified: 2 Gemini -> 2 GRSai OpenAI")
print(f"New LLM IDs: {new_llm_id_1}, {new_llm_id_2}")