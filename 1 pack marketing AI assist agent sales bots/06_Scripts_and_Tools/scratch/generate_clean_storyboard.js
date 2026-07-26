const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const keyFile = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/2 accounts sub security/amocrm_wazzup_analytics/google_service_account.json";
const credentials = JSON.parse(fs.readFileSync(keyFile, 'utf8'));

const iat = Math.floor(Date.now() / 1000);
const exp = iat + 3600;

const header = { alg: "RS256", typ: "JWT" };
const payload = {
  iss: credentials.client_email,
  scope: "https://www.googleapis.com/auth/cloud-platform",
  aud: "https://oauth2.googleapis.com/token",
  exp: exp,
  iat: iat
};

function base64url(obj) {
  return Buffer.from(JSON.stringify(obj))
    .toString('base64')
    .replace(/=/g, '')
    .replace(/\+/g, '-')
    .replace(/\//g, '_');
}

const tokenInput = `${base64url(header)}.${base64url(payload)}`;
const sign = crypto.createSign('RSA-SHA256');
sign.update(tokenInput);
const signature = sign.sign(credentials.private_key, 'base64')
  .replace(/=/g, '')
  .replace(/\+/g, '-')
  .replace(/\//g, '_');

const jwt = `${tokenInput}.${signature}`;

async function generateImage(prompt, filename) {
  const tokenRes = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      grant_type: "urn:ietf:params:oauth:grant-type:jwt-bearer",
      assertion: jwt
    })
  });
  const tokenData = await tokenRes.json();
  const token = tokenData.access_token;

  const project = credentials.project_id;
  const url = `https://us-central1-aiplatform.googleapis.com/v1/projects/${project}/locations/us-central1/publishers/google/models/imagen-3.0-generate-002:predict`;

  const body = {
    instances: [{ prompt: prompt }],
    parameters: {
      aspectRatio: "9:16",
      numberOfImages: 1,
      outputMimeType: "image/png"
    }
  };

  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify(body)
  });

  const data = await response.json();
  if (data.predictions && data.predictions[0]) {
    const base64Image = data.predictions[0].bytesBase64Encoded;
    const buffer = Buffer.from(base64Image, 'base64');
    const outDir = path.join(__dirname, 'version_cinematic');
    if (!fs.existsSync(outDir)) {
      fs.mkdirSync(outDir);
    }
    const filePath = path.join(outDir, filename);
    fs.writeFileSync(filePath, buffer);
    console.log(`Saved clean image: ${filePath}`);
  } else {
    console.error(`Failed generation for ${filename}:`, JSON.stringify(data));
  }
}

async function run() {
  console.log("Generating Scene 2 (Clean Mansur for laptop overlays)...");
  // Чистый ноутбук без текста (наложим стикеры программно)
  await generateImage(
    "Cinematic realism, high-end commercial style, photorealistic. A young Kazakh IT developer (Mansur) wearing a gray hoodie and glasses, sitting in a dark room. His face is lit by the blue and green neon glow of a clean laptop screen. The laptop lid is visible and clean without any text. On the laptop screen, a complex node graph with glowing connections is shown. Cinematic lighting, cyberpunk vibes, shot on 35mm lens.",
    "scene2_mansur_clean.png"
  );

  console.log("Generating Scene 3 (Clean Phone for SMS overlays)...");
  // Чистый телефон без текста (наложим Kaspi и СМС программно)
  await generateImage(
    "Cinematic realism, high-end commercial style, photorealistic. A modern smartphone lying on a wooden table in a dark room. The screen is blank but brightly lit with a clean green-blue gradient wallpaper. No text or icons on the screen. High detail, macro-lens focus, shot on 35mm lens.",
    "scene3_phone_clean.png"
  );
}

run().catch(console.error);
