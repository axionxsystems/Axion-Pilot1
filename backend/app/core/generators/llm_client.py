import os
import litellm
from groq import Groq
from google import genai

# Forced reload for environment variables
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).resolve().parent.parent.parent.parent / ".env")

class LLMClient:
    def __init__(self, api_key="", provider=""):
        # Normalize empty string or junk (dots/spaces) to None
        self.api_key = api_key.strip() if api_key and len(api_key.strip()) > 10 else None
        self.provider = provider.strip().lower() if provider else ""
        
        # Auto-detect API keys from environment if not provided
        # PRIORITY: Groq > Anthropic > OpenAI > Gemini (to avoid quota issues)
        if not self.api_key:
            # Try Groq first (most reliable)
            self.api_key = os.getenv("GROQ_API_KEY")
            if self.api_key:
                self.provider = "groq"
                print(f"DEBUG: LLMClient Loaded GROQ_API_KEY from env")
            else:
                # Fall back to other providers
                self.api_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY")
                if self.api_key:
                    if os.getenv("ANTHROPIC_API_KEY"):
                        self.provider = "anthropic"
                        print(f"DEBUG: LLMClient Loaded ANTHROPIC_API_KEY from env")
                    else:
                        self.provider = "openai"
                        print(f"DEBUG: LLMClient Loaded OPENAI_API_KEY from env")
                else:
                    print("DEBUG: No Groq/Anthropic/OpenAI keys found - may use Gemini if explicitly requested")
        
        # Auto-detect provider from API key format if provider not specified
        if self.api_key and not self.provider:
            if self.api_key.startswith("gsk_"):
                self.provider = "groq"
            elif self.api_key.startswith("sk-ant"):
                self.provider = "anthropic"
            elif self.api_key.startswith("sk-") and "proj" in self.api_key:
                self.provider = "openai"
            elif self.api_key.startswith("AIza"):
                self.provider = "gemini"
            else:
                self.provider = "groq"  # default to Groq
        
        if not self.api_key:
            raise ValueError("API Key is required")

        # Set optimal models based on provider
        if self.provider == "groq":
            self.model = "llama-3.3-70b-versatile"
        elif self.provider == "gemini":
            self.model = "gemini-2.0-flash"
        elif self.provider == "openai":
            self.model = "gpt-4o-mini"
        elif self.provider == "anthropic":
            self.model = "claude-3-5-sonnet-20241022"
        else:
            self.model = "default"

    def generate(self, prompt, system_prompt="You are a helpful AI assistant.", model=None, temperature=0.7, max_tokens=4096):
        try:
            target_model = model or self.model
            
            # Use native Gemini SDK if provider is Gemini
            if self.provider == "gemini":
                client = genai.Client(api_key=self.api_key)
                response = client.models.generate_content(
                    model=target_model,
                    contents=prompt,
                    config=genai.types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=temperature,
                        max_output_tokens=max_tokens,
                    )
                )
                return response.text
            
            # Use native Groq if provider is Groq
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
            
            # Use litellm for other providers
            model_string = target_model if "/" in target_model else f"{self.provider}/{target_model}"

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
            if "invalid_api_key" in error_msg.lower() or "401" in error_msg or "api key" in error_msg.lower():
                error_msg = f"The {self.provider.upper()} API key is invalid or has been revoked."
            elif "rate_limit" in error_msg.lower():
                error_msg = f"The {self.provider.upper()} API rate limit was hit."
            
            raise RuntimeError(f"Generation failed ({self.provider}): {error_msg}")
