import time

steam_sleep_time = 0.01

# openai.api_key ="---"

def get_embedding(context: str):
    """
    获取文本的embedding

    Parameters:
        context(str): 文本
    Returns:
        embedding(list[float]): 文本的embedding值
    """
    # response = openai.Embedding.create(
    #     input=context,
    #     engine="embedding"
    # )
    # return response['data'][0]['embedding'] # type: ignore
    raise "暂不支持openai API"

def get_chat_response(message_list: list, options: dict = {}):
    """
    获取聊天回复
    
    Parameters:
        message_list(list): 消息列表
        options(dict): 模型请求配置项
    Returns:
        openai_generate(function): 回复生成器，流式获取聊天回复
    """
    # response = openai.ChatCompletion.create(
    #     engine="gpt35",
    #     messages=message_list,
    #     temperature=options.get('temperature', 0.7),
    #     max_tokens=options.get('max_tokens', 800),
    #     stream=True
    # )
    # def openai_generate():
    #     for chunk in response:
    #         # 处理每个数据块
    #         if chunk:
    #             chunk_str = chunk['choices'][0]['delta'].get('content', '') # type: ignore
    #             print(chunk_str, end="", flush=False)
    #             time.sleep(steam_sleep_time) # 接口响应过快，暂停20ms营造流式输出氛围
    #             yield chunk_str
    
    # return openai_generate
    raise "暂不支持openai API"