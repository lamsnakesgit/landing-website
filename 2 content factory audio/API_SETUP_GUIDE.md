# Content Factory: API Configuration & Setup Guide

To get your automated video factory running, you need to configure the following API keys in your n8n credentials.

## 1. OpenAI (GPT-4o)
*   **Purpose:** Script generation and scene descriptions.
*   **Where to get:** [platform.openai.com](https://platform.openai.com/)
*   **n8n Node:** `OpenAI`
*   **Setup:** Create a new "OpenAI API" credential in n8n and paste your Secret Key.

## 2. Google Vertex AI (Imagen 3 & TTS) - Native HTTP Setup
*   **Purpose:** High-quality image generation and Studio-grade voiceovers using your $300 credit.
*   **Where to get:** [console.cloud.google.com](https://console.cloud.google.com/)
*   **n8n Nodes:** `HTTP Request` (Native). This avoids "question mark" errors in older n8n versions.
*   **Setup:** 
    1. **Enable APIs:** Search for "Vertex AI API" and "Cloud Text-to-Speech API" and enable them.
    2. **Service Account:** Go to "IAM & Admin" > "Service Accounts". Create one named `n8n-video-factory`.
    3. **Roles:** Assign `Vertex AI User` and `Cloud Text-to-Speech User`.
    4. **JSON Key:** Click on the service account > "Keys" > "Add Key" > "Create new key" (JSON).
    5. **n8n Credential:** In n8n, create a "Google Cloud Service Account" credential and paste the JSON content.
    6. **Project ID:** Copy your Project ID from the Google Cloud Console and paste it into the `Config: Google Cloud` node in n8n.
*   **Free Tier Tip:** Imagen 3 is very cost-effective on the trial. For TTS, use `en-US-Studio-O` or `en-US-Neural2-F` for the most realistic "human" sound without extra costs.

## 3. FFmpeg (Local Installation)
*   **Purpose:** Stitching images, audio, and music into the final video.
*   **Requirement:** FFmpeg must be installed on the machine running n8n (or inside the Docker container).
*   **Verification:** Run `ffmpeg -version` in your terminal to check.
*   **n8n Node:** `Execute Command`.
*   **Troubleshooting:** If you see "Unrecognized node type", ensure `N8N_BLOCK_NODES` is not blocking `executeCommand` in your environment variables.

## 4. Workflow Variables
When triggering the workflow manually, provide the following JSON input:
```json
{
  "niche": "kamchatka", 
  "format": "shorts",
  "image_prompt": "Cinematic volcano eruption at night, 8k, realistic"
}
```
*(Change "niche" to "ai_agents" and "format" to "long" as needed)*

## 5. File Paths
The FFmpeg nodes expect files named `image.png`, `audio.mp3`, and `music.mp3` in the n8n working directory. You can use the `Write Binary File` node before the FFmpeg nodes to save the AI-generated assets with these names.
