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

async function generateKeyframe(prompt, filename) {
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
    const outDir = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/scratch/series/pacany_i_ii/03_storyboards/episode_1_dynamic";
    const filePath = path.join(outDir, filename);
    fs.writeFileSync(filePath, buffer);
    console.log(`Saved Keyframe: ${filePath}`);
  } else {
    console.error(`Failed generation for ${filename}:`, JSON.stringify(data));
  }
}

async function run() {
  console.log("Generating Clip 1 Keyframes (Start & End)...");
  await generateKeyframe(
    "Cinematic realism, macro shot, low angle. A polished black leather boot stepping out of a dark Toyota Land Cruiser 200 onto rough gravel. Dust flying. Post-soviet courtyard on the background, dramatic lighting, shot on 35mm lens.",
    "clip1_start.png"
  );
  
  await new Promise(r => setTimeout(r, 12000));
  
  await generateKeyframe(
    "Cinematic realism, macro shot, low angle. A polished black leather boot firmly planted on gravel next to an open black Toyota Land Cruiser 200 door. Dust settling, dramatic lighting, shot on 35mm lens.",
    "clip1_end.png"
  );
}

run().catch(console.error);
