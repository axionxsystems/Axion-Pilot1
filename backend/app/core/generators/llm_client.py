import os
import logging
import litellm
from google import genai

# Forced reload for environment variables
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).resolve().parent.parent.parent.parent / ".env")

# from app.utils.ollama_generator import OllamaGenerator


logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self, api_key="", provider=""):
        # Normalize empty string or junk (dots/spaces) to None
        self.api_key = api_key.strip() if api_key and len(api_key.strip()) > 10 else None
        self.provider = provider.strip().lower() if provider else ""
        
        # Auto-detect AI Provider and API Key
        env_provider = os.getenv("AI_PROVIDER", "").strip().lower()
        
        if not self.provider:
            self.provider = env_provider

        # PRIORITY: 1. Explicit provider, 2. Groq, 3. Gemini, 4. Others
        if not self.api_key:
            if self.provider == "groq" or (not self.provider and os.getenv("GROQ_API_KEY")):
                self.api_key = os.getenv("GROQ_API_KEY")
                self.provider = "groq"
                logger.debug("LLMClient: Loaded GROQ_API_KEY from env")
            elif self.provider == "gemini" or (not self.provider and os.getenv("GEMINI_API_KEY")):
                self.api_key = os.getenv("GEMINI_API_KEY")
                self.provider = "gemini"
                logger.debug("LLMClient: Loaded GEMINI_API_KEY from env")
            elif self.provider == "ollama":
                self.api_key = "local-ollama"
                logger.debug("LLMClient: Using local Ollama as requested")
            else:
                # Fall back to other providers
                self.api_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY")
                if self.api_key:
                    if os.getenv("ANTHROPIC_API_KEY"):
                        self.provider = "anthropic"
                    else:
                        self.provider = "openai"
                # Final fallback to Ollama is removed as per user request to disable it
                # elif os.getenv("OLLAMA_BASE_URL"): 
                #     self.provider = "ollama"
                #     self.api_key = "local-ollama"
                else:
                    logger.warning("LLMClient: No AI keys found")
        
        # Validation
        if not self.api_key:
            # if self.provider != "ollama" and os.getenv("OLLAMA_BASE_URL"):
            #     self.provider = "ollama"
            #     self.api_key = "local-ollama"
            # else:
            raise ValueError("AI API Key is required. Please check your .env file.")

        # Set optimal models based on provider
        if self.provider == "groq":
            self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        elif self.provider == "gemini":
            self.model = "gemini-2.0-flash"
        elif self.provider == "openai":
            self.model = "gpt-4o-mini"
        elif self.provider == "anthropic":
            self.model = "claude-3-5-sonnet-20241022"
        elif self.provider == "ollama":
            self.model = os.getenv("OLLAMA_MODEL", "llama3")
        else:
            self.model = "default"

    def generate(self, prompt, system_prompt="You are a helpful AI assistant.", model=None, temperature=0.7, max_tokens=4096):
        try:
            target_model = model or self.model
            
            # Use litellm for all providers (including gemini and groq)
            if self.provider == "gemini" and "/" not in target_model:
                model_string = f"gemini/{target_model}"
            elif self.provider == "groq" and "/" not in target_model:
                model_string = f"groq/{target_model}"
            else:
                model_string = target_model if "/" in target_model else f"{self.provider}/{target_model}"

            if self.provider == "ollama":
                # Ollama is disabled but logic kept for reference/commenting out
                # gen = OllamaGenerator(model=target_model)
                # return gen.generate(prompt, system=system_prompt, options={"temperature": temperature})
                raise RuntimeError("Ollama provider is currently disabled by user request.")

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
            elif "leaked" in error_msg.lower():
                error_msg = f"Your {self.provider.upper()} API key has been reported as leaked. Please update your .env file."
            elif "rate_limit" in error_msg.lower():
                error_msg = f"The {self.provider.upper()} API rate limit was hit."
            
            raise RuntimeError(f"Generation failed ({self.provider}): {error_msg}")

