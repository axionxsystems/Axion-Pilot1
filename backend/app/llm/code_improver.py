"""Code improver — reuses the shared LLMClient (Groq/Gemini/OpenAI/Anthropic via litellm)."""
import asyncio
import logging

from app.core.generators.llm_client import LLMClient

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a code improvement assistant. Given a file's current contents and a "
    "user request, return the full updated file contents only — no explanations, "
    "no markdown code fences."
)


async def improve_code(file_id: str, current_code: str, user_request: str) -> str:
    prompt = (
        f"File: {file_id}\n"
        f"User request: {user_request}\n"
        f"Current code:\n{current_code}\n"
        "Please return the full updated file contents only."
    )

    try:
        client = LLMClient()
        loop = asyncio.get_event_loop()
        updated = await loop.run_in_executor(
            None, lambda: client.generate(prompt, system_prompt=SYSTEM_PROMPT)
        )
        if updated and isinstance(updated, str) and updated.strip():
            return updated
    except Exception as e:
        logger.warning("Code improvement LLM call failed, returning fallback: %s", e)

    # Fallback: naive stub - return current code with a comment and do not break
    fallback = "# IMPROVED BY LLM (fallback — no AI provider configured or call failed)\n"
    return fallback + "\n" + current_code
