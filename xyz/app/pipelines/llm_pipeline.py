from app.pipelines.base import BasePipeline
from app.services import llm_provider


class LLMPipeline(BasePipeline):
    def execute(self, user_input: str) -> str:
        """
        Executes the pure LLM pipeline logic.
        """
        prompt_template = self.config.get("prompt_template", "{user_input}")
        prompt = prompt_template.format(user_input=user_input)

        return llm_provider.generate(prompt, self.model)
