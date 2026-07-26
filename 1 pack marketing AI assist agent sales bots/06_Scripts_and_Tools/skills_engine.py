import os
import yaml
import json
import logging

logger = logging.getLogger(__name__)

SKILLS_DIR = ".agents/skills"

def parse_frontmatter(file_content):
    """Парсит YAML frontmatter из SKILL.md"""
    if file_content.startswith("---"):
        parts = file_content.split("---", 2)
        if len(parts) >= 3:
            try:
                frontmatter = yaml.safe_load(parts[1])
                body = parts[2].strip()
                return frontmatter, body
            except yaml.YAMLError as e:
                logger.error(f"Ошибка парсинга YAML: {e}")
    return None, file_content

def load_all_skills():
    """Сканирует папку со скиллами и собирает OpenAI Tools"""
    skills = []
    tools = []
    
    if not os.path.exists(SKILLS_DIR):
        logger.warning(f"Директория {SKILLS_DIR} не найдена.")
        return tools, skills

    for root, dirs, files in os.walk(SKILLS_DIR):
        if "SKILL.md" in files:
            skill_path = os.path.join(root, "SKILL.md")
            try:
                with open(skill_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                frontmatter, body = parse_frontmatter(content)
                if frontmatter and "name" in frontmatter and "description" in frontmatter:
                    skill_name = frontmatter["name"].replace("-", "_")
                    description = frontmatter["description"]
                    
                    # Сохраняем информацию о скилле
                    skills.append({
                        "name": skill_name,
                        "description": description,
                        "path": root,
                        "body": body
                    })
                    
                    # Формируем OpenAI Tool
                    tools.append({
                        "type": "function",
                        "function": {
                            "name": f"execute_{skill_name}",
                            "description": f"Use this tool to execute the '{frontmatter['name']}' skill. Description: {description}",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "task_input": {
                                        "type": "string",
                                        "description": "The specific query, parameters, or input for this skill."
                                    }
                                },
                                "required": ["task_input"]
                            }
                        }
                    })
            except Exception as e:
                logger.error(f"Ошибка загрузки скилла {skill_path}: {e}")
                
    return tools, skills

def execute_skill(skill_name, task_input):
    """Здесь будет логика запуска скриптов скилла"""
    logger.info(f"Executing skill {skill_name} with input: {task_input}")
    
    if skill_name == "threads_leadgen":
        from threads_parser import parse_threads_leads
        return parse_threads_leads(task_input)
    
    # Пока заглушка для остальных: просто возвращаем факт того, что скилл вызван
    return f"Skill {skill_name} successfully called with input: {task_input}. No python execution logic attached yet."

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    tools, skills = load_all_skills()
    print(f"Loaded {len(skills)} skills:")
    for t in tools:
        print(json.dumps(t, indent=2, ensure_ascii=False))
