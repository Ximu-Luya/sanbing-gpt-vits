from flask import Blueprint, request, jsonify

from server.db.milvus import milvus_query, milvus_insert, milvus_delete, milvus_update
from server import llm

memory = Blueprint('memory', __name__)

# milvus 记忆创建
@memory.route('/api/memory/create', methods=['POST'])
def memory_create():
    data = request.get_json()
    memory_block = data['memory']
    if memory_block == "":
        return jsonify({"result": "失败，记忆片段为空"})
    print(memory_block)

    # 将记忆片段转为Embedding向量
    print('1. 将记忆片段转为Embedding向量')
    memory_block_embedding = llm.get_embedding(memory_block)

    print('2. 将记忆片段存入 Milvus 集合')
    res = milvus_insert('zhuge_page_knowledge', {
        'content': memory_block,  # content 字段的值
        'embedding': memory_block_embedding,  # embedding 字段的值
    })

    print('插入数据', res)
    return jsonify({"message": "记忆创建成功", "success": True})


# 知识检索
# @memory.route('/api/memory/get', methods=['GET'])
# def knowledge_get():
#     # 从知识库库中检索相关的知识片段
#     response = db.table('zhuege_knowledge_base').select('id', 'content').order('id').execute()
#     memories = response.data
#     print(f"获取到记忆 {memories.__len__()} 条")
#     return jsonify({"memories": memories})

# milvus知识检索
@memory.route('/api/memory/get', methods=['GET'])
def knowledge_get():
    # 从知识库库中检索相关的知识片段
    response = milvus_query('zhuge_page_knowledge')
    result = []
    for item in response:
        obj = {
            "id": str(item.get("id")),
            "content": item.get("content")
        }
        result.append(obj)
    print(f"获取到记忆 {result.__len__()} 条")
    return jsonify({"memories": result})


# 记忆删除
# @memory.route('/api/memory/delete', methods=['POST'])
# def memory_delete():
#     data = request.get_json()
#     memory_id = data['memoryId']
#
#     # 从记忆库中删除记忆片段
#     db.table('zhuege_knowledge_base').delete().eq('id', memory_id).execute()
#     return jsonify({"message": "记忆删除成功", "success": True})


# milvus记忆删除
@memory.route('/api/memory/delete', methods=['POST'])
def memory_delete():
    data = request.get_json()
    memory_id = data['memoryId']

    # 从记忆库中删除记忆片段
    res = milvus_delete('zhuge_page_knowledge', memory_id)
    print('delete', res)
    return jsonify({"message": "记忆删除成功", "success": True})

# milvus 记忆修改
@memory.route('/api/memory/update', methods=['POST'])
def memory_update():
    data = request.get_json()
    memory_id = data['memoryId']
    memory = data['memory']

    # 将修改后的记忆片段转为Embedding向量
    print("1. 将修改后的记忆片段转为Embedding向量")
    embedding_data = llm.get_embedding(memory)

    mr = milvus_update('zhuge_page_knowledge', {
        'id': int(memory_id),
        'content': memory,  # content 字段的值
        'embedding': embedding_data,  # embedding 字段的值
    })

    print(f"3. 记忆更新成功, {mr}")
    return jsonify({"message": "记忆更新成功", "success": True})
