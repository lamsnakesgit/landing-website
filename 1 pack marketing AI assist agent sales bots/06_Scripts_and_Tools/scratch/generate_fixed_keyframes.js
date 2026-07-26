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

// Загружаем наши эталонные лица в base64
const bakeRefB64 = fs.readFileSync("/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/scratch/series/pacany_i_ii/02_dna_bible/bake_ref.png").toString("base64");
const mansurRefB64 = fs.readFileSync("/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/scratch/series/pacany_i_ii/02_dna_bible/mansur_ref.png").toString("base64");

async function generateFixedImage(prompt, filename, refB64) {
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
  const url = `https://us-central1-aiplatform.googleapis.com/v1/projects/${project}/locations/us-central1/publishers/google/models/imagen-3.0-capability-001:predict`;

  const body = {
    instances: [{
      prompt: prompt,
      referenceImages: [
        {
          referenceType: "REFERENCE_TYPE_RAW",
          referenceId: 1,
          referenceImage: {
            bytesBase64Encoded: refB64
          }
        }
      ]
    }],
    parameters: {
      aspectRatio: "9:16",
      sampleCount: 1
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
    const outDir = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/scratch/series/pacany_i_ii/03_storyboards/episode_1_fixed";
    const filePath = path.join(outDir, filename);
    fs.writeFileSync(filePath, buffer);
    console.log(`Saved Fixed Keyframe: ${filePath}`);
  } else {
    console.error(`Failed fixed generation for ${filename}:`, JSON.stringify(data));
  }
}

async function run() {
  console.log("Starting Fixed Keyframe Generation Loop (with Face References)...");

  // Перегенерируем clip2_start с референсом лица Мансура
  console.log("Generating clip2_start (scared Mansur)...");
  await generateFixedImage(
    "Cinematic realism, photorealistic. A young Kazakh developer in a gray hoodie and glasses, looking scared, standing in a post-soviet courtyard in Almaty under overcast sky. The face must match the reference image exactly. Shot on 35mm lens.",
    "clip2_start.png",
    mansurRefB64
  );

  console.log("Waiting 12s...");
  await new Promise(r => setTimeout(r, 12000));

  // Перегенерируем clip2_end с референсом Баке
  console.log("Generating clip2_end (Mansur and Bake entering garage)...");
  await generateFixedImage(
    "Cinematic realism, photorealistic. A young developer in a gray hoodie opening the door to a dark garage-office with neon blue and green lighting inside. A tough man in a leather jacket stands behind him. The tough man's face must match the reference image exactly.",
    "clip2_end.png",
    bakeRefB64
  );

  console.log("Waiting 12s...");
  await new Promise(r => setTimeout(r, 12000));

  // Перегенерируем clip3_start с референсом лица Мансура
  console.log("Generating clip3_start (Mansur sitting at laptop)...");
  await generateFixedImage(
    "Cinematic realism, photorealistic. A young IT developer sitting down in front of a laptop in a dark garage-office, neon green and blue lighting reflecting on his face and glasses. The face must match the reference image exactly. Cinematic shot on 35mm lens.",
    "clip3_start.png",
    mansurRefB64
  );
}

run().catch(console.error);
