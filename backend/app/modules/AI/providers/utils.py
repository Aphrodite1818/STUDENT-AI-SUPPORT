#==========================#
#        UTILS.PY          #
#==========================#



from typing import Any


"""adds validation and ensure api_key for provider gets managed well"""
def require_api_key(api_key: str | None, provider_name: str) -> str:
    if not api_key:
        raise ValueError(f"{provider_name} API key is not configured")
    return api_key



"""normalize content of any type and returns a simple string """
def text_from_content(content: Any) -> str:
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        text_parts = []
        for part in content:
            if isinstance(part, str):
                text_parts.append(part)
            elif isinstance(part, dict):
                text = part.get("text")
                if isinstance(text, str):
                    text_parts.append(text)
        return "\n".join(text_parts)

    if content is None:
        return ""

    return str(content)

"""converts sdk model objects into plain python dictionaries"""
def model_to_dict(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(exclude_none=True)

    if hasattr(value, "to_dict"):
        return value.to_dict()

    if isinstance(value, list):
        return [model_to_dict(item) for item in value]

    if isinstance(value, dict):
        return {
            key: model_to_dict(item)
            for key, item in value.items()
        }

    return value

"""normalize tool calling to anthropic standard"""
def openai_tool_to_anthropic(tool: dict[str, Any]) -> dict[str, Any]:
    if tool.get("type") != "function":
        return tool

    function = tool.get("function", {})
    return {
        "name": function.get("name"),
        "description": function.get("description", ""),
        "input_schema": function.get("parameters", {"type": "object", "properties": {}}),
    }



"""normalize tool calling to gemini standard"""
def openai_tool_to_gemini_declaration(tool: dict[str, Any]) -> dict[str, Any]:
    if tool.get("type") != "function":
        return tool

    function = tool.get("function", {})
    return {
        "name": function.get("name"),
        "description": function.get("description", ""),
        "parameters_json_schema": function.get(
            "parameters",
            {"type": "object", "properties": {}},
        ),
    }
