import json
import logging

from app.services import llm_provider

logger = logging.getLogger(__name__)

DETECTION_PROMPT = """Analyze this user request and classify it. Return ONLY valid JSON, nothing else.

User request: "{user_input}"

Rules:
- needs_rag: true if the user is asking about specific documents, files, policies, or internal data
- needs_agent: true if the user needs multi-step reasoning, code execution, or tool use

Return exactly: {{"needs_rag": true/false, "needs_agent": true/false}}"""


def detect(user_input: str, model: str) -> dict:
    """Classify user intent to determine pipeline routing.

    Returns:
        dict with keys needs_rag (bool) and needs_agent (bool).
    """
    if model == "mock":
        return {"needs_rag": False, "needs_agent": False}

    try:
        prompt = DETECTION_PROMPT.format(user_input=user_input)
        raw = llm_provider.generate(prompt, model)
        # Cleanup potential markdown formatting
        raw = raw.strip()

        if "NEEDS_RAG" in raw:
            return {"needs_rag": True, "needs_agent": False}
        if "NEEDS_AGENT" in raw:
            return {"needs_rag": False, "needs_agent": True}

        if raw.startswith("```json"):
            raw = raw[7:]
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()

        result = json.loads(raw)
        return {
            "needs_rag": bool(result.get("needs_rag", False)),
            "needs_agent": bool(result.get("needs_agent", False)),
        }
    except Exception as e:
        logger.warning(f"Task detection failed, using defaults: {e}")
        return {"needs_rag": False, "needs_agent": False}
