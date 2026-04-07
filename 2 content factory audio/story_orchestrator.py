import asyncio
import json
import os
from pathlib import Path

from google import genai
from google.genai import types
from dotenv import load_dotenv

from google_content_factory.vids_automation import create_google_vid
from nano_banana_generator import generate_story_image

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

DEFAULT_MODEL_CANDIDATES = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite-preview-02-05",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
]

API_KEY = os.environ.get("GOOGLE_API_KEY")

class StoryOrchestrator:
    def __init__(self, model_name=None):
        self.requested_model_name = model_name or os.environ.get("GEMINI_MODEL") or DEFAULT_MODEL_CANDIDATES[0]
        self.model_name = self.requested_model_name
        self.client = None
        if API_KEY:
            self.client = genai.Client(api_key=API_KEY)
        self.system_prompt = self._load_system_prompt()
        self.last_user_prompt = ""
        self.last_full_prompt = ""

    def _load_system_prompt(self):
        try:
            with open(BASE_DIR / "GEMINI_STORY_ENGINE.md", "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            print("Error: GEMINI_STORY_ENGINE.md not found.")
            return ""

    def _ensure_client(self):
        if not self.client:
            raise RuntimeError(
                "GOOGLE_API_KEY не найден. Добавьте ключ в .env или переменные окружения."
            )

    def _generate_with_model_fallback(self, prompt, system_instruction=None):
        self._ensure_client()
        last_error = None
        
        # Try requested model first, then candidates
        candidates = [self.requested_model_name] + [c for c in DEFAULT_MODEL_CANDIDATES if c != self.requested_model_name]
        
        for candidate in candidates:
            try:
                print(f"Trying Gemini model: {candidate}")
                response = self.client.models.generate_content(
                    model=candidate,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        response_mime_type="application/json"
                    )
                )
                self.model_name = candidate
                return response
            except Exception as error:
                last_error = error
                print(f"Model {candidate} failed: {error}")
                continue

        raise RuntimeError(
            f"Не удалось найти рабочую Gemini-модель. Последняя ошибка: {last_error}"
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

    async def generate_story_plan(self, user_goal, audience="", style="", custom_system_prompt=None):
        self._ensure_client()
        
        system_prompt = custom_system_prompt or self.system_prompt
        user_prompt = f"User Input: {user_goal}\nTarget Audience: {audience}\nVisual Style: {style}\n\nGenerate the story sequence in the requested JSON format."
        
        self.last_user_prompt = user_prompt
        self.last_full_prompt = f"SYSTEM:\n{system_prompt}\n\nUSER:\n{user_prompt}"
        
        response = self._generate_with_model_fallback(user_prompt, system_instruction=system_prompt)
        
        try:
            plan = self._parse_json_response(response.text)
            if isinstance(plan, dict):
                plan.setdefault("_meta", {})
                plan["_meta"].update({
                    "story_engine_model": self.model_name,
                    "story_engine_user_prompt": self.last_user_prompt,
                    "story_engine_system_prompt": system_prompt,
                    "story_engine_full_prompt": self.last_full_prompt,
                })
            return plan
        except Exception as e:
            print(f"Error parsing JSON: {e}")
            print("Raw response:", response.text)
            return None

    async def rework_story_plan(self, current_plan, feedback, custom_system_prompt=None):
        self._ensure_client()
        system_prompt = custom_system_prompt or self.system_prompt
        
        # Remove meta to keep context clean
        clean_plan = {k: v for k, v in current_plan.items() if k != "_meta"}
        
        user_prompt = (
            f"Current Story Plan (JSON):\n{json.dumps(clean_plan, ensure_ascii=False)}\n\n"
            f"User Feedback for Rework: {feedback}\n\n"
            "Please update the story plan based on this feedback. Maintain the Timochko structure (Hook-Context-Value-CTA). "
            "Return the full updated JSON."
        )
        
        self.last_user_prompt = user_prompt
        self.last_full_prompt = f"SYSTEM:\n{system_prompt}\n\nUSER:\n{user_prompt}"
        
        response = self._generate_with_model_fallback(user_prompt, system_instruction=system_prompt)
        
        try:
            plan = self._parse_json_response(response.text)
            if isinstance(plan, dict):
                plan.setdefault("_meta", {})
                plan["_meta"].update({
                    "story_engine_model": self.model_name,
                    "story_engine_user_prompt": self.last_user_prompt,
                    "story_engine_system_prompt": system_prompt,
                    "story_engine_full_prompt": self.last_full_prompt,
                    "rework_feedback": feedback
                })
            return plan
        except Exception as e:
            print(f"Error parsing JSON: {e}")
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
        
        if slide_type == "video":
            print(f"Triggering Google Vids for: {visual_prompt}")
            full_vids_prompt = f"{visual_prompt}. Include text overlay: '{script_text}'"
            await create_google_vid(full_vids_prompt)
        else:
            print(f"Static slide detected. Generating image via Nano Banana Pro...")
            output_path = BASE_DIR / "outputs" / "orchestrator_exports" / f"slide_{slide_num}.png"
            try:
                result = generate_story_image(slide, output_path)
                print(f"Successfully generated image: {result['file_path']}")
            except Exception as e:
                print(f"Error generating image for slide {slide_num}: {e}")

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
    
    user_goal = "Продать курс по ИИ-автоматизации для новичков"
    audience = "Владельцы малого бизнеса и фрилансеры"
    style = "Современный, профессиональный, технологичный, но доступный"
    
    await orchestrator.run(user_goal, audience, style)

if __name__ == "__main__":
    asyncio.run(main())
