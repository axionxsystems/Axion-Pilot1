PROJECT_STRUCTURE_PROMPT = """
[DEPRECATED] - Use the structured pipeline prompts below.
"""

# --- PIPELINE STAGE 1: IDEA EXPANSION ---
IDEA_EXPANSION_PROMPT = """
You are a Product Manager and Domain Expert. Expand the following project idea into a full-scale professional concept.
Domain: {domain}
Topic: {topic}
Original Description: {description}
Difficulty: {difficulty}
Level: {level}

Expand this into:
1. Detailed Project Overview (400+ words).
2. Key Features (at least 8 professional features).
3. Target Audience & Use Cases.
4. Innovation & Unique Selling Points (USP).

Output exactly in this JSON format:
{{
    "expanded_title": "...",
    "project_overview": "...",
    "features": ["...", "..."],
    "target_audience": "...",
    "usps": ["...", "..."]
}}
"""

# --- PIPELINE STAGE 2: TECHNICAL ARCHITECTURE ---
ARCHITECTURE_PLANNING_PROMPT = """
As a Technical Architect, design a robust system architecture for:
Project: {title}
Concept: {overview}
Features: {features}
Tech Stack preference: {tech_stack}

Provide:
1. Deep Architecture Description (Modules, Microservices/Components).
2. Database Schema (detailed tables and relationships).
3. Data Flow & System Logic.
4. Security & Performance considerations.

Output exactly in this JSON format:
{{
    "system_architecture": "...",
    "database_design": "...",
    "logic_flow": "...",
    "security_measures": "...",
    "tech_stack_details": {{
        "frontend": "...",
        "backend": "...",
        "database": "...",
        "other": "..."
    }}
}}
"""

# --- PIPELINE STAGE 3: CODEBASE GENERATION ---
CODEBASE_GENERATION_PROMPT = """
As a Senior Developer, generate a full, production-ready codebase structure and core implementation for:
Architecture: {architecture}
Tech Stack: {tech_stack}

Provide 3-5 high-quality files including the core logic, requirements, and a detailed README.
Make sure the code is PROFESSIONAL, not generic. Implement real logic, not placeholders.

Output exactly in this JSON format:
{{
    "files": [
        {{ "filename": "...", "content": "..." }},
        ...
    ]
}}
"""

# --- PIPELINE STAGE 4: DOCUMENTATION & REPORT ---
DOCUMENTATION_PROMPT = """
As an Academic Documentation Specialist, generate detailed report content for this project.
Concept: {concept}
Architecture: {architecture}

Generate:
1. High-quality Abstract (300 words).
2. Problem Statement.
3. Literature Survey (Summarize 3 hypothetical research papers related to this).
4. Methodology.

Output exactly in this JSON format:
{{
    "abstract": "...",
    "problem_statement": "...",
    "literature_survey": "...",
    "methodology": "..."
}}
"""

# --- PIPELINE STAGE 5: VIVA PREP ---
VIVA_PREP_PROMPT = """
As a Viva Examiner, generate 10 high-level "Advanced" questions and answers based on this project.
Title: {title}
Architecture: {architecture}
Code Summary: {code_summary}

Focus on:
1. Implementation choices.
2. Troubleshooting.
3. Scaling the project.

Output exactly in this JSON format:
{{
    "viva_questions": [
        {{ "question": "...", "answer": "..." }},
        ...
    ]
}}
"""
