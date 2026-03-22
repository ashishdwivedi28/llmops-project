from abc import ABC, abstractmethod
from typing import Any


class Tool(ABC):
    """
    Base class for all Agent Tools.
    Each tool must define its name, description, and an 'execute' method.
    """

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def execute(self, **kwargs: Any) -> str:
        """Runs the tool logic and returns a string result."""
        pass


class CalculatorTool(Tool):
    """Simple tool for performing arithmetic operations."""

    def __init__(self) -> None:
        super().__init__(
            name="calculator",
            description="Use this tool for math operations. Input must be a valid Python expression like '2 + 2'.",
        )

    def execute(self, **kwargs: Any) -> str:
        expression = kwargs.get("expression")
        if not expression:
            return "Error: 'expression' not provided for calculator tool."
        try:
            # Note: In production, avoid eval() for security.
            # Use a safer library like 'numexpr' or 'simpleeval'.
            result = eval(expression)
            return str(result)
        except Exception as e:
            return f"Error evaluating expression: {str(e)}"


class GCSWriterTool(Tool):
    """Mock tool for writing data to Google Cloud Storage."""

    def __init__(self) -> None:
        super().__init__(
            name="gcs_writer",
            description="Use this to save files or data to GCS. Input: {'filename': 'str', 'content': 'str'}",
        )

    def execute(self, **kwargs: Any) -> str:
        filename = kwargs.get("filename")
        content = kwargs.get("content")
        if not filename or not content:
            return "Error: 'filename' or 'content' not provided for GCS writer tool."
        # Simulated GCS write
        return f"Successfully saved '{filename}' to bucket 'llmops-outputs'."


class ToolRegistry:
    """Registry to manage and retrieve tools for the Agent."""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}
        # Register default tools
        self.register(CalculatorTool())
        self.register(GCSWriterTool())

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def get_tool_descriptions(self) -> str:
        return "\n".join([f"- {t.name}: {t.description}" for t in self._tools.values()])
