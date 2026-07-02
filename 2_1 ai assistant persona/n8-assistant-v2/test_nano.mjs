import { GoogleAuth } from 'google-auth-library';
import fs from 'fs';

async function test() {
  try {
    const credsJson = process.env.GOOGLE_APPLICATION_CREDENTIALS_JSON;
    if (!credsJson) throw new Error("Missing creds");
    const credentials = JSON.parse(credsJson);
    const auth = new GoogleAuth({
      credentials,
      scopes: ['https://www.googleapis.com/auth/cloud-platform']
    });
    const client = await auth.getClient();
    const token = await client.getAccessToken();
    
    const projectId = credentials.project_id;
    const location = 'us-central1';
    
    console.log("Token acquired, calling Vertex AI...");
    
    const response = await fetch(
      `https://${location}-aiplatform.googleapis.com/v1/projects/${projectId}/locations/${location}/publishers/google/models/gemini-3.1-flash-image:generateContent`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token.token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          contents: [{
            role: "user",
            parts: [{ text: "A beautiful futuristic city with neon lights at night." }]
          }],
          generationConfig: {
            responseModalities: ["IMAGE"],
            aspectRatio: "1:1"
          }
        })
      }
    );
    
    if (!response.ok) {
      const err = await response.text();
      console.error("Error from Vertex AI:", err);
      process.exit(1);
    }
    
    const data = await response.json();
    if (data.candidates && data.candidates[0].content.parts[0].inlineData) {
      console.log("Success! Received base64 image data.");
    } else {
      console.log("Response format unexpected:", JSON.stringify(data).substring(0, 500));
    }
  } catch (err) {
    console.error(err);
  }
}

test();
