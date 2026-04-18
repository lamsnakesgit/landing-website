# n8n AI Assistant / Agent Debug Guide

## Goal

Quickly find why an n8n Telegram AI assistant or AI agent:
- leaks reasoning/debug text,
- answers in the wrong format,
- mixes system/internal text into user replies,
- behaves differently after Gemini/provider updates.

## 1. Main rule

Always debug the flow in this order:

1. **Input**: what exactly enters the LLM node.
2. **Raw LLM output**: full JSON returned by the provider.
3. **Transform step**: Code / Set / Function node after the LLM.
4. **Final Telegram payload**: exact field sent to the user.

If you skip step 2, you can easily debug the wrong place.

## 2. Typical reasons for broken assistant output

### A. Wrong field is sent to Telegram

Most common issue.

Examples of mistakes:
- sending the whole `$json`,
- sending `JSON.stringify(response)`,
- sending a full provider object instead of final text,
- concatenating `content + reasoning + debug`.

### B. Provider response format changed

Gemini/OpenRouter/AI nodes can change JSON structure after updates.

What worked before:
- `text`

What may appear now:
- `content.parts[]`
- `candidates[]`
- `message.content`
- `reasoning`
- `analysis`
- `thoughts`
- metadata/debug fields

### C. Prompt asks for visible reasoning

Bad prompt fragments:
- `think step by step`
- `show your reasoning`
- `explain your internal thought process`

Use output instructions instead:
- `Provide only the final answer.`
- `Do not reveal internal reasoning.`

### D. Code node merges internal fields

Typical bug:

```javascript
return [{
  text: $json.content + '\n' + $json.reasoning
}];
```

### E. Debug/log text is accidentally forwarded

Sometimes logs are appended to final output while testing.

## 3. Best debugging workflow in n8n

## Step 1 — Freeze one test input

Use one stable Telegram message, for example:

```text
Write a short answer: what is the capital of France?
```

Do not debug with changing prompts first.

## Step 2 — Inspect raw LLM output

Open the LLM node execution and inspect the raw JSON.

Look for:
- where the final user-visible text actually lives,
- whether reasoning/internal fields are present,
- whether tool output or metadata is mixed into the response.

## Step 3 — Add a temporary Code node after the LLM

Use a minimal debug node.

```javascript
return [{
  raw: $json
}];
```

This helps you inspect what the next node really receives.

## Step 4 — Create one explicit final field

After you identify the correct path, normalize it into one field only.

Example:

```javascript
return [{
  final_text: $json.text
}];
```

Or for nested output:

```javascript
return [{
  final_text: $json.message?.content || $json.text || ''
}];
```

Then Telegram must send only `final_text`.

## Step 5 — Verify Telegram node payload

In the Telegram node, send only something like:

```text
{{$json.final_text}}
```

Not:
- `{{$json}}`
- `{{JSON.stringify($json)}}`
- mixed objects

## 4. Safe normalization pattern

If provider format is unstable, add a dedicated normalization Code node.

```javascript
const data = $json;

const finalText =
  data.final_text ||
  data.text ||
  data.message?.content ||
  data.content ||
  data.candidates?.[0]?.content?.parts?.map(p => p.text).join(' ') ||
  '';

return [{
  final_text: String(finalText).trim()
}];
```

Then keep Telegram output isolated from provider-specific fields.

## 5. Gemini-specific debugging notes

When Gemini starts acting differently, check these first:

1. **Model changed**
   - example: previous model returned plain text,
   - new model returns candidates/parts/reasoning blocks.

2. **Endpoint changed**
   - Google direct API,
   - OpenRouter,
   - proxy/compatible endpoint,
   - n8n built-in AI node.

3. **Response schema changed**
   - especially after provider or node updates.

4. **Reasoning-enabled mode appeared**
   - even if your workflow was untouched.

## 6. What to log during debugging

For each broken run, capture:
- input message,
- model name,
- node name,
- raw response JSON,
- normalized `final_text`,
- final Telegram payload.

Without these 5 points, debugging is slow and random.

## 7. Minimal code-side debugging checklist

If you debug outside n8n too:

1. Print the full raw provider response once.
2. Print the extracted final text separately.
3. Never mix logs with return payload.
4. Add a strict schema for final output.
5. Store one failing sample response for regression testing.

Example:

```python
print("RAW RESPONSE:", response)
print("FINAL TEXT:", final_text)
```

## 8. Recommended production pattern

Use this chain:

1. **Telegram Trigger**
2. **Prompt preparation**
3. **LLM node**
4. **Normalization node**
5. **Optional safety filter**
6. **Telegram Send Message**

The normalization node should be the only place that knows provider JSON structure.

## 9. Fast diagnosis matrix

### Symptom: assistant prints internal reasoning
- Check raw JSON for `reasoning`, `analysis`, `thoughts`
- Remove those fields from final mapping
- Review prompt for reasoning instructions

### Symptom: bot sends huge JSON blob
- Telegram node is sending the full object
- Replace with `final_text`

### Symptom: behavior changed without workflow edits
- Provider/model/node updated response schema
- Re-check raw output and remap fields

### Symptom: answer language/style became weird
- Check system prompt
- Check previous memory/context node
- Check whether debug prompt text is appended before LLM call

## 10. Final rule

In n8n, never trust provider output shape to stay stable.

Always:
- inspect raw output,
- normalize to one final field,
- send only that field to the user.