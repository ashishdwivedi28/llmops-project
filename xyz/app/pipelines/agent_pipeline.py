import re
from typing import Any

from app.pipelines.base import BasePipeline
from app.services import llm_provider


class AgentPipeline(BasePipeline):
    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self.max_iterations = self.config.get("max_iterations", 3)

    def _calculator(self, expression: str) -> str:
        try:
            # Simple safe eval for demo purposes
            allowed_chars = "0123456789+-*/(). "
            if not all(c in allowed_chars for c in expression):
                return "Error: Invalid characters in expression"
            return str(eval(expression, {"__builtins__": {}}))
        except Exception as e:
            return f"Error: {str(e)}"

    def execute(self, user_input: str) -> str:
        """
        Executes a ReAct loop.
        """
        model = self.config.get("model", "gemini")
        system_prompt = self.config.get("system_prompt", "You are an agent.")
        history = f"{system_prompt}\nUser: {user_input}\n"

        for i in range(self.max_iterations):
            # 1. Ask LLM
            response = llm_provider.generate(history, model)
            history += f"{response}\n"

            # 2. Check for Final Answer
            if "Final Answer:" in response:
                return response.split("Final Answer:")[-1].strip()

            # 3. Check for Tool Calls (Simple Parsing)
            # Expecting format: Action: calculator\nInput: 2 + 2
            action_match = re.search(r"Action:\s*(\w+)", response)
            input_match = re.search(r"Input:\s*(.+)", response)

            if action_match and input_match:
                tool = action_match.group(1).strip().lower()
                tool_input = input_match.group(1).strip()

                result = ""
                if tool == "calculator":
                    result = self._calculator(tool_input)
                else:
                    result = f"Error: Tool '{tool}' not found."

                history += f"Observation: {result}\n"
            else:
                # If no clear action or final answer, just return the response
                # Or continue loop if the model is just 'thinking'
                if i == self.max_iterations - 1:
                    return response

        return "Agent reached maximum iterations without a final answer."
