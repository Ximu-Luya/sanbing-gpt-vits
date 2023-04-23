import json
import random
import requests
from flask import Flask, Response, stream_with_context, request, render_template, jsonify

# from control import *

BASE_REMOTE_URL = "https://api.deliveryai.social:3002/"
app = Flask(__name__, 
            static_url_path='/', 
            static_folder='static',
            template_folder="./static",
            )

@app.route('/')
def index():
    return render_template("index.html")
    
@app.route("/chat-process", methods=["POST"])
@app.route("/api/chat-process", methods=["POST"])
def chat_process():
    url = 'https://sanbing-gpt.vercel.app/api/docs'

    req_data = request.get_json()

    data = {'question': req_data['prompt']}

    # 发送 HTTPS 请求
    print('开始发送请求到sanbing-gpt')
    sanbing_gpt_response = requests.post(
        url, 
        json=data,
        stream = True
        )
        
    def generate():
        full_text = ''
        for chunk in sanbing_gpt_response.iter_content(chunk_size=1024):
            # 处理每个数据块
            if chunk:
                chunk_str = chunk.decode('utf-8')
                full_text += chunk_str
                print(full_text)
                yield chunk
    
    response = Response(stream_with_context(generate()), 
                    content_type = 'application/json')
    print('完成请求sanbing-gpt')
    return response

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port="3003")
