const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const keyFile = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/2 accounts sub security/amocrm_wazzup_analytics/google_service_account.json";
const credentials = JSON.parse(fs.readFileSync(keyFile, 'utf8'));

const iat = Math.floor(Date.now() / 1000);
const exp = iat + 3600;

const header = {
  alg: "RS256",
  typ: "JWT"
};

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
  console.log(`Generating: ${filename}...`);
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
    const outDir = path.join(__dirname, 'output_images');
    if (!fs.existsSync(outDir)) {
      fs.mkdirSync(outDir);
    }
    const filePath = path.join(outDir, filename);
    fs.writeFileSync(filePath, buffer);
    console.log(`Saved: ${filePath}`);
  } else {
    console.error(`Failed generation for ${filename}:`, JSON.stringify(data));
  }
}

async function run() {
  // Сцена 1: Баке выходит из машины (Фотореализм)
  await generateImage(
    "Cinematic realism, high-end commercial style, photorealistic. A tough Kazakh man (Bake) with a buzz cut, wearing a black leather jacket, steps out of a dark Toyota Land Cruiser 200. He points his finger aggressively straight at the camera. Soviet-style apartment buildings in Almaty in the background. Low angle, dramatic action movie lighting, shot on 35mm lens.",
    "scene1_bake_ref.png"
  );

  // Сцена 2: Мансур за ноутом с n8n (Фотореализм)
  await generateImage(
    "Cinematic realism, high-end commercial style, photorealistic. A young IT developer (Mansur) wearing a gray hoodie and glasses, sitting in a dark room. His face is lit by the blue and green neon glow of a laptop screen. On the laptop lid, there is a visible Telegram logo sticker with text '@nnsvt' and an Instagram logo sticker with text '@lamanopro_'. On the laptop screen, a complex node graph with glowing connections is shown. Cinematic lighting, cyberpunk vibes, shot on 35mm lens.",
    "scene2_mansur_ref.png"
  );

  // Сцена 3: Экран телефона с Kaspi и СМС (Фотореализм)
  await generateImage(
    "Cinematic realism, high-end commercial style, photorealistic. A modern smartphone lying on a wooden table in a dark room. The screen is brightly lit, showing a push notification on Russian language with clear text: 'Kaspi: Пополнение +1,500,000 ₸'. Instantly, a Telegram notification pops up below it from sender 'Баке' with text: 'Мансик, твой бот выбил долг! Но наш сервер взломали...'. High detail text rendering, micro-lens focus, shot on 35mm lens.",
    "scene3_phone_ref.png"
  );
}

run().catch(console.error);
