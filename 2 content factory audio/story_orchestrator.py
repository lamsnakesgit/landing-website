import asyncio
import json
import os
from pathlib import Path

import google.generativeai as genai
from dotenv import load_dotenv

from google_content_factory.vids_automation import create_google_vid

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Configuration
# Ensure you have GOOGLE_API_KEY set in your environment variables
API_KEY = os.environ.get("GOOGLE_API_KEY")
if not API_KEY:
    print("Warning: GOOGLE_API_KEY not found in environment variables.")
else:
    genai.configure(api_key=API_KEY)

class StoryOrchestrator:
    def __init__(self, model_name="gemini-1.5-pro"):
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name) if API_KEY else None
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self):
        try:
            with open(BASE_DIR / "GEMINI_STORY_ENGINE.md", "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            print("Error: GEMINI_STORY_ENGINE.md not found.")
            return ""

    def _ensure_model(self):
        if not self.model:
            raise RuntimeError(
                "GOOGLE_API_KEY не найден. Добавьте ключ в .env или переменные окружения."
            )

    @staticmethod
    def _parse_json_response(raw_text):
        cleaned = raw_text.strip()

        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            cleaned = "\n".join(lines).strip()
            if cleaned.lower().startswith("json"):
                cleaned = cleaned[4:].strip()

        return json.loads(cleaned)

    async def generate_story_plan(self, user_goal, audience="", style=""):
        self._ensure_model()

        prompt = f"""
User Input: {user_goal}
Target Audience: {audience}
Visual Style: {style}

Generate the story sequence in the requested JSON format.
"""
        print(f"Generating story plan for: {user_goal}...")
        
        # Combine system prompt with user input
        full_prompt = f"{self.system_prompt}\n\n{prompt}"
        
        response = self.model.generate_content(
            full_prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        try:
            plan = self._parse_json_response(response.text)
            return plan
        except json.JSONDecodeError:
            print("Error: Failed to parse JSON from Gemini response.")
            print("Raw response:", response.text)
            return None

    async def process_slide(self, slide):
        slide_num = slide.get("slide_number")
        stage = slide.get("stage")
        slide_type = slide.get("type", "photo")
        visual_prompt = slide.get("visual_prompt")
        script_text = slide.get("script_text")
        source_image = slide.get("source_image_path") or slide.get("source_image")
        
        print(f"\n--- Processing Slide {slide_num} ({stage}) ---")
        print(f"Type: {slide_type}")
        print(f"Text: {script_text}")
        if source_image:
            print(f"Source image: {source_image}")
        
        if slide_type == "video":
            print(f"Triggering Google Vids for: {visual_prompt}")
            # In a real scenario, we might want to combine script_text and visual_prompt
            full_vids_prompt = f"{visual_prompt}. Include text overlay: '{script_text}'"
            await create_google_vid(full_vids_prompt)
        else:
            # Fallback to Fal.ai (Nano Banana) placeholder
            print(f"Static slide detected. Fallback to Fal.ai (Nano Banana) would happen here.")
            print(f"Prompt: {visual_prompt}")
            # TODO: Implement Fal.ai integration when needed
            await self._mock_fal_ai_call(slide)

    async def _mock_fal_ai_call(self, slide):
        # Placeholder for Fal.ai integration
        await asyncio.sleep(1)
        if slide.get("source_image_path") or slide.get("source_image"):
            print(
                f"Using uploaded image as base asset for slide {slide.get('slide_number')}"
            )
        print(f"Fal.ai placeholder: Generated static layout for slide {slide.get('slide_number')}")

    async def process_story_plan(self, plan):
        if not plan or "stories" not in plan:
            raise ValueError("Invalid plan: missing 'stories' key.")

        print(f"Plan generated with {len(plan['stories'])} slides.")

        for slide in plan["stories"]:
            await self.process_slide(slide)

        print("\nAll slides processed successfully!")
        return plan

    async def run(self, user_goal, audience="", style=""):
        plan = await self.generate_story_plan(user_goal, audience, style)
        if not plan or "stories" not in plan:
            print("Failed to generate a valid story plan.")
            return

        await self.process_story_plan(plan)
        return plan

async def main():
    orchestrator = StoryOrchestrator()
    
    # Пример использования
    user_goal = "Продать курс по ИИ-автоматизации для новичков"
    audience = "Владельцы малого бизнеса и фрилансеры"
    style = "Современный, профессиональный, технологичный, но доступный"
    
    await orchestrator.run(user_goal, audience, style)

if __name__ == "__main__":
    asyncio.run(main())
