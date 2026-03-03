
import json
import re

def extract_json(text):
    """Callback to extract JSON from LLM response which might contain backticks or control characters."""
    try:
        # 1. robust cleanup of markdown code blocks or 'json' prefix
        text = text.strip()
        
        if text.lower().startswith("json"):
             text = text[4:].strip()
        
        text = text.replace("```json", "").replace("```", "").strip()

        # 2. Find the first open brace and the last closed brace
        start = text.find("{")
        end = text.rfind("}") + 1
        
        if start != -1 and end != -1:
            json_str = text[start:end]
        else:
            json_str = text

        # 3. Try standard parsing
        try:
            return json.loads(json_str, strict=False)
        except json.JSONDecodeError as e:
            pass

        # 4. Fallback: Fix common LLM JSON syntax errors (unescaped newlines)
        try:
           clean_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', json_str) 
           clean_str = clean_str.replace('\n', '\\n')
           return json.loads(clean_str, strict=False)
        except Exception as e:
           pass

        return None

    except Exception as e:
        return None

# Test with various inputs
test_inputs = [
    # 1. Correct markdown
    '```json\n{"title": "Test"}\n```',
    # 2. Markdown with prefix
    'Here is your JSON: ```json\n{"title": "Test"}\n```',
    # 3. JSON with unescaped newlines in values (compact)
    '```json\n{"abstract": "Line 1\nLine 2"}\n```',
    # 4. Pretty-printed JSON with unescaped newlines in values (SUSPECTED BUG CASE)
    '```json\n{\n  "abstract": "Line 1\nLine 2"\n}\n```'
]

for i, inp in enumerate(test_inputs):
    print(f"Test {i+1} input length: {len(inp)}")
    res = extract_json(inp)
    print(f"Test {i+1} result: {res}")
