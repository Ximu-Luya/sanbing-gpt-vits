from flask import Blueprint, request, stream_with_context, Response
import json
from uuid import uuid4

from server.plugins.page_search.search import seach_page
chat = Blueprint('chat', __name__)

@chat.route('/api/chat', methods=['POST'])
def chat_api():
    data = request.get_json()
    message = data.get('message', '')
    dialogue = data.get('dialogue', '无')
    misid = request.cookies.get('hd_user_mis', 'none')

    uuid = str(uuid4())
    stream_conroller = StreamConroller(uuid)

    # 如果用户没有输入，返回错误
    if message == '':
        return stream_conroller.send_message(message="用户消息不能为空", success=False)
    
    # 生成页面检索处理逻辑的生成器
    handler_steam_generator = seach_page(
        message,
        uuid=uuid,
        misid=misid,
        dialogue=dialogue,
        stream_conroller=stream_conroller
    )

    return Response(
        stream_with_context(handler_steam_generator),
        content_type='application/text'
    )

class StreamConroller:
    """
    流式接口数据控制器类
    """
    def __init__(self, uuid: str):
        self.uuid = uuid
        self.message_list = []

    def send_message(self, data: str= "", message: str = "", success: bool = True) -> str:
        message = { "uuid": self.uuid, "data": data, "message": message, "success": success }
        self.message_list.append(message)
        return ("\n" if self.message_list.__len__() > 1 else "") + json.dumps(message, ensure_ascii=False)