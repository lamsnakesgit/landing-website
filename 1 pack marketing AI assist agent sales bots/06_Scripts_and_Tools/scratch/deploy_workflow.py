import os
import json
import requests

# Загрузка переменных из .env файла
env_vars = {}
with open('.env', 'r') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        key, val = line.split('=', 1)
        env_vars[key.strip()] = val.strip().strip('"').strip("'")

n8n_url = "https://n8n.aiconicvibe.store"
n8n_api_key = env_vars.get("N8N_API_KEY")
evolution_api_key = env_vars.get("EVOLUTION_API_KEY")
evolution_instance = env_vars.get("EVOLUTION_INSTANCE")
evolution_url = env_vars.get("EVOLUTION_BASE_URL")
tg_token = env_vars.get("TG_REALSTATE_SMM_BOT")
google_key = env_vars.get("GOOGLE_API_KEY")

print(f"Инициализация импорта для n8n: {n8n_url}")

# Создаем структуру Workflow JSON с учетом всех параметров пользователя
workflow_data = {
    "name": "🔥 Evolution WhatsApp ↔ Telegram Master Bridge with Media, Participant Tracker & AI Intro v1",
    "nodes": [
        {
            "parameters": {
                "httpMethod": "POST",
                "path": "evolution-master-bridge",
                "options": {}
            },
            "id": "1",
            "name": "Evolution Webhook",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 1,
            "position": [0, 300]
        },
        {
            "parameters": {
                "rules": {
                    "values": [
                        {
                            "conditions": {
                                "options": {
                                    "caseSensitive": True,
                                    "leftValue": "",
                                    "typeValidation": "strict"
                                },
                                "conditions": [
                                    {
                                        "id": "is-message",
                                        "leftHandSide": "={{ $json.body.event }}",
                                        "operator": "equal",
                                        "rightHandSide": "messages.upsert"
                                    }
                                ],
                                "combinator": "and"
                            },
                            "outputIndex": 0
                        },
                        {
                            "conditions": {
                                "options": {
                                    "caseSensitive": True,
                                    "leftValue": "",
                                    "typeValidation": "strict"
                                },
                                "conditions": [
                                    {
                                        "id": "is-participants-update",
                                        "leftHandSide": "={{ $json.body.event }}",
                                        "operator": "equal",
                                        "rightHandSide": "group-participants.update"
                                    }
                                ],
                                "combinator": "and"
                            },
                            "outputIndex": 1
                        }
                    ]
                }
            },
            "id": "2",
            "name": "Event Router",
            "type": "n8n-nodes-base.switch",
            "typeVersion": 1,
            "position": [200, 300]
        },
        {
            "parameters": {
                "jsCode": """// Нормализация данных сообщения из Evolution API
const body = $input.first().json.body || {};
const data = body.data || {};
const key = data.key || {};
const message = data.message || {};
const messageType = data.messageType;

const fromMe = key.fromMe || False;
const remoteJid = key.remoteJid || '';
const senderName = data.pushName || 'Unknown';
const messageId = key.id || '';

// Получаем текст в зависимости от типа
let text = '';
if (messageType === 'conversation') {
  text = message.conversation;
} else if (messageType === 'extendedTextMessage') {
  text = message.extendedTextMessage.text;
} else if (messageType && message[messageType]) {
  text = message[messageType].caption || '';
}

const mediaTypes = ['imageMessage', 'videoMessage', 'audioMessage', 'documentMessage'];
const hasMedia = mediaTypes.includes(messageType);

return [{
  json: {
    event: 'message',
    fromMe,
    remoteJid,
    senderName,
    messageId,
    messageType,
    text,
    hasMedia
  }
}];"""
            },
            "id": "3",
            "name": "Normalize Message",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [420, 180]
        },
        {
            "parameters": {
                "conditions": {
                    "boolean": [
                        {
                            "value1": "={{ $json.fromMe }}",
                            "value2": True
                        }
                    ]
                }
            },
            "id": "4",
            "name": "Ignore Self Messages",
            "type": "n8n-nodes-base.if",
            "typeVersion": 1,
            "position": [620, 180]
        },
        {
            "parameters": {
                "conditions": {
                    "boolean": [
                        {
                            "value1": "={{ $json.hasMedia }}",
                            "value2": True
                        }
                    ]
                }
            },
            "id": "5",
            "name": "Has Media?",
            "type": "n8n-nodes-base.if",
            "typeVersion": 1,
            "position": [840, 180]
        },
        {
            "parameters": {
                "method": "POST",
                "url": f"{evolution_url}/chat/getBase64FromMediaMessage/{evolution_instance}",
                "sendHeaders": True,
                "headerParameters": {
                    "parameters": [
                        {
                            "name": "apikey",
                            "value": evolution_api_key
                        },
                        {
                            "name": "Content-Type",
                            "value": "application/json"
                        }
                    ]
                },
                "sendBody": True,
                "specifyBody": "json",
                "jsonBody": "={\n  \"message\": {\n    \"key\": {\n      \"id\": \"{{ $json.messageId }}\"\n    }\n  },\n  \"convertToMp4\": true\n}",
                "options": {}
            },
            "id": "6",
            "name": "Get Media Base64",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.1,
            "position": [1060, 80]
        },
        {
            "parameters": {
                "jsCode": """// Декодируем Base64 в бинарное свойство
const item = $input.first().json;
const base64Data = item.base64;
const messageType = $('Normalize Message').first().json.messageType;

let mimeType = 'application/octet-stream';
let fileName = 'file';

if (messageType === 'imageMessage') { mimeType = 'image/jpeg'; fileName = 'photo.jpg'; }
else if (messageType === 'videoMessage') { mimeType = 'video/mp4'; fileName = 'video.mp4'; }
else if (messageType === 'audioMessage') { mimeType = 'audio/ogg'; fileName = 'voice.ogg'; }
else if (messageType === 'documentMessage') { mimeType = 'application/pdf'; fileName = 'document.pdf'; }

return {
  json: {
    ...$('Normalize Message').first().json,
    mimeType,
    fileName
  },
  binary: {
    data: {
      data: base64Data,
      mimeType: mimeType,
      fileName: fileName
    }
  }
};"""
            },
            "id": "7",
            "name": "Base64 Decode",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [1280, 80]
        },
        {
            "parameters": {
                "rules": {
                    "values": [
                        {
                            "conditions": {
                                "options": {
                                    "caseSensitive": True,
                                    "leftValue": "",
                                    "typeValidation": "strict"
                                },
                                "conditions": [
                                    {
                                        "id": "is-image",
                                        "leftHandSide": "={{ $json.messageType }}",
                                        "operator": "equal",
                                        "rightHandSide": "imageMessage"
                                    }
                                ],
                                "combinator": "and"
                            },
                            "outputIndex": 0
                        },
                        {
                            "conditions": {
                                "options": {
                                    "caseSensitive": True,
                                    "leftValue": "",
                                    "typeValidation": "strict"
                                },
                                "conditions": [
                                    {
                                        "id": "is-video",
                                        "leftHandSide": "={{ $json.messageType }}",
                                        "operator": "equal",
                                        "rightHandSide": "videoMessage"
                                    }
                                ],
                                "combinator": "and"
                            },
                            "outputIndex": 1
                        },
                        {
                            "conditions": {
                                "options": {
                                    "caseSensitive": True,
                                    "leftValue": "",
                                    "typeValidation": "strict"
                                },
                                "conditions": [
                                    {
                                        "id": "is-audio",
                                        "leftHandSide": "={{ $json.messageType }}",
                                        "operator": "equal",
                                        "rightHandSide": "audioMessage"
                                    }
                                ],
                                "combinator": "and"
                            },
                            "outputIndex": 2
                        }
                    ]
                }
            },
            "id": "8",
            "name": "Switch Media Type",
            "type": "n8n-nodes-base.switch",
            "typeVersion": 1,
            "position": [1500, 80]
        },
        {
            "parameters": {
                "chatId": "YOUR_TG_CHAT_ID",
                "file": "data",
                "additionalFields": {
                    "caption": "=📸 <b>Фото из WhatsApp</b>\n👤 <b>От:</b> {{ $json.sender_name }}\n💬 <b>Чат:</b> {{ $json.remoteJid }}\n\n{{ $json.text ? `📝 <b>Описание:</b> ` + $json.text : '' }}",
                    "parse_mode": "HTML"
                }
            },
            "id": "9",
            "name": "TG: Send Photo",
            "type": "n8n-nodes-base.telegram",
            "typeVersion": 1.2,
            "position": [1740, -40]
        },
        {
            "parameters": {
                "operation": "sendVideo",
                "chatId": "YOUR_TG_CHAT_ID",
                "video": "data",
                "additionalFields": {
                    "caption": "=🎬 <b>Видео из WhatsApp</b>\n👤 <b>От:</b> {{ $json.sender_name }}\n💬 <b>Чат:</b> {{ $json.remoteJid }}\n\n{{ $json.text ? `📝 <b>Описание:</b> ` + $json.text : '' }}",
                    "parse_mode": "HTML"
                }
            },
            "id": "10",
            "name": "TG: Send Video",
            "type": "n8n-nodes-base.telegram",
            "typeVersion": 1.2,
            "position": [1740, 60]
        },
        {
            "parameters": {
                "operation": "sendAudio",
                "chatId": "YOUR_TG_CHAT_ID",
                "audio": "data",
                "additionalFields": {
                    "caption": "=🎙 <b>Голосовое/Аудио из WhatsApp</b>\n👤 <b>От:</b> {{ $json.sender_name }}\n💬 <b>Чат:</b> {{ $json.remoteJid }}",
                    "parse_mode": "HTML"
                }
            },
            "id": "11",
            "name": "TG: Send Audio",
            "type": "n8n-nodes-base.telegram",
            "typeVersion": 1.2,
            "position": [1740, 160]
        },
        {
            "parameters": {
                "chatId": "YOUR_TG_CHAT_ID",
                "text": "=💬 <b>Новое сообщение из WhatsApp</b>\n👤 <b>От:</b> {{ $json.sender_name }}\n💬 <b>Чат:</b> {{ $json.remoteJid }}\n\n📝 <b>Текст:</b>\n{{ $json.text }}",
                "additionalFields": {
                    "parse_mode": "HTML"
                }
            },
            "id": "12",
            "name": "TG: Send Text Message",
            "type": "n8n-nodes-base.telegram",
            "typeVersion": 1.2,
            "position": [1060, 260]
        },
        {
            "parameters": {
                "jsCode": """// Обработка вебхука обновления участников группы
const body = $input.first().json.body || {};
const data = body.data || {};
const groupJid = data.id || '';
const action = data.action || '';
const participants = Array.isArray(data.participants) ? data.participants : [];
const author = data.author || '';

const formattedParticipant = participants.map(p => p.split('@')[0]).join(', ');

return [{
  json: {
    event: 'group-participants.update',
    groupJid,
    action,
    participantNumber: formattedParticipant,
    participants,
    authorJid: author,
    authorNumber: author.split('@')[0]
  }
}];"""
            },
            "id": "13",
            "name": "Normalize Group Event",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [420, 420]
        },
        {
            "parameters": {
                "promptType": "define",
                "text": "=У нас новое событие нетворкинга!\nВ группу WhatsApp вступил новый пользователь: +{{ $json.participantNumber }}.\n\nПодготовь короткий дружелюбный драфт приветствия-самопрезентации (Self-Presentation Draft), который мы (админ) можем отправить ему.\nСделай его в стиле нетворкинг-копирайтинга: теплое приветствие, предложение познакомиться, краткое упоминание о том, что в группе собираются ИТ-эксперты и маркетологи, и ненавязчивый вопрос о его проектах.",
                "options": {
                    "systemMessage": "Ты — элитный нетворкинг-ассистент. Твоя задача — генерировать конвертящие, дружелюбные драфты самопрезентаций и приветствий на русском языке."
                }
            },
            "id": "14",
            "name": "Gemini: AI Welcome Pitch",
            "type": "@n8n/n8n-nodes-langchain.agent",
            "typeVersion": 1,
            "position": [620, 420]
        },
        {
            "parameters": {
                "modelName": "models/gemini-1.5-flash",
                "options": {}
            },
            "id": "15",
            "name": "Google Gemini Core",
            "type": "@n8n/n8n-nodes-langchain.lmChatGoogleGemini",
            "typeVersion": 1,
            "position": [620, 600]
        },
        {
            "parameters": {
                "chatId": "YOUR_TG_CHAT_ID",
                "text": "=👥 <b>Обновление состава группы WhatsApp!</b>\n\n📌 <b>Группа:</b> {{ $node[\"Normalize Group Event\"].json[\"groupJid\"] }}\n⚡ <b>Действие:</b> {{ $node[\"Normalize Group Event\"].json[\"action\"] === 'add' ? '➕ Новый участник добавился' : '➖ Участник покинул группу' }}\n👤 <b>Участник:</b> +{{ $node[\"Normalize Group Event\"].json[\"participantNumber\"] }}\n🛡 <b>Инициатор:</b> +{{ $node[\"Normalize Group Event\"].json[\"authorNumber\"] }}\n\n{{ $node[\"Normalize Group Event\"].json[\"action\"] === 'add' ? `🤖 <b>ИИ-Драфт приветствия / самопрезентации:</b>\\n` + $json.output : '' }}",
                "additionalFields": {
                    "parse_mode": "HTML"
                }
            },
            "id": "16",
            "name": "TG: Send Group Notification",
            "type": "n8n-nodes-base.telegram",
            "typeVersion": 1.2,
            "position": [880, 420]
        },
        {
            "parameters": {
                "content": "## Evolution Webhook Router\nСлушает все сообщения и события групп Evolution API.\nПеренаправляет в ветку сообщений или обновлений участников.",
                "height": 180,
                "width": 300
            },
            "id": "s-1",
            "name": "Sticky Webhook Info",
            "type": "n8n-nodes-base.stickyNote",
            "typeVersion": 1,
            "position": [-50, 120]
        },
        {
            "parameters": {
                "content": "## ИИ Копилот & Драфты знакомств\nДля события вступления в группу ИИ-модель Google Gemini мгновенно генерирует драфт самопрезентации для нетворкинга.",
                "height": 180,
                "width": 300
            },
            "id": "s-2",
            "name": "Sticky AI Info",
            "type": "n8n-nodes-base.stickyNote",
            "typeVersion": 1,
            "position": [560, 360]
        }
    ],
    "connections": {
        "Evolution Webhook": {
            "main": [
                [
                    {
                        "node": "Event Router",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Event Router": {
            "main": [
                [
                    {
                        "node": "Normalize Message",
                        "type": "main",
                        "index": 0
                    }
                ],
                [
                    {
                        "node": "Normalize Group Event",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Normalize Message": {
            "main": [
                [
                    {
                        "node": "Ignore Self Messages",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Ignore Self Messages": {
            "main": [
                [
                    {
                        "node": "Has Media?",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Has Media?": {
            "main": [
                [
                    {
                        "node": "Get Media Base64",
                        "type": "main",
                        "index": 0
                    }
                ],
                [
                    {
                        "node": "TG: Send Text Message",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Get Media Base64": {
            "main": [
                [
                    {
                        "node": "Base64 Decode",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Base64 Decode": {
            "main": [
                [
                    {
                        "node": "Switch Media Type",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Switch Media Type": {
            "main": [
                [
                    {
                        "node": "TG: Send Photo",
                        "type": "main",
                        "index": 0
                    }
                ],
                [
                    {
                        "node": "TG: Send Video",
                        "type": "main",
                        "index": 0
                    }
                ],
                [
                    {
                        "node": "TG: Send Audio",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Normalize Group Event": {
            "main": [
                [
                    {
                        "node": "Gemini: AI Welcome Pitch",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Gemini: AI Welcome Pitch": {
            "main": [
                [
                    {
                        "node": "TG: Send Group Notification",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Google Gemini Core": {
            "ai_languageModel": [
                [
                    {
                        "node": "Gemini: AI Welcome Pitch",
                        "type": "ai_languageModel",
                        "index": 0
                    }
                ]
            ]
        }
    },
    "settings": {
        "executionOrder": "v1"
    }
}

# Отправка workflow на n8n инстанцию пользователя
headers = {
    "X-N8N-API-KEY": n8n_api_key,
    "Content-Type": "application/json"
}

# Сначала получим существующие телеграм credentials из n8n, если они есть
# Но так как мы не знаем credentials id, пользователь сможет легко прикрепить свои credentials прямо в UI.
# Добавим в отправку наш workflow
response = requests.post(f"{n8n_url}/api/v1/workflows", json=workflow_data, headers=headers)

if response.status_code in [200, 201]:
    result = response.json()
    print("SUCCESS: Успешно импортирован новый Master Bridge Workflow!")
    print(f"ID воркфлоу: {result.get('id')}")
    print(f"Название: {result.get('name')}")
    print(f"Путь вебхука: {n8n_url}/webhook/evolution-master-bridge")
else:
    print(f"ERROR: Ошибка импорта. Код: {response.status_code}")
    print(response.text)
