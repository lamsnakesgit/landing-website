const fs = require('fs');

const apiKey = "AIzaSyD5jmzR6scSp-KsRH0ECOjSqLbemAfQWw0";
const opId = "142e929f-fa9f-4d5c-bca4-54140bfda251";
const project = "gen-lang-client-0675220826";

async function run() {
  const endpoints = [
    // 1. Generative Language API with API key (model path)
    `https://generativelanguage.googleapis.com/v1beta/projects/${project}/locations/us-central1/publishers/google/models/veo-3.1-lite-generate-001/operations/${opId}?key=${apiKey}`,
    // 2. Generative Language API with API key (short path)
    `https://generativelanguage.googleapis.com/v1beta/projects/${project}/locations/us-central1/operations/${opId}?key=${apiKey}`,
    // 3. Generative Language API (root operations path)
    `https://generativelanguage.googleapis.com/v1beta/operations/${opId}?key=${apiKey}`,
    // 4. Generative Language API with full path
    `https://generativelanguage.googleapis.com/v1beta/projects/${project}/locations/us-central1/publishers/google/models/veo-3.1-lite-generate-001/operations/${opId}?key=${apiKey}`
  ];

  for (let i = 0; i < endpoints.length; i++) {
    const url = endpoints[i];
    console.log(`\nTesting URL ${i+1}: ${url}`);
    try {
      const res = await fetch(url);
      console.log(`Status: ${res.status}`);
      const text = await res.text();
      console.log(`Snippet: ${text.substring(0, 500)}`);
    } catch (e) {
      console.error(`Error: ${e.message}`);
    }
  }
}

run();
