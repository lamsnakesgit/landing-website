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
    const outDir = path.join(__dirname, 'version_cinematic', 'keyframes');
    if (!fs.existsSync(outDir)) {
      fs.mkdirSync(outDir, { recursive: true });
    }
    const filePath = path.join(outDir, filename);
    fs.writeFileSync(filePath, buffer);
    console.log(`Saved Keyframe: ${filePath}`);
  } else {
    console.error(`Failed generation for ${filename}:`, JSON.stringify(data));
  }
}

async function run() {
  console.log("Starting Keyframe Generation Pipeline...");

  // --- КЛИП 1 (Сцена 1: Баке выходит из машины) ---
  console.log("Generating Clip 1 Keyframes...");
  // Старт: Баке открывает дверь джипа
  await generateImage(
    "Cinematic realism, photorealistic. A tough Kazakh man (Bake) with a buzz cut, wearing a black leather jacket, opening the door of a dark Toyota Land Cruiser 200 in a post-soviet courtyard in Almaty. Overcast moody lighting, shot on 35mm lens.",
    "clip1_start.png"
  );
  // Конец: Баке стоит перед камерой и тычет пальцем
  await generateImage(
    "Cinematic realism, photorealistic. A tough Kazakh man (Bake) with a buzz cut, wearing a black leather jacket, standing in a post-soviet courtyard in Almaty, pointing his finger aggressively straight at the camera. Overcast lighting, low angle shot on 35mm lens.",
    "clip1_end.png"
  );

  // --- КЛИП 2 (Сцена 1 -> Сцена 2: Переход к Мансуру) ---
  console.log("Generating Clip 2 Keyframes...");
  // Старт: Мансур испуганно смотрит на Баке во дворе
  await generateImage(
    "Cinematic realism, photorealistic. A young Kazakh developer (Mansur) in a gray hoodie and glasses, looking scared, standing in a post-soviet courtyard in Almaty under overcast sky. Shot on 35mm lens.",
    "clip2_start.png"
  );
  // Конец: Мансур и Баке заходят в темный гараж-офис
  await generateImage(
    "Cinematic realism, photorealistic. A young developer (Mansur) in a gray hoodie opening the door to a dark garage-office with neon blue and green lighting inside. A tough man in a leather jacket stands behind him. Cybertech atmosphere.",
    "clip2_end.png"
  );

  // --- КЛИП 3 (Сцена 2: Настройка n8n) ---
  console.log("Generating Clip 3 Keyframes...");
  // Старт: Мансур садится за ноутбук
  await generateImage(
    "Cinematic realism, photorealistic. A young IT developer (Mansur) sitting down in front of a laptop in a dark garage-office, neon green and blue lighting reflecting on his face and glasses. Cinematic shot on 35mm lens.",
    "clip3_start.png"
  );
  // Конец: Мансур показывает Баке настроенный n8n на экране
  await generateImage(
    "Cinematic realism, photorealistic. A young developer (Mansur) pointing at a glowing laptop screen displaying a complex node graph. A tough man in a leather jacket stands next to him, looking at the screen with curiosity. Neon lighting.",
    "clip3_end.png"
  );

  // --- КЛИП 4 (Сцена 3: Запуск и Саспенс) ---
  console.log("Generating Clip 4 Keyframes...");
  // Старт: Палец Мансура завис над кнопкой Enter
  await generateImage(
    "Cinematic realism, macro close-up. An IT developer's finger hovering just above the 'Enter' key on a mechanical keyboard in a dark room. Neon green light reflection on the finger, extremely detailed.",
    "clip4_start.png"
  );
  // Конец: Палец нажимает Enter, экран вспыхивает зеленым
  await generateImage(
    "Cinematic realism, macro close-up. An IT developer's finger firmly pressing down the 'Enter' key on a mechanical keyboard, a bright green light glow emitting from the screen off-camera. Detailed textures.",
    "clip4_end.png"
  );
}

run().catch(console.error);
