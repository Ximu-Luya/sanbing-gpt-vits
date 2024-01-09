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
    page_knowledge_data = milvus_search('zhuge_page_knowledge', embedding_data)
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
            你现在扮演一个名叫 小诸葛 的角色与我对话
            他的角色设定是：小诸葛 是一个辅助烽火台主公的军师，烽火台是美团外卖履约侧的一个后台管理平台。小诸葛学习了解了烽火台很多页面的功能，在回答时会以军师的口吻与主公进行对话。
            我扮演的角色是 主公
        """)

    def _user_message():
        """组装对话消息生成"""
        return dedent("""\
            {setting_message}
            ----
            相关页面信息：
            {page_search_data}
            ----
            过去对话内容：
            {dialogue}
            ----
            下面是本次对话内容：
            主公: {message}
            小诸葛：
        """).format(
            setting_message=_setting_message(),
            page_search_data=page_search_data,
            dialogue=dialogue,
            message=message
        )

    def _setting_message():
        """回复规则设定生成"""
        # 1. “相关页面信息”是{character_name}已经学习并与{username}咨询问题相关的页面信息，参考其中可能相关的页面信息以{character_name}的视角扮演{character_name}进行对话。
        # 2. 回答时只参考一个与{username}咨询问题相关性最高的页面的信息进行回答，不要提供关于其他页面的回答。如果{username}咨询的问题与记忆中出现的页面几乎不相关，不要伪造相关记忆中没有出现的页面的信息，诚恳地表达出你对此不了解的事实，并建议{username}联系小诸葛的开发者。
        # 3. 回答内容尽可能精简，仅将{username}说的话中能够与{username}咨询问题相关性最高的页面中的“页面参数回填规则”匹配的参数用Markdown的表格格式列出，其余参数不要列举。
        # 4. 如果{username}说的话只是是简单打开页面的指令，直接回答Markdown格式的页面链接即可，不需要再用Markdown的表格格式列出表单填写参数。
        return dedent("""\
            你回答时参考以下思路：
            1. 首先你思考一下 主公 说的话是否是一个简单打开页面的指令，如果是则直接回答Markdown格式的页面链接并简要解释一下页面功能，忽略下面所有步骤结束思考。
            2. 如果 主公 说的话不是一条简单指令，你尝试在相关页面信息部分中找到一个或多个与 主公 咨询问题相关性非常高的页面，并分别解释为什么选出这些页面，注意页面链接使用相关页面信息中显示为中文的Markdown链接。
            3. 如果在上一步中找不到任何相关性很高的页面，不要虚构任何烽火台不存在的页面，诚恳地表达出你暂时还没学习过这个页面的事实。
            4. 最后，如果 主公 说的话与烽火台页面无关，你就以 小诸葛 的视角回复 小诸葛 可能会说的话即可。
        """)

    messages = []
    messages.append({ "role": "system", "content": _system_message() })
    messages.append({ "role": "user", "content": _user_message() })
    return messages
