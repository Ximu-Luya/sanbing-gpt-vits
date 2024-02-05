import json    
import time
import requests
from retrying import retry
from dotenv import load_dotenv
import os

from server.llm.apikey_manager import ApikeyManager

# 流式回复时的暂停时间
steam_sleep_time = 0.01

# 加载AZURE_API_KEY
load_dotenv()
azure_api_key = os.getenv('AZURE_API_KEY')
azure_base_url = os.getenv('AZURE_BASE_URL')

def get_embedding(context: str):
    """
    获取文本的embedding

    Parameters:
        context(str): 文本
    Returns:
        embedding(list[float]): 文本的embedding值
    """
    data = {
        "input": context
    }
    
    response = _request_data(
        url="/text-embedding-ada-002/embeddings?api-version=2023-06-01-preview",
        data=data
    )
    
    return response.json()['data'][0]['embedding']

def get_chat_response(message_list: list, options: dict = {}):
    """
    获取聊天回复
    
    Parameters:
        message_list(list): 消息列表
        options(dict): 模型请求配置项
    Returns:
        azure_generate(function): 回复生成器，流式获取聊天回复
    """
    data = {
        "messages": message_list,
        "temperature": options.get('temperature', 0.7),
        "max_tokens": options.get('max_tokens', 6000),
        "stream": True
    }
    
    response = _request_data(
        url='/gpt-35-turbo-16k/chat/completions?api-version=2023-03-15-preview',
        data=data,
        stream=True
    )

    def azure_generate():
        full_reply = ''
        for chunk in response.iter_lines():
            # 处理每个数据块
            if chunk:
                chunk_json_str = chunk.decode('utf-8').replace('data: ', '')

                if chunk_json_str == '[DONE]':
                    yield full_reply, True
                    return
                chunk_json = json.loads(chunk_json_str)
                full_reply += "" if not chunk_json['choices'] else chunk_json['choices'][0]['delta'].get('content', '')
                
                time.sleep(steam_sleep_time) # 新版接口响应过快，暂停一定时间营造流式输出氛围
                yield full_reply, False
    
    return azure_generate()

def _request_data(url: str, timeout: int = 5, **kwargs):
    """
    请求数据，默认5秒超时，并自带重试机制

    Parameters:
        url(str): 请求地址
        timeout(int): 超时时间
        kwargs(dict): 请求参数
    Returns:
        response(requests.): 请求响应
    """
    @retry(stop_max_attempt_number=5, wait_fixed=100, stop_max_delay=10000)
    def _request():
        headers = { "Api-Key": f"{azure_api_key}" }
        data = kwargs.get('data', {}) # 取出data参数
        stream = kwargs.get('stream', False) # 取出stream参数
        # Azure接口基础地址
        base_url = azure_base_url
        response = requests.post(
            url=f"{base_url}{url}",
            headers=headers,
            json=data,
            timeout=timeout,
            stream=stream
        )
        response.raise_for_status()
        return response
    
    response = _request()
    return response