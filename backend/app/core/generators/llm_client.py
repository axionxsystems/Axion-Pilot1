import os
import litellm
from groq import Groq

# Forced reload for environment variables
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).resolve().parent.parent.parent.parent / ".env")

class LLMClient:
    def __init__(self, api_key, provider="groq"):
        # Normalize empty string or junk (dots/spaces) to None
        self.api_key = api_key.strip() if api_key and len(api_key.strip()) > 10 else None
        self.provider = provider or "groq"
        
        # Auto-detect defaults if key is missing — use system env key
        if not self.api_key:
            self.api_key = os.getenv("GROQ_API_KEY")
            if self.api_key:
                print(f"DEBUG: LLMClient Loaded ENV KEY: {self.api_key[:10]}...")
            else:
                print("DEBUG: LLMClient GROQ_API_KEY IS MISSING IN ENV!")
            self.provider = "groq"
        else:
             self.api_key = self.api_key.strip()
            
        # Optional intelligent format detection
        if self.api_key and self.provider == "groq":
            if self.api_key.startswith("sk-ant"):
                self.provider = "anthropic"
            elif self.api_key.startswith("sk-") and "proj" in self.api_key:
                self.provider = "openai"
                
        if not self.api_key:
            raise ValueError("API Key is required")

        # Set optimal models
        if self.provider == "groq":
            self.model = "llama-3.3-70b-versatile"
        elif self.provider == "openai":
            self.model = "gpt-4o-mini"
        elif self.provider == "anthropic":
            self.model = "claude-3-5-sonnet-20241022"
        elif self.provider == "gemini":
             self.model = "gemini/gemini-2.0-flash"
        else:
             self.model = f"{self.provider}/default"

    def generate(self, prompt, system_prompt="You are a helpful AI assistant.", model=None, temperature=0.7, max_tokens=4096):
        try:
            target_model = model or self.model
            
            # Use native Groq if provider is Groq to bypass litellm complications
            if self.provider == "groq":
                client = Groq(api_key=self.api_key)
                response = client.chat.completions.create(
                    model=target_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content
            
            # Use litellm for everything else
            model_string = target_model if "/" in target_model else f"{self.provider}/{target_model}"
            # Gemini bypass: gemini/gemini...
            if self.provider == "gemini" and not model_string.startswith("gemini/"):
                 model_string = f"gemini/{target_model}"

            response = litellm.completion(
                model=model_string,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                api_key=self.api_key,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
             # Specialized error reporting
             error_msg = str(e)
             if "invalid_api_key" in error_msg.lower():
                  error_msg = f"The {self.provider} API key is invalid or has been revoked."
             elif "rate_limit_exceeded" in error_msg.lower():
                  error_msg = f"The {self.provider} API rate limit was hit."
             
             raise RuntimeError(f"Generation failed ({self.provider}): {error_msg}")
