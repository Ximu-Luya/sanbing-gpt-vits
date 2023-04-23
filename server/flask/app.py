import json
import random
import requests
from flask import Flask, Response, stream_with_context, request, render_template, jsonify

from control import *

BASE_REMOTE_URL = "https://api.deliveryai.social:3002/"
app = Flask(__name__, 
            static_url_path='/', 
            static_folder='static',
            template_folder="./static",
            )

@app.route('/')
def index():
    return render_template("index.html")

def forward(path,request):
    # 获取HTTP请求的请求头
    headers = dict(request.headers)

    # 获取 HTTP 请求的数据
    data = request.get_data()

    # 构造 HTTPS 请求的 URL
    url = BASE_REMOTE_URL + path

    # 发送 HTTPS 请求
    req = requests.post(
        url, 
        headers=headers,
        data=data
    )

    # 构造 HTTP 响应
    resp = app.make_response(req.content)
    resp.headers['Content-Type'] = req.headers['Content-Type']
    return resp

@app.route("/chat-process", methods=["POST"])
@app.route("/api/chat-process", methods=["POST"])
def chat_process():

    # 获取HTTP请求的请求头
    headers = dict(request.headers)

    # 获取 HTTP 请求的数据
    data = request.get_json()

    stage = data['options'].get('conversationStage',0)
    print('当前stage:', stage)

    system_message = system_prompts[str(stage)]
    # print(system_message)

    data['options']['systemMessage'] = system_message
    print(data['options'])

    # 构造 HTTPS 请求的 URL
    url = BASE_REMOTE_URL + "/chat-process"

    # TODO：修改包装prompt
    wrapped_prompt = data['prompt']
    provideStatus = data['options'].get('provideStatus', None)
    if provideStatus == 1:
        print('进行prompt包装')
        waybill = data['options'].get('waybill', None)
        if waybill is not None:
            wrapped_prompt = wrap_prompt(wrapped_prompt, int(waybill))
            print(wrapped_prompt)
    else:
        print('未进行包装')
    data['prompt'] = wrapped_prompt

    print('历史数据在这！！！！！')
    print(data['options']['textHistory'])
    print('\n')

    # 发送 HTTPS 请求
    req = requests.post(
        url, 
        headers=headers,
        json=data,
        verify=True,
        stream = True
        )

    def generate():
        first = True
        ans = None
        for chunk in req.iter_lines(chunk_size=None):
            if chunk:
                json_info = json.loads(chunk.split(b'\n')[-1])
                chunk = json.dumps(json_info)
                ans = chunk
                if first:
                    yield chunk
                else:
                    yield '\n' + chunk
            first = False
        json_info = json.loads(ans.split('\n')[-1])
        text = json_info['text']
        next_stage = stage_transform(text, stage)
        parsed_waybill = parse_waybill(data, stage, text)
        if parsed_waybill is not None:
            json_info['waybill'] = str(parsed_waybill)
            print('订单号:',parsed_waybill)
            print('解析出来的订单是：\n',find_waybill_by_id(int(parsed_waybill)))
        json_info['conversationStage'] = next_stage
        json_info['showCandidateWaybill'] = whether_show_waybill_list(text, next_stage)
        json_info['provideStatus'] = where_provide_waybill_status(stage, next_stage)
        json_info['wrappedPrompt'] = wrapped_prompt
        chunk = json.dumps(json_info)


        print(text[:10],'...\t',end='')
        print('当前stage是:',stage,end='\t')
        print('下一stage是:',next_stage,end='\t')
        print('运单号是:',parsed_waybill,end='\t')
        print('后续时候提供状态:',json_info['provideStatus'])
        
        yield '\n'+chunk
    
    response = Response(stream_with_context(generate()), 
                    content_type = req.headers['content-type'])
    return response

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port="3003")
