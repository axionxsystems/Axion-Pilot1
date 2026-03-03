from .llm_client import LLMClient
from ..prompts.system_prompts import VIVA_ASSISTANT_SYSTEM_PROMPT

def get_viva_response(api_key, history, project_data):
    """
    Generates a response for the viva assistant based on chat history and project context.
    """
    client = LLMClient(api_key=api_key)
    
    # Construct context from project data
    context = ""
    if project_data:
        context = f"""
        Student Project Context:
        Title: {project_data.get('title')}
        Abstract: {project_data.get('abstract')}
        Architecture: {project_data.get('architecture_description')}
        Tech Stack: {project_data.get('tech_stack_details')}
        """
    
    # Format messages for LLM
    messages = [{"role": "system", "content": VIVA_ASSISTANT_SYSTEM_PROMPT + "\n" + context}]
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})
        
    # We need to expose the raw message structure to the client or reconstruct the prompt
    # Simplification: We'll just append the last question with context to a wrapper if simple generation
    # But LLMClient.generate takes a string prompt. We should enhance LLMClient to handle messages or stringify.
    # For now, let's just format the conversation as a string script.
    
    conversation_str = ""
    for msg in history:
        conversation_str += f"{msg['role'].upper()}: {msg['content']}\n"
        
    final_prompt = f"{context}\n\nConversation History:\n{conversation_str}\n\nEXAMINER (You):"
    
    return client.generate(final_prompt, system_prompt=VIVA_ASSISTANT_SYSTEM_PROMPT)
