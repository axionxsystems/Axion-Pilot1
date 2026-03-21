import json
import re
from .llm_client import LLMClient
from ..prompts.system_prompts import PROJECT_GENERATOR_SYSTEM_PROMPT
from ..prompts.templates import (
    IDEA_EXPANSION_PROMPT,
    ARCHITECTURE_PLANNING_PROMPT,
    CODEBASE_GENERATION_PROMPT,
    DOCUMENTATION_PROMPT,
    VIVA_PREP_PROMPT
)

def extract_json(text):
    """Robust JSON extraction from LLM response."""
    try:
        if not text:
            return None
        text = text.strip()
        if text.lower().startswith("json"):
             text = text[4:].strip()
        
        text = text.replace("```json", "").replace("```", "").strip()
        start = text.find("{")
        end = text.rfind("}") + 1
        
        if start != -1 and end != -1:
            json_str = text[start:end]
            # Clean control characters but preserve common whitespace
            clean_str = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]', '', json_str)
            return json.loads(clean_str, strict=False)
        return None
    except Exception as e:
        print(f"JSON Parse Error: {e}")
        return None

def generate_project(api_key, domain, topic, description, difficulty, tech_stack, level, ai_config=None):
    client = LLMClient(api_key=api_key)
    
    # Extract AI Config
    config = ai_config or {}
    temp = config.get("temperature", 0.7)
    tokens = config.get("max_tokens", 4096)
    features = config.get("features", {
        "advanced_mode": True,
        "deep_code": True,
        "extended_docs": True,
        "arch_planning": True
    })

    # STAGE 1: IDEA EXPANSION
    print("Pipeline Stage 1: Idea Expansion")
    idea_prompt = IDEA_EXPANSION_PROMPT.format(
        domain=domain,
        topic=topic,
        description=description,
        difficulty=difficulty,
        level=level
    )
    res_idea = client.generate(idea_prompt, system_prompt=PROJECT_GENERATOR_SYSTEM_PROMPT, temperature=temp, max_tokens=tokens)
    idea_data = extract_json(res_idea) or {}
    
    title = idea_data.get("expanded_title", topic)
    overview = idea_data.get("project_overview", description)
    features_list = idea_data.get("features", [])

    # STAGE 2: ARCHITECTURE PLANNING (Conditional)
    arch_data = {}
    if features.get("arch_planning"):
        print("Pipeline Stage 2: Architecture Planning")
        arch_prompt = ARCHITECTURE_PLANNING_PROMPT.format(
            title=title,
            overview=overview,
            features=", ".join(features_list),
            tech_stack=tech_stack
        )
        res_arch = client.generate(arch_prompt, system_prompt=PROJECT_GENERATOR_SYSTEM_PROMPT, temperature=temp, max_tokens=tokens)
        arch_data = extract_json(res_arch) or {}

    # STAGE 3: CODEBASE GENERATION (Conditional)
    code_data = {"files": []}
    if features.get("deep_code"):
        print("Pipeline Stage 3: Codebase Generation")
        code_prompt = CODEBASE_GENERATION_PROMPT.format(
            architecture=arch_data.get("system_architecture", "Standard Software Architecture"),
            tech_stack=tech_stack
        )
        res_code = client.generate(code_prompt, system_prompt=PROJECT_GENERATOR_SYSTEM_PROMPT, temperature=temp, max_tokens=tokens)
        code_data = extract_json(res_code) or {"files": []}

    # STAGE 4: DOCUMENTATION GENERATION (Conditional)
    doc_data = {}
    if features.get("extended_docs"):
        print("Pipeline Stage 4: Documentation Generation")
        doc_prompt = DOCUMENTATION_PROMPT.format(
            concept=overview,
            architecture=arch_data.get("system_architecture", "Standard Architecture")
        )
        res_doc = client.generate(doc_prompt, system_prompt=PROJECT_GENERATOR_SYSTEM_PROMPT, temperature=temp, max_tokens=tokens)
        doc_data = extract_json(res_doc) or {}

    # STAGE 5: VIVA PREP
    print("Pipeline Stage 5: Viva Preparation")
    viva_prompt = VIVA_PREP_PROMPT.format(
        title=title,
        architecture=arch_data.get("system_architecture", "Standard Architecture"),
        code_summary=f"Includes files: {', '.join([f.get('filename', '') for f in code_data.get('files', [])])}"
    )
    res_viva = client.generate(viva_prompt, system_prompt=PROJECT_GENERATOR_SYSTEM_PROMPT, temperature=temp, max_tokens=tokens)
    viva_data = extract_json(res_viva) or {"viva_questions": []}

    # Consolidated Result
    return {
        "title": title,
        "abstract": doc_data.get("abstract", overview),
        "problem_statement": doc_data.get("problem_statement", ""),
        "architecture_description": arch_data.get("system_architecture", ""),
        "tech_stack_details": arch_data.get("tech_stack_details", {}),
        "files": code_data.get("files", []),
        "viva_questions": viva_data.get("viva_questions", []),
        "tags": [domain, difficulty],
        "estimated_completion_time": "2-3 Weeks",
        "domain": domain,
        "difficulty": difficulty,
        "features": features_list,
        "database_design": arch_data.get("database_design", ""),
        "logic_flow": arch_data.get("logic_flow", ""),
        "security_measures": arch_data.get("security_measures", ""),
        "literature_survey": doc_data.get("literature_survey", ""),
        "methodology": doc_data.get("methodology", ""),
    }
