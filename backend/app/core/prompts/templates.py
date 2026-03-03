PROJECT_STRUCTURE_PROMPT = """
Generate a comprehensive project structure for a college project with the following details:
Domain: {domain}
Topic: {topic}
Difficulty: {difficulty}
Tech Stack: {tech_stack}
Academic Level: {level}

Please provide the output in the following JSON format:
{{
    "title": "Project Title",
    "abstract": "200-300 words abstract...",
    "problem_statement": "Clear problem definition...",
    "architecture_description": "Description of system modules...",
    "tech_stack_details": {{
        "Frontend": "...",
        "Backend": "...",
        "Database": "...",
        "AI/ML Model": "..."
    }},
    "files": [
        {{
            "filename": "main.py",
            "content": "Full code here..."
        }},
        {{
            "filename": "requirements.txt",
            "content": "..."
        }},
        {{
            "filename": "README.md",
            "content": "..."
        }}
    ],
    "viva_questions": [
        {{
            "question": "...",
            "answer": "..."
        }},
        ... (5 questions)
    ]
}}
Ensure the code is functional, commented, and uses the specified tech stack.
"""
