import json    
import time
import requests
from retrying import retry

from server.llm.apikey_manager import ApikeyManager

# 流式回复时的暂停时间
steam_sleep_time = 0.01

# Friday平台AppId
friday_appid_list = [
    "1660906310172266539",
    "1666413562438013011",
    "1666413564526923792",
    "1666413566410063959"
]

# Friday平台AppId轮询管理器
friday_appid_manager = ApikeyManager(friday_appid_list)

def get_embedding(context: str):
    """
    获取文本的embedding

    Parameters:
        context(str): 文本
    Returns:
        embedding(list[float]): 文本的embedding值
    """
    data = {
        "input": context,
        "model": "text-embedding-ada-002"
    }
    
    response = _request_data(
        url="/embeddings",
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
        friday_generate(function): 回复生成器，流式获取聊天回复
    """
    data = {
        "model": "gpt-3.5-turbo-0613",
        "messages": message_list,
        "temperature": options.get('temperature', 0.7),
        "max_tokens": options.get('max_tokens', 800),
        "stream": True
    }
    
    response = _request_data(
        url='/chat/completions',
        data=data,
        stream=True
    )

    def friday_generate():
        full_reply = ''
        for chunk in response.iter_lines():
            # 处理每个数据块
            if chunk:
                chunk_json_str = chunk.decode('utf-8').replace('data: ', '')

                if chunk_json_str == '[DONE]':
                    yield full_reply, True
                    return
                chunk_json = json.loads(chunk_json_str)
                # chunk_reply = chunk_json['choices'][0]['delta'].get('content', '')
                reply = chunk_json['content']
                if chunk_json['lastOne']:
                    full_reply = chunk_json['content']
                
                time.sleep(steam_sleep_time) # 接口响应过快，暂停一定时间营造流式输出氛围
                yield reply, False
    
    return friday_generate()

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
        headers = { "Authorization": f"Bearer {friday_appid_manager.get_apikey()}" }
        data = kwargs.get('data', {}) # 取出data参数
        stream = kwargs.get('stream', False) # 取出stream参数
        # Friday平台接口基础地址
        is_mock = False
        base_url = "http://yapi.bmp.sankuai.com/mock/3078/v1/openai/native" if is_mock else "https://aigc.sankuai.com/v1/openai/native"
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