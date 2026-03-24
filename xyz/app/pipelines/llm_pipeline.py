import logging

from app.pipelines.base import BasePipeline
from app.services import llm_provider

logger = logging.getLogger(__name__)


class LLMPipeline(BasePipeline):
    def execute(self, user_input: str) -> str:
        """
        Executes the pure LLM pipeline logic.
        """
        prompt_template = self.config.get("prompt_template", "{user_input}")
        logger.info(f"LLMPipeline: preparing prompt. Model: {self.model}")

        prompt = prompt_template.format(user_input=user_input)
        logger.debug(f"LLMPipeline prompt: {prompt[:100]}...")

        response = llm_provider.generate(prompt, self.model)
        logger.info(f"LLMPipeline: generated response length={len(response)}")

        return response
