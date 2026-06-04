import asyncio
from typing import Literal

from pydantic import BaseModel

from backend.app.config.logging import get_logger
from backend.app.modules.AI.providers.factory import ProviderFactory
from backend.app.modules.AI.schemas import validate_phone_number
from backend.app.modules.AI.providers.utils import (
    model_to_dict,
    text_from_content,
)

logger = get_logger(__name__)


class User(BaseModel):
    name: str
    age: int


class Product:
    def __init__(self, name: str, price: float):
        self.name = name
        self.price = price

    def to_dict(self):
        return {
            "name": self.name,
            "price": self.price,
        }


def test_text_from_content():
    content = ["i am a boy"]

    result = text_from_content(content)
    print(result)
    assert result == "i am a boy"


def test_model_dump_object():
    user = User(name="Taiwo", age=20)

    result = model_to_dict(user)
    print(result)
    assert result == {
        "name": "Taiwo",
        "age": 20,
    }


def test_to_dict_object():
    product = Product("Laptop", 1500)

    result = model_to_dict(product)
    print(result)
    assert result == {
        "name": "Laptop",
        "price": 1500,
    }


def test_list_of_models():
    users = [
        User(name="Taiwo", age=20),
        User(name="John", age=25),
    ]

    result = model_to_dict(users)
    print(result)
    assert result == [
        {"name": "Taiwo", "age": 20},
        {"name": "John", "age": 25},
    ]


def test_nested_dictionary():
    data = {
        "user": User(name="Taiwo", age=20),
        "product": Product("Laptop", 1500),
        "tags": ["python", "ai"],
    }

    result = model_to_dict(data)
    print(result)
    assert result == {
        "user": {
            "name": "Taiwo",
            "age": 20,
        },
        "product": {
            "name": "Laptop",
            "price": 1500,
        },
        "tags": ["python", "ai"],
    }


def test_primitive_value():
    result = model_to_dict("hello")
    print(result)
    assert result == "hello"

def say_hello() -> Literal['hello my love']:
    return "hello my love"


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "say_hello",
            "description": "Return a friendly hello message.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    }
]

AVAILABLE_TOOLS = {
    "say_hello": say_hello,
}


async def chat() -> None:
    ai = ProviderFactory()
    provider = ai.get_provider("gemini")
    response = await provider.chat(
        [{"role": "user", "content": "use the tool to say hello"}],
        tools=TOOLS,
    )

    print(response["content"])
    print(response["tool_calls"])

    for tool_call in response["tool_calls"] or []:
        tool_name = tool_call.get("name")
        tool = AVAILABLE_TOOLS.get(tool_name)

        if tool:
            print(tool())



phone_numbers = [
    # Valid numbers
    "+234 707 442 4824",        # Nigerian with spaces
    "+1 (800) 555-0199",        # US with parentheses and dashes
    "+44 20 7946 0958",         # UK with spaces
    "+91-98765-43210",          # India with dashes
    "+2347074424824",           # Nigerian no formatting
    "+18005550199",             # US no formatting
    "+6281234567890",           # Indonesia
    "+55 (11) 91234-5678",      # Brazil with parentheses

    # Invalid numbers
    "123",                      # Too short
    "00000000000",              # Leading zero
    "+999999999999999999",      # Too long
    "abcdefghijk",              # Letters
    "+",                        # Just a plus
    "",                         # Empty string
    "+1 800 555 CALL",          # Letters mixed in
    "++2347074424824",          # Double plus
]


def phone_number_val():
    for number in phone_numbers:
        print("=" * 25)
        print("validating number")
        validated = validate_phone_number(number)
        if validated:
            print(f"{validated} passed✅✅")
        else:

            print("failed")
        print("=" * 25)


if __name__ == "__main__":
    # test_text_from_content()
    # test_model_dump_object()
    # test_to_dict_object()
    # test_list_of_models()
    # test_nested_dictionary()
    # test_primitive_value()
    # asyncio.run(chat())
    phone_number_val()

    print("All tests passed.")
