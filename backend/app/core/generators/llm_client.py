import os
from groq import Groq
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

class LLMClient:
    def __init__(self, api_key, provider="groq"):
        self.api_key = api_key
        self.provider = provider
        self.client = None
        
        if not api_key:
            api_key = os.getenv("GROQ_API_KEY")
        
        if not api_key:
            raise ValueError("API Key is required")

        if provider == "groq":
            self.client = Groq(api_key=api_key)
            self.model = "llama-3.3-70b-versatile" # High performance free model
        elif provider == "openrouter":
            if OpenAI is None:
                raise ImportError("openai library required for OpenRouter")
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key
            )
            self.model = "meta-llama/llama-3-70b-instruct" # Example OpenRouter model
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def generate(self, prompt, system_prompt="You are a helpful AI assistant."):
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.7,
                max_tokens=4096, # Ensure enough context for code/reports
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"Error generating content: {str(e)}"
