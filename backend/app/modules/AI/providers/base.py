#==========================#
#     BASE LLM PROVIDER    #
#==========================#




from abc import ABC, abstractmethod
from typing import Any


class BaseLLMProvider(ABC):

    @abstractmethod
    async def chat(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        Send messages to LLM provider.

        Returns standardized response:
        {
            "content": str,
            "tool_calls": list | None,
            "raw_response": Any
        }
        """
        raise NotImplementedError