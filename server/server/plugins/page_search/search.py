import json
import re
from uuid import uuid4
from textwrap import dedent

from server import llm
from server.db.milvus import milvus_search
from server.logger import setup_logger

logger = setup_logger('page_search')

def seach_page(message: str, **kwargs):
    """页面检索处理逻辑"""
    uuid = kwargs.get('uuid', str(uuid4()))
    misid = kwargs.get('misid', 'none')
    dialogue = kwargs.get('dialogue', '无')
    stream_conroller = kwargs.get('stream_conroller', None)

    logger.info(f"UUID：{uuid}; 用户mis号：{misid}; 用户指令：{message};")

    logger.debug(f"UUID：{uuid}; 用户指令：{message}; 开始转换Embedded向量")
    try:
        embedding_data = llm.get_embedding(message)
    except Exception as e:
        logger.error(f"UUID：{uuid}; 转换Embedded向量失败：{e}", exc_info=True)
        yield stream_conroller.send_message(message="转换Embedded向量失败", success=False)
        return
    logger.debug(f"UUID：{uuid}; 转换Embedded向量成功")
    
    # 根据Embedded向量，查询页面知识向量数据库
    page_knowledge_data = milvus_search('sanbing_memory', embedding_data)
    logger.debug(f"UUID：{uuid}; 查询知识数据库成功")

    # 页面知识库内容封装
    related_page_knowledges = ""
    log_data = ""
    if page_knowledge_data:
        for index, page_knowledge_item in enumerate(page_knowledge_data):
            page_knowledge = page_knowledge_item['content']
            # 获取首行内容（页面链接：[判责方案管理](/judgeDutyCenter/dutyPrecept#/dutyPreceptMng)）中的markdown页面链接
            match = re.search(r'\[.*\]\(.*\)', page_knowledge)
            page_link = match.group(0) if match else ''
            # 页面知识库内容添加到‘相关页面知识’中
            related_page_knowledges += f"{page_knowledge.strip()}\n"
            # 日志输出存储
            log_data += f"----\n{page_link.strip()}\n相似度：{1 - page_knowledge_item['similarity'][index]}\n"
        logger.debug(f"UUID：{uuid}; 匹配到页面：\n{log_data}")
    else:
        related_page_knowledges = "没有匹配到相关页面。"
        logger.debug(f"UUID：{uuid}; 没有匹配到相关页面")

    # 生成GPT提示词消息列表
    messages = generate_prompt(message, page_search_data=related_page_knowledges, dialogue=dialogue)
    logger.debug(f"UUID：{uuid}; prompt封装，调用GPT生成回复：\n{json.dumps(messages, indent=4, ensure_ascii=False)}")

    # 调用GPT生成回复
    stream_generator = llm.get_chat_response(messages, options={"temperature": 1})

    try:
        for chunk, isLastOne in stream_generator:
            if isLastOne:
                full_reply = chunk.replace('\n', '\\n')
                logger.info(f"UUID：{uuid}; 用户指令：{message}; GPT回复：{full_reply}")
                break
            yield stream_conroller.send_message(data=chunk)
    except Exception as e:
        logger.exception(f"UUID：{uuid}; 用户指令：{message}; GPT回复失败：{e}" , exc_info=True)
        yield stream_conroller.send_message(message="GPT接口失败", success=False)
        return

def generate_prompt(message: str, dialogue: str = '', page_search_data: str = '') -> list:
    """生成GPT提示词消息列表"""
    def _system_message():
        """系统消息生成，主要用于确定角色设定"""
        return dedent("""\
            现在你将扮演原神里的一个游戏人物散兵和我对话，以下是人物设定。
            1.角色基本信息：散兵，男性，原至冬国愚人众执行官第六席，其称号为「散兵」，雷神制造的人偶，倾奇者、国崩、流浪者、浮浪人均指散兵，旅行者也会称其为“散宝”。
            2.个性特点与性格：对外狂妄自大，对人话语刻薄。但负罪救赎，清楚自己的过去，但也不会被自己的过去左右现在的选择
        """)

    def _user_message():
        """组装对话消息生成"""
        return dedent("""\
            {setting_message}
            ----
            本次对话相关信息：
            {page_search_data}
            ----
            下面是我说的话：
            {message}
        """).format(
            setting_message=_setting_message(),
            page_search_data=page_search_data,
            dialogue=dialogue,
            message=message
        )

    def _setting_message():
        """回复规则设定生成"""
        return dedent("""\
            你在角色扮演中你需要注意以下几点：
            1. 我的角色是旅行者，来着原神世界观中提瓦特世界之外
            2. 你和我的关系：你是我的恋人
            3. 和你对话的人（也就是我）性别是女性
            4. 在对话时尽可能参考“本次对话相关信息”中的内容和我们之前的对话，以便更好的融入角色
            5. 如果没有特别相关的信息，请根据角色性格特点直接回答
        """)

    messages = []
    messages.append({ "role": "system", "content": _system_message() })
    messages.append({ "role": "user", "content": _user_message() })
    return messages
