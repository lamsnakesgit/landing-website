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

// Load Start and End images in base64
const imgStart = fs.readFileSync("/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/scratch/series/pacany_i_ii/03_storyboards/episode_1_fixed/clip1_start.png").toString("base64");
const imgEnd = fs.readFileSync("/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/scratch/series/pacany_i_ii/03_storyboards/episode_1_fixed/clip1_end.png").toString("base64");

async function run() {
  console.log("Acquiring access token...");
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
  const url = `https://us-central1-aiplatform.googleapis.com/v1/projects/${project}/locations/us-central1/publishers/google/models/veo-3.1-lite-generate-001:predictLongRunning`;

  const body = {
    instances: [
      {
        prompt: "Cinematic realism, close-up, low angle. A polished black leather boot stepping out of a dark Land Cruiser door onto gravel. The video must start exactly like the start reference image and end exactly like the end reference image. Realistic camera motion.",
        imageInput: {
          bytesBase64Encoded: imgStart
        },
        imageInputEnd: {
          bytesBase64Encoded: imgEnd
        }
      }
    ],
    parameters: {
      aspectRatio: "9:16",
      durationSeconds: 5,
      generateAudio: true,
      audioPrompt: "Loud sound of gravel crunching under a heavy boot, car door open chime, low threatening synthesizer rumble."
    }
  };

  console.log("Sending video request to Vertex AI Veo 3.1 Lite...");
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify(body)
  });

  const data = await response.json();
  console.log("Response:", JSON.stringify(data));

  if (!data.name) {
    console.error("No operation name in response.");
    process.exit(1);
  }

  const opName = data.name;
  console.log(`\nOperation started: ${opName}`);

  // We check using v1beta1 version of URL
  // Format of opName: projects/{project}/locations/{location}/publishers/google/models/{model}/operations/{opId}
  const pollUrl = `https://us-central1-aiplatform.googleapis.com/v1beta1/${opName}`;
  console.log(`Polling URL: ${pollUrl}`);

  while (true) {
    console.log(`\nChecking status at ${new Date().toLocaleTimeString()}...`);
    try {
      const pollRes = await fetch(pollUrl, {
        headers: { "Authorization": `Bearer ${token}` }
      });
      console.log("Status:", pollRes.status);
      if (pollRes.status === 200) {
        const pollData = await pollRes.json();
        if (pollData.done) {
          if (pollData.error) {
            console.error("Operation failed:", JSON.stringify(pollData.error));
            process.exit(1);
          }
          if (pollData.response && pollData.response.videos && pollData.response.videos[0]) {
            const b64 = pollData.response.videos[0].bytesBase64Encoded;
            const buffer = Buffer.from(b64, 'base64');
            const outDir = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/scratch/series/pacany_i_ii/04_renders";
            if (!fs.existsSync(outDir)) {
              fs.mkdirSync(outDir, { recursive: true });
            }
            const filePath = path.join(outDir, "clip1_dynamic_sound.mp4");
            fs.writeFileSync(filePath, buffer);
            console.log(`\nSUCCESS! Saved video to: ${filePath}`);
            process.exit(0);
          } else {
            console.error("No video in response:", JSON.stringify(pollData));
            process.exit(1);
          }
        } else {
          const progress = pollData.metadata && pollData.metadata.progressPercent !== undefined ? pollData.metadata.progressPercent : "unknown";
          console.log(`Operation in progress... Progress: ${progress}%`);
        }
      } else {
        const errText = await pollRes.text();
        console.error("Polling error response:", errText);
      }
    } catch (e) {
      console.error("Error during polling:", e.message);
    }
    // Wait 15 seconds before next poll
    await new Promise(r => setTimeout(r, 15000));
  }
}

run().catch(console.error);
