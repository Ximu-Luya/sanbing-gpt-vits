from .provider import openai
from .provider import azure
from .apikey_manager import ApikeyManager

# 配置所选API
api_name = "azure"

def get_embedding(text: str) -> list[float]:
    """
    获取文本的embedding
    """
    if api_name == "openai":
        return openai.get_embedding(text)
    elif api_name == "azure":
        return azure.get_embedding(text)
    else:
        raise ValueError(f"不支持的API名称: {api_name}")

def get_chat_response(message_list: list, options: dict = {}):
    """
    获取聊天回复
    """
    if api_name == "openai":
        return openai.get_chat_response(message_list, options)
    elif api_name == "azure":
        return azure.get_chat_response(message_list, options)
    else:
        raise ValueError(f"不支持的API名称: {api_name}")

__all__ = [
    'get_embedding',
    'get_chat_response',
    'ApikeyManager'
]