import json
import boto3
from dataclasses import asdict
from mythme.model.chat import ChatContent, ChatMessage, ChatResponse
from mythme.utils.config import config
from mythme.utils.log import logger


def invoke_anthropic_chat(
    model: str,
    messages: list[ChatMessage],
    system_prompt: str | None = None,
) -> ChatResponse:

    bedrock_runtime = boto3.client(service_name="bedrock-runtime")

    request = {
        "anthropic_version": config.chat.anthropic_version,
        "max_tokens": config.chat.max_tokens,
        "messages": [asdict(message) for message in messages],
    }

    if system_prompt:
        request["system"] = system_prompt
    body = json.dumps(request)

    response = bedrock_runtime.invoke_model(
        body=body, modelId=config.chat.bedrock_models[model]
    )
    response_dict = json.loads(response.get("body").read())
    logger.debug(f"Bedrock response: {response_dict}")
    return ChatResponse(
        id=response_dict["id"],
        model=response_dict["model"],
        type=response_dict["type"],
        role=response_dict["role"],
        content=ChatContent(
            type=response_dict["content"][0]["type"],
            text=response_dict["content"][0]["text"],
        ),
    )
