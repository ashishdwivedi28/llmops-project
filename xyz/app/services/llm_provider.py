import logging
import os

logger = logging.getLogger(__name__)


def generate(prompt: str, model: str) -> str:
    """Call the appropriate LLM provider based on model name.

    Args:
        prompt: The full formatted prompt string.
        model: One of 'mock', or a valid model name starting with 'gemini' or 'claude'.

    Returns:
        The model's text response.

    Raises:
        ValueError: If model name is not recognized.
        RuntimeError: If the API call fails.
    """
    # 1. Handle Mock
    if model == "mock":
        return f"[MOCK RESPONSE] You asked: {prompt[:80]}..."

    # 2. Handle Gemini / Vertex AI
    # We check if 'gemini' is in the name (case-insensitive) to allow variants like 'gemini-2.5-flash'
    elif "gemini" in model.lower():
        try:
            import vertexai
            from vertexai.generative_models import GenerativeModel

            project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
            location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")

            if not project_id:
                raise RuntimeError("GOOGLE_CLOUD_PROJECT environment variable is not set.")

            # Initialize Vertex AI
            vertexai.init(project=project_id, location=location)

            # Use the provided model name. If just "gemini", default to a stable flash model.
            vertex_model_name = model if model.lower() != "gemini" else "gemini-1.0-pro"

            client = GenerativeModel(vertex_model_name)
            response = client.generate_content(prompt)
            return str(response.text)

        except ImportError as e:
            raise RuntimeError("google-cloud-aiplatform package is not installed.") from e
        except Exception as e:
            raise RuntimeError(
                f"Gemini (Vertex AI) API call failed for model '{model}': {str(e)}"
            ) from e

    # 3. Handle Claude
    elif "claude" in model.lower():
        try:
            import anthropic

            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                raise RuntimeError("ANTHROPIC_API_KEY environment variable is not set.")

            client = anthropic.Anthropic(api_key=api_key)

            # Use provided model name, or default if just "claude"
            anthropic_model = model if model.lower() != "claude" else "claude-3-opus-20240229"

            message = client.messages.create(
                model=anthropic_model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )
            return str(message.content[0].text)
        except ImportError as e:
            raise RuntimeError("anthropic package is not installed.") from e
        except Exception as e:
            raise RuntimeError(f"Claude API call failed: {str(e)}") from e

    else:
        raise ValueError(f"Unknown model: '{model}'. Valid values: mock, gemini*, claude*")
