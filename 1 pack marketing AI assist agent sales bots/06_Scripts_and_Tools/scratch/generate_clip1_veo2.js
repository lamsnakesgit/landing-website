const fs = require('fs');
const path = require('path');

const apiKey = "AIzaSyD5jmzR6scSp-KsRH0ECOjSqLbemAfQWw0";
const model = "veo-2.0-generate-001";

// Load Start and End images in base64
const imgStart = fs.readFileSync("/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/scratch/series/pacany_i_ii/03_storyboards/episode_1_fixed/clip1_start.png").toString("base64");
const imgEnd = fs.readFileSync("/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/scratch/series/pacany_i_ii/03_storyboards/episode_1_fixed/clip1_end.png").toString("base64");

async function run() {
  const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:predictLongRunning?key=${apiKey}`;

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

  console.log("Sending video request to Generative Language Veo 2.0...");
  const response = await fetch(url, {
    method: "POST",
    headers: {
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

  const pollUrl = `https://generativelanguage.googleapis.com/v1beta/${opName}?key=${apiKey}`;
  console.log(`Polling URL: ${pollUrl}`);

  while (true) {
    console.log(`\nChecking status at ${new Date().toLocaleTimeString()}...`);
    try {
      const pollRes = await fetch(pollUrl);
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
