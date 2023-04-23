# -*- coding=utf-8 -*- 
import requests

base_url = 'http://127.0.0.1:3002'


def fetchChatConfig():
    url =base_url + '/config'
    response = requests.post(url)

    print(response.status_code) # 打印响应状态码
    print(response.json()) # 打印 JSON 格式的响应数据


def fetchChatAPIProcess():
    url =base_url + '/chat'
    prompt = 'python和C++最大的不同是什么\n'
    conversationId = ''
    parentMessageId = ''
    data = {
        'prompt':prompt,
        'options':{
            'conversationId':conversationId,
            'parentMessageId':parentMessageId
        }
    }

    def on_download_progress(chunk, response, *args, **kwargs):
        total_size = int(response.headers.get('content-length', 0))
        bytes_downloaded = len(chunk)
        print(f"Downloaded {bytes_downloaded} bytes out of {total_size}")

    signal = False
    stream = True

    response = requests.post(
        url, 
        json=data, 
        signal=signal,
        stream=stream,
        hooks={'response': lambda r, *args, **kwargs: on_download_progress(r.content, r, *args, **kwargs)},
    )
    

    print(response.status_code) # 打印响应状态码
    print(response.json()) # 打印 JSON 格式的响应数据

def fetchSession():
    url =base_url + '/session'
    response = requests.post(url)

    print(response.status_code) # 打印响应状态码
    print(response.json()) # 打印 JSON 格式的响应数据

def fetchVerify():
    url =base_url + '/verify'
    data = {'token':123456}
    response = requests.post(url, json=data)

    print(response.status_code) # 打印响应状态码
    print(response.json()) # 打印 JSON 格式的响应数据



if __name__ == '__main__':
    # fetchChatConfig()
    fetchChatAPIProcess()
    # fetchSession()
    # fetchVerify()