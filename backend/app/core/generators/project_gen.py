import json
import re
from .llm_client import LLMClient
from ..prompts.system_prompts import PROJECT_GENERATOR_SYSTEM_PROMPT
from ..prompts.templates import PROJECT_STRUCTURE_PROMPT

def extract_json(text):
    """Callback to extract JSON from LLM response which might contain backticks or control characters."""
    try:
        print(f"DEBUG: Raw LLM Response length: {len(text)}")
        
        # 1. robust cleanup of markdown code blocks or 'json' prefix
        # Regex explanation:
        # ^\s* -> start of string, optional whitespace
        # (```json)? -> optional ```json
        # (json)? -> optional "json" word (if no backticks)
        # .*? -> non-greedy match until {
        text = text.strip()
        
        # Simple string replacements for common patterns
        if text.lower().startswith("json"):
             text = text[4:].strip()
        
        text = text.replace("```json", "").replace("```", "").strip()

        # 2. Find the first open brace and the last closed brace
        start = text.find("{")
        end = text.rfind("}") + 1
        
        if start != -1 and end != -1:
            json_str = text[start:end]
        else:
            print(f"DEBUG: Could not find braces. Response start: {text[:50]}...")
            json_str = text

        # 3. Try standard parsing
        try:
            return json.loads(json_str, strict=False)
        except json.JSONDecodeError as e:
            print(f"DEBUG: Initial JSON parse failed: {e}")

        # 4. Fallback: Fix common LLM JSON syntax errors (unescaped newlines)
        try:
           # Naive cleanup for control characters
           import re
           # Remove control characters
           clean_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', json_str) 
           # Escape newlines inside strings if needed (simple approach)
           clean_str = clean_str.replace('\n', '\\n')
           return json.loads(clean_str, strict=False)
        except Exception as e:
           print(f"DEBUG: Fallback parsing failed: {e}")
           pass

        return None

    except Exception as e:
        print(f"JSON Parse Error: {e}")
        return None

def generate_project(api_key, domain, topic, difficulty, tech_stack, level):
    client = LLMClient(api_key=api_key)
    
    prompt = PROJECT_STRUCTURE_PROMPT.format(
        domain=domain,
        topic=topic,
        difficulty=difficulty,
        tech_stack=tech_stack,
        level=level
    )
    
    raw_response = client.generate(prompt, system_prompt=PROJECT_GENERATOR_SYSTEM_PROMPT)
    
    if raw_response and raw_response.startswith("Error generating content"):
        raise Exception(raw_response)

    project_data = extract_json(raw_response)
    
    if not project_data:
        raise Exception(f"Failed to parse project data. Raw response: {raw_response[:200]}...")
        
    return project_data
