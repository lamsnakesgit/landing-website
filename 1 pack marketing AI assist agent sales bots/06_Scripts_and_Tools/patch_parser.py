import re

with open("scripts/sud_parser/kalkan_docker/sud_parser.py", "r") as f:
    content = f.read()

mac_content = open("scripts/sud_parser_mac.py", "r").read()

m = re.search(r'(def solve_captcha.*?)(?=def main\(\):)', mac_content, re.DOTALL)
if m:
    new_funcs = m.group(1)
    
    new_funcs = new_funcs.replace("/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/output/pdfs", "/output/pdfs")
    new_funcs = new_funcs.replace("/Users/higherpower/Desktop/1_Active_Projects/2 Ai_agents/1 pack marketing AI assist agent sales bots/output/labor_cases.json", "/output/labor_cases.json")
    new_funcs = new_funcs.replace("OUTPUT_FILE", '"/output/labor_cases.json"')
    
    # Ищем начало блока search_cases
    start_idx = content.find("def search_cases(")
    end_idx = content.find("def main():")
    
    if start_idx != -1 and end_idx != -1:
        content = content[:start_idx] + new_funcs + content[end_idx:]
    
    if "import ddddocr" not in content:
        content = content.replace("import sys\n", "import sys\nimport urllib3\nimport ddddocr\nfrom bs4 import BeautifulSoup\n")
        
    content = content.replace("search_cases(session)", "search_and_download_cases(session)")
    
    with open("scripts/sud_parser/kalkan_docker/sud_parser.py", "w") as f:
        f.write(content)
    print("Patched!")
else:
    print("Could not find functions in mac script")
