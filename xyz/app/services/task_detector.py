import json
import logging
import os

logger = logging.getLogger(__name__)

DETECTION_PROMPT = """Analyze this user request and classify it. Return ONLY valid JSON, nothing else.

User request: "{user_input}"

Rules:
- needs_rag: true if the user is asking about specific documents, files, policies, or internal data
- needs_agent: true if the user needs multi-step reasoning, code execution, or tool use

Return exactly: {{"needs_rag": true/false, "needs_agent": true/false}}"""

_CLASSIFIER_MODEL = None


def detect(user_input: str, model: str) -> dict:
    """Classify user intent to determine pipeline routing.

    Returns:
        dict with keys needs_rag (bool) and needs_agent (bool).
    """
    global _CLASSIFIER_MODEL

    if model == "mock":
        return {"needs_rag": False, "needs_agent": False}

    try:
        # Use the unified llm_provider instead of initializing Vertex AI directly.
        # This ensures we go through LiteLLM and respect whatever provider the user has configured,
        # while defaulting to a fast/cheap model (like gemini-2.5-flash) for classification.
        from app.services import llm_provider
        
        prompt = DETECTION_PROMPT.format(user_input=user_input)

        logger.info(f"TaskDetector: analyzing input with fast classifier model (defaulting to gemini-2.5-flash)")
        
        # We can safely use gemini-2.5-flash if GOOGLE_CLOUD_PROJECT is set, 
        # otherwise we should fallback to whatever model they passed in.
        classifier_model = "gemini-2.5-flash" if os.getenv("GOOGLE_CLOUD_PROJECT") else model
        
        raw = llm_provider.generate(prompt=prompt, model=classifier_model).strip()
        logger.debug(f"TaskDetector: raw response: {raw}")

        # Handle simple string keywords first
        if "NEEDS_RAG" in raw:
            logger.info("TaskDetector: matched keyword NEEDS_RAG")
            return {"needs_rag": True, "needs_agent": False}
        if "NEEDS_AGENT" in raw:
            logger.info("TaskDetector: matched keyword NEEDS_AGENT")
            return {"needs_rag": False, "needs_agent": True}

        # Cleanup potential markdown formatting
        if raw.startswith("```json"):
            raw = raw[7:]
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()

        result = json.loads(raw)
        logger.info(f"TaskDetector: parsed result: {result}")
        return {
            "needs_rag": bool(result.get("needs_rag", False)),
            "needs_agent": bool(result.get("needs_agent", False)),
        }
    except Exception as e:
        logger.warning(f"Task detection failed, using defaults: {e}")
        return {"needs_rag": False, "needs_agent": False}
