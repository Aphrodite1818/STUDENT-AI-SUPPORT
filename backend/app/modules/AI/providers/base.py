#==========================#
#     BASE LLM PROVIDER    #
#==========================#


"""THIS DECLARES THE DEFAULT STANDARD FOR LLM PROVIDERS AND CAN BE ALTERED IN THE FUTURE"""

from abc import ABC, abstractmethod
from typing import Any


class BaseLLMProvider(ABC): 
    """class cannot be instantiated only inherited"""


    @abstractmethod
    async def chat(
        self,
        messages: list[dict[str, str]], # e.g dict{"role" : "user" , "content" : "---"}
        tools: list[dict[str, Any]] | None = None, #pass a list of tools dict{"academic":academic()} | None 
    ) -> dict[str, Any]: # must return a dictionary
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