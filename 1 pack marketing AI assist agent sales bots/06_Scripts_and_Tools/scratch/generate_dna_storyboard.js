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

// Загружаем различные ракурсы из Библии ДНК
const biblePath = "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/scratch/series/pacany_i_ii/02_dna_bible";
const bakeFront = fs.readFileSync(path.join(biblePath, "bake", "front.png")).toString("base64");
const bake34 = fs.readFileSync(path.join(biblePath, "bake", "three_quarters.png")).toString("base64");

const mansurFront = fs.readFileSync(path.join(biblePath, "mansur", "front.png")).toString("base64");
const mansurProfile = fs.readFileSync(path.join(biblePath, "mansur", "profile.png")).toString("base64");
const mansurScared = fs.readFileSync(path.join(biblePath, "mansur", "scared.png")).toString("base64");

async function generateKeyframe(prompt, filename, refB64 = null) {
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
  const model = refB64 ? "imagen-3.0-capability-001" : "imagen-3.0-generate-002";
  const url = `https://us-central1-aiplatform.googleapis.com/v1/projects/${project}/locations/us-central1/publishers/google/models/${model}:predict`;

  const instance = { prompt: prompt };
  if (refB64) {
    instance.referenceImages = [
      {
        referenceType: "REFERENCE_TYPE_RAW",
        referenceId: 1,
        referenceImage: {
          bytesBase64Encoded: refB64
        }
      }
    ];
  }

  const body = {
    instances: [instance],
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
  console.log("Starting full 1-minute keyframe production loop with multi-angle DNA...");

  const delay = () => new Promise(r => setTimeout(r, 12000));

  // --- КЛИП 1 ---
  console.log("Clip 1/7...");
  await generateKeyframe(
    "Cinematic realism, photorealistic. A tough Kazakh man (Bake) with a buzz cut, wearing a black leather jacket, opening the door of a dark Toyota Land Cruiser 200 in a post-soviet courtyard in Almaty. Overcast lighting, shot on 35mm lens. Face matches reference exactly.",
    "clip1_start.png",
    bake34 // в полуоборот
  );
  await delay();
  await generateKeyframe(
    "Cinematic realism, photorealistic. A tough Kazakh man (Bake) with a buzz cut, wearing a black leather jacket, standing in a post-soviet courtyard in Almaty, pointing his finger aggressively straight at the camera. Overcast lighting, low angle shot on 35mm lens. Face matches reference exactly.",
    "clip1_end.png",
    bakeFront // анфас
  );
  await delay();

  // --- КЛИП 2 ---
  console.log("Clip 2/7...");
  await generateKeyframe(
    "Cinematic realism, photorealistic. A young Kazakh developer in a gray hoodie and glasses, looking scared, standing in a post-soviet courtyard in Almaty under overcast sky. Face matches reference exactly. Shot on 35mm lens.",
    "clip2_start.png",
    mansurScared // испуганный ракурс
  );
  await delay();
  await generateKeyframe(
    "Cinematic realism, photorealistic. A young developer in a gray hoodie opening the door to a dark garage-office with neon blue and green lighting inside. A tough man in a leather jacket stands behind him. The young developer's face matches reference exactly. The tough man's face matches reference exactly.",
    "clip2_end.png",
    mansurProfile // вид сбоку
  );
  await delay();

  // --- КЛИП 3 ---
  console.log("Clip 3/7...");
  await generateKeyframe(
    "Cinematic realism, photorealistic. A young IT developer sitting down in front of a laptop in a dark garage-office, neon green and blue lighting reflecting on his face and glasses. Face matches reference exactly. Cinematic shot on 35mm lens.",
    "clip3_start.png",
    mansurProfile // вид сбоку за столом
  );
  await delay();
  await generateKeyframe(
    "Cinematic realism, photorealistic. A young developer pointing at a glowing laptop screen displaying a complex node graph. A tough man in a leather jacket stands next to him, looking at the screen with curiosity. Neon lighting. Faces match references exactly.",
    "clip3_end.png",
    mansurFront // анфас
  );
  await delay();

  // --- КЛИП 4 ---
  console.log("Clip 4/7...");
  await generateKeyframe(
    "Cinematic realism, macro close-up. An IT developer's finger hovering just above the 'Enter' key on a mechanical keyboard in a dark room. Neon green light reflection on the finger, extremely detailed.",
    "clip4_start.png"
  );
  await delay();
  await generateKeyframe(
    "Cinematic realism, macro close-up. An IT developer's finger firmly pressing down the 'Enter' key on a mechanical keyboard, a bright green light glow emitting from the screen off-camera. Detailed textures.",
    "clip4_end.png"
  );
  await delay();

  // --- КЛИП 5 ---
  console.log("Clip 5/7...");
  await generateKeyframe(
    "Cinematic realism, photorealistic. A modern smartphone lying on a wooden table in a dark room. The screen is blank but brightly lit with a clean gradient wallpaper. No text. High detail, macro-lens focus, shot on 35mm lens.",
    "clip5_start.png"
  );
  await delay();
  // Копируем готовый пуш
  console.log("Copying final mockup screen to clip5_end.png...");
  fs.copyFileSync(
    "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/scratch/version_cinematic/scene3_phone_final.png",
    "/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/scratch/series/pacany_i_ii/03_storyboards/episode_1_fixed/clip5_end.png"
  );

  // --- КЛИП 6 ---
  console.log("Clip 6/7...");
  await generateKeyframe(
    "Cinematic realism, photorealistic. A close-up of a young developer in a gray hoodie and glasses, holding a smartphone, his face instantly turning pale and terrified in a dark neon-lit room. Face matches reference exactly.",
    "clip6_start.png",
    mansurScared
  );
  await delay();
  await generateKeyframe(
    "Cinematic realism, photorealistic. A young developer in a gray hoodie and glasses, panic-stricken, typing furiously on a glowing mechanical keyboard in a dark room with red emergency lighting. Face matches reference exactly.",
    "clip6_end.png",
    mansurScared
  );
  await delay();

  // --- КЛИП 7 ---
  console.log("Clip 7/7...");
  await generateKeyframe(
    "Cinematic realism. Red error messages 'ACCESS DENIED' flashing on a computer monitor, reflecting on a panicked developer's glasses. Fast zoom out, close-up shot.",
    "clip7_start.png"
  );
  await delay();
  await generateKeyframe(
    "A clean solid pitch black screen, no objects, no lights.",
    "clip7_end.png"
  );

  console.log("All keyframes generated with multi-angle DNA!");
}

run().catch(console.error);
