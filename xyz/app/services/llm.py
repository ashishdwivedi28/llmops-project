from typing import Any

from app.services.llm_provider import generate as llm_generate


def generate(prompt: str, **kwargs: Any) -> str:
    """A wrapper for the LLM provider's generate function.

    This provides a consistent interface for other parts of the application
    to call the LLM, abstracting away the specific provider implementation.
    """
    return llm_generate(prompt, **kwargs)
