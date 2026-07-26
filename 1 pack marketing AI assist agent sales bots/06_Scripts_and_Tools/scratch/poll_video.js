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

const opName = "projects/gen-lang-client-0675220826/locations/us-central1/publishers/google/models/veo-3.1-lite-generate-001/operations/6782d250-f6cf-43f1-9e86-63a32c2f388e";

async function poll() {
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

  const url = `https://us-central1-aiplatform.googleapis.com/v1/${opName}`;
  console.log("Checking operation status...");
  
  const response = await fetch(url, {
    headers: { "Authorization": `Bearer ${token}` }
  });
  const data = await response.json();
  
  if (data.done) {
    if (data.error) {
      console.error("Operation failed:", JSON.stringify(data.error));
      process.exit(1);
    }
    if (data.response && data.response.videos && data.response.videos[0]) {
      const b64 = data.response.videos[0].bytesBase64Encoded;
      const buffer = Buffer.from(b64, 'base64');
      const outDir = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/scratch/series/pacany_i_ii/04_renders";
      if (!fs.existsSync(outDir)) {
        fs.mkdirSync(outDir, { recursive: true });
      }
      const filePath = path.join(outDir, "clip1_dynamic_sound.mp4");
      fs.writeFileSync(filePath, buffer);
      console.log(`Video saved successfully with audio: ${filePath}`);
      process.exit(0);
    } else {
      console.log("No video in response:", JSON.stringify(data));
      process.exit(1);
    }
  } else {
    console.log("Operation still in progress...");
  }
}

poll().catch(console.error);
