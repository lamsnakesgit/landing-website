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

async function generateDnaReference(prompt, subfolder, filename) {
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
      aspectRatio: "1:1", // для эталонных портретов используем квадрат
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
    const outDir = path.join("/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/scratch/series/pacany_i_ii/02_dna_bible", subfolder);
    const filePath = path.join(outDir, filename);
    fs.writeFileSync(filePath, buffer);
    console.log(`Saved DNA Reference: ${filePath}`);
  } else {
    console.error(`Failed DNA generation for ${filename}:`, JSON.stringify(data));
  }
}

async function run() {
  console.log("Generating Multi-Angle Character DNA Sheets...");
  const delay = () => new Promise(r => setTimeout(r, 12000));

  // --- МАНСУР ---
  console.log("Generating Mansur DNA...");
  // 1. Анфас
  await generateDnaReference(
    "Cinematic realism, close-up portrait, front view. A 25-year-old Kazakh IT developer (Mansur) with glasses and short black hair, wearing a gray hoodie. Dark room, neutral background, cinematic studio lighting.",
    "mansur",
    "front.png"
  );
  await delay();
  // 2. Профиль (сбоку)
  await generateDnaReference(
    "Cinematic realism, close-up portrait, side profile view. A 25-year-old Kazakh IT developer (Mansur) with glasses and short black hair, wearing a gray hoodie. Dark room, neutral background, cinematic studio lighting.",
    "mansur",
    "profile.png"
  );
  await delay();
  // 3. Эмоция страха / удивления
  await generateDnaReference(
    "Cinematic realism, close-up portrait, front view, worried expression. A 25-year-old Kazakh IT developer (Mansur) with glasses and short black hair, wearing a gray hoodie, looking scared and shocked. Dark room, cinematic studio lighting.",
    "mansur",
    "scared.png"
  );
  await delay();

  // --- БАКЕ ---
  console.log("Generating Bake DNA...");
  // 1. Анфас
  await generateDnaReference(
    "Cinematic realism, close-up portrait, front view. A tough 35-year-old Kazakh man (Bake) with a buzz cut, buzz cut hairstyle, wearing a black leather jacket. Severe look. Neutral background, cinematic lighting.",
    "bake",
    "front.png"
  );
  await delay();
  // 2. В полуоборот (3/4)
  await generateDnaReference(
    "Cinematic realism, close-up portrait, three-quarters view. A tough 35-year-old Kazakh man (Bake) with a buzz cut, buzz cut hairstyle, wearing a black leather jacket. Severe look. Neutral background, cinematic lighting.",
    "bake",
    "three_quarters.png"
  );

  console.log("DNA Bible generation complete!");
}

run().catch(console.error);
