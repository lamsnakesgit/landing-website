import asyncio
import json
from core.story_orchestrator import StoryOrchestrator

async def test_fix():
    orchestrator = StoryOrchestrator()
    
    # Test case 1: Normal generation
    print("Testing normal generation...")
    plan = await orchestrator.generate_story_plan(
        user_goal="Продать курс по ИИ",
        audience="Новички",
        style="Современный",
        storyline_type="Expert",
        strategy="Популяризация ИИ"
    )
    
    if plan and isinstance(plan, dict) and "stories" in plan:
        print("✅ Success: Plan is a dictionary with 'stories' key.")
        print(f"Number of slides: {len(plan['stories'])}")
    else:
        print("❌ Failure: Plan structure is incorrect.")
        print(f"Plan type: {type(plan)}")
        print(f"Plan content: {plan}")

    # Test case 2: Manual normalization check
    print("\nTesting manual normalization logic...")
    # Mocking a list response to see if it gets wrapped
    mock_list = [{"slide_number": 1, "stage": "Hook"}]
    
    # We can't easily mock the internal _parse_json_response without changing the class
    # but we can test the logic we added to generate_story_plan by looking at the code
    # or by creating a small helper to test the normalization logic specifically.
    
    def normalize(plan):
        if isinstance(plan, list):
            plan = {"stories": plan}
        elif not isinstance(plan, dict):
            plan = {"stories": []}
        
        if "stories" not in plan:
            if any(isinstance(v, list) for v in plan.values()):
                for k, v in plan.items():
                    if isinstance(v, list):
                        plan["stories"] = v
                        break
            else:
                plan["stories"] = []
        return plan

    test_list = [{"a": 1}]
    normalized_list = normalize(test_list)
    if normalized_list == {"stories": [{"a": 1}]}:
        print("✅ Success: List correctly wrapped in 'stories' key.")
    else:
        print(f"❌ Failure: List normalization failed. Result: {normalized_list}")

    test_dict_wrong_key = {"slides": [{"a": 1}]}
    normalized_dict = normalize(test_dict_wrong_key)
    if "stories" in normalized_dict and normalized_dict["stories"] == [{"a": 1}]:
        print("✅ Success: Dict with wrong key correctly normalized.")
    else:
        print(f"❌ Failure: Dict normalization failed. Result: {normalized_dict}")

if __name__ == "__main__":
    asyncio.run(test_fix())
