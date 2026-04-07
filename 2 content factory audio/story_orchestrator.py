import asyncio
import json
import os
from pathlib import Path

import google.generativeai as genai
from dotenv import load_dotenv

from google_content_factory.vids_automation import create_google_vid
from nano_banana_generator import generate_story_image

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
DEFAULT_MODEL_CANDIDATES = [
    "models/gemini-2.5-flash",
    "models/gemini-2.5-pro",
    "models/gemini-flash-latest",
    "models/gemini-pro-latest",
    "models/gemini-2.0-flash-001",
    "models/gemini-2.0-flash-lite",
]

# Configuration
# Ensure you have GOOGLE_API_KEY set in your environment variables
API_KEY = os.environ.get("GOOGLE_API_KEY")
if not API_KEY:
    print("Warning: GOOGLE_API_KEY not found in environment variables.")
else:
    genai.configure(api_key=API_KEY)

class StoryOrchestrator:
    def __init__(self, model_name=None):
        self.requested_model_name = model_name or os.environ.get("GEMINI_MODEL") or DEFAULT_MODEL_CANDIDATES[0]
        self.model_name = self._normalize_model_name(self.requested_model_name)
        self.model = genai.GenerativeModel(self.model_name) if API_KEY else None
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

    def _ensure_model(self):
        if not self.model:
            raise RuntimeError(
                "GOOGLE_API_KEY не найден. Добавьте ключ в .env или переменные окружения."
            )

    @staticmethod
    def _normalize_model_name(model_name):
        if not model_name:
            return model_name
        if model_name.startswith("models/"):
            return model_name
        return f"models/{model_name}"

    @staticmethod
    def _is_general_text_model(model_name):
        excluded_keywords = (
            "image",
            "tts",
            "robotics",
            "computer-use",
            "deep-research",
            "customtools",
        )
        return model_name.startswith("models/gemini") and not any(
            keyword in model_name for keyword in excluded_keywords
        )

    def _list_available_generate_models(self):
        try:
            available_models = []
            for model in genai.list_models():
                methods = getattr(model, "supported_generation_methods", []) or []
                if "generateContent" in methods:
                    available_models.append(model.name)
            return available_models
        except Exception as error:
            print(f"Warning: failed to list Gemini models dynamically: {error}")
            return []

    def _build_model_candidates(self):
        unique_candidates = []
        requested_candidate = self._normalize_model_name(self.requested_model_name)
        default_candidates = [self._normalize_model_name(candidate) for candidate in DEFAULT_MODEL_CANDIDATES]
        available_models = self._list_available_generate_models()

        if available_models:
            prioritized_candidates = [
                candidate for candidate in [requested_candidate, *default_candidates]
                if candidate in available_models
            ]
            general_fallback_candidates = [
                model_name
                for model_name in available_models
                if self._is_general_text_model(model_name)
            ]
            candidate_pool = [*prioritized_candidates, *general_fallback_candidates]
        else:
            candidate_pool = [requested_candidate, *default_candidates]

        for candidate in candidate_pool:
            if candidate and candidate not in unique_candidates:
                unique_candidates.append(candidate)
        return unique_candidates

    @staticmethod
    def _is_missing_or_unsupported_model_error(error):
        message = str(error).lower()
        return any(
            signature in message
            for signature in (
                "404",
                "not found",
                "not supported for generatecontent",
                "unsupported for generatecontent",
                "is not supported",
                "model",
            )
        ) and "api key" not in message

    def _generate_with_model_fallback(self, prompt):
        last_error = None

        for candidate in self._build_model_candidates():
            try:
                print(f"Trying Gemini model: {candidate}")
                model = genai.GenerativeModel(candidate)
                response = model.generate_content(
                    prompt,
                    generation_config={"response_mime_type": "application/json"}
                )
                self.model = model
                self.model_name = candidate
                return response
            except Exception as error:
                last_error = error
                if self._is_missing_or_unsupported_model_error(error):
                    print(f"Model {candidate} unavailable, trying fallback...")
                    continue
                raise

        tried_models = ", ".join(self._build_model_candidates())
        raise RuntimeError(
            f"Не удалось найти рабочую Gemini-модель. Попробовал: {tried_models}. "
            f"Последняя ошибка: {last_error}"
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

    @staticmethod
    def _build_user_prompt(user_goal, audience="", style=""):
        return f"""
User Input: {user_goal}
Target Audience: {audience}
Visual Style: {style}

Generate the story sequence in the requested JSON format.
"""

    async def generate_story_plan(self, user_goal, audience="", style=""):
        self._ensure_model()

        prompt = self._build_user_prompt(user_goal, audience, style)
        print(f"Generating story plan for: {user_goal}...")
        
        # Combine system prompt with user input
        full_prompt = f"{self.system_prompt}\n\n{prompt}"
        self.last_user_prompt = prompt.strip()
        self.last_full_prompt = full_prompt.strip()
        
        response = self._generate_with_model_fallback(full_prompt)
        print(f"Using Gemini model: {self.model_name}")
        
        try:
            plan = self._parse_json_response(response.text)
            if isinstance(plan, dict):
                plan.setdefault("_meta", {})
                plan["_meta"].update(
                    {
                        "story_engine_model": self.model_name,
                        "story_engine_user_prompt": self.last_user_prompt,
                        "story_engine_system_prompt": self.system_prompt,
                        "story_engine_full_prompt": self.last_full_prompt,
                    }
                )
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
            print(f"Static slide detected. Generating image via Nano Banana Pro...")
            output_path = BASE_DIR / "outputs" / "orchestrator_exports" / f"slide_{slide_num}.png"
            try:
                # generate_story_image is synchronous, but we can run it in a thread if needed.
                # For simplicity in this orchestrator, we'll call it directly.
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
    
    # Пример использования
    user_goal = "Продать курс по ИИ-автоматизации для новичков"
    audience = "Владельцы малого бизнеса и фрилансеры"
    style = "Современный, профессиональный, технологичный, но доступный"
    
    await orchestrator.run(user_goal, audience, style)

if __name__ == "__main__":
    asyncio.run(main())
