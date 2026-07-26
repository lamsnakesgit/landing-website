const fs = require('fs');
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

// The latest operation ID from task-1359 log (we will read it)
const logContent = fs.readFileSync("/Users/higherpower/.gemini/antigravity/brain/2215aa2f-a74e-425c-9810-061da8248ff6/.system_generated/tasks/task-1359.log", "utf8");
const match = logContent.match(/operations\/([a-f0-9\-]+)/i);
const opId = match ? match[1] : null;

async function run() {
  if (!opId) {
    console.error("Could not find operation ID in log.");
    process.exit(1);
  }
  console.log(`Found operation ID: ${opId}`);

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
  const urls = [
    `https://generativelanguage.googleapis.com/v1beta/projects/${project}/locations/us-central1/publishers/google/models/veo-3.1-lite-generate-001/operations/${opId}`,
    `https://generativelanguage.googleapis.com/v1beta/projects/${project}/locations/us-central1/operations/${opId}`,
    `https://generativelanguage.googleapis.com/v1beta/operations/${opId}`
  ];

  for (let i = 0; i < urls.length; i++) {
    const url = urls[i];
    console.log(`\nTesting URL ${i+1}: ${url}`);
    try {
      const res = await fetch(url, {
        headers: { "Authorization": `Bearer ${token}` }
      });
      console.log(`Status: ${res.status}`);
      const text = await res.text();
      console.log(`Snippet: ${text.substring(0, 300)}`);
    } catch (e) {
      console.error(`Error: ${e.message}`);
    }
  }
}

run();
