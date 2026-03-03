
import json
import re

def extract_json(text):
    text = text.strip()
    if text.lower().startswith("json"):
         text = text[4:].strip()
    text = text.replace("```json", "").replace("```", "").strip()
    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end != -1:
        json_str = text[start:end]
    else:
        json_str = text
    try:
        return json.loads(json_str, strict=False)
    except json.JSONDecodeError as e:
        pass
    try:
       clean_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', json_str) 
       clean_str = clean_str.replace('\n', '\\n')
       return json.loads(clean_str, strict=False)
    except Exception as e:
       pass
    return None

print(f"Test 1: {extract_json('{\"a\": 1}')}")
print(f"Test 2: {extract_json('```json\\n{\"a\": 1}\\n```')}")
print(f"Test 3: {extract_json('{\\n  \"a\": \"line1\\nline2\"\\n}')}")
print(f"Test 4 (Pretty-printed fail): {extract_json('{\\n  \"a\": 1\\n}')}")
