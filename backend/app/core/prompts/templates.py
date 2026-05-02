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

REQUIREMENTS:
1. Provide a professional codebase including the core logic, configuration, and a detailed README.
2. The code must be production-ready with real logic, not placeholders.
3. If the tech stack is Flask, you MUST follow this exact structure:
   [project-name]/
   ├── app.py (main Flask application)
   ├── config.py (configuration settings)
   ├── requirements.txt (all dependencies)
   ├── models.py (database models using SQLAlchemy)
   ├── routes.py (all API endpoints)
   ├── templates/ (HTML files for web interface: base.html, index.html, create.html, edit.html, detail.html)
   ├── static/ (CSS: css/style.css, JS: js/script.js)
   ├── README.md (setup & usage instructions)
   └── .env.example (environment variables template)

Output exactly in this JSON format:
{{
    "files": [
        {{ "filename": "...", "content": "..." }},
        ...
    ]
}}
"""

FLASK_CODEBASE_PROMPT = """
You are an expert Python developer generating a complete, production-ready Flask web application.

PROJECT CONTEXT:
- Project Name: {title}
- Description: {overview}
- Difficulty Level: {difficulty}
- Duration: 3-4 weeks for a student

REQUIREMENTS - GENERATE COMPLETE & WORKING CODE:

1. PROJECT STRUCTURE:
Create files in this exact structure:
[project-name]/
├── app.py (main Flask application)
├── config.py (configuration settings)
├── requirements.txt (all dependencies)
├── models.py (database models using SQLAlchemy)
├── routes.py (all API endpoints)
├── templates/ (HTML files for web interface)
│   ├── base.html
│   ├── index.html
│   ├── create.html
│   ├── edit.html
│   └── detail.html
├── static/ (CSS, JS files)
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
├── README.md (setup & usage instructions)
└── .env.example (environment variables template)

Note: database.db should NOT be generated as a file, but your code should handle its creation.

Generate the content for ALL these files. Ensure the logic is connected correctly (routes use models, app uses routes and config, etc.).

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
