from pymilvus import connections, Collection, utility
from .start_db import start_milvus

# 启动 Milvus Lite 服务
# start_milvus()

# 连接 Milvus Lite 服务
print("开始连接 Milvus Lite 服务……")
connections.connect(
    host='0.0.0.0',
    port=19530
)
print("连接 Milvus Lite 服务 成功")

from .init_db import init_collection
# 如果集合不存在，则初始化集合
if not utility.has_collection("sanbing_memory"):
    print("记忆数据集合不存在，初始化集合")
    init_collection("sanbing_memory", description="散兵记忆库")

# 加载集合
collections = {
    "sanbing_memory": Collection("sanbing_memory"),
}
for collection in collections.values():
    collection.load()

# 查询集合所有数据
def milvus_query(collection_name, **kwargs):
    # 选择数据库
    if collection_name not in collections:
        raise ValueError("Invalid collection name")
    collection = collections[collection_name]

    params = {
        'expr': 'id > 0',
        'output_fields': ['id', 'content', 'title'],
        **kwargs
    }
    res = collection.query(**params)
    response = sorted(res, key=lambda x: x['id'])

    return response


# 向量查询集合数据
def milvus_search(collection_name, embedding_data, **kwargs):
    # 选择数据库
    if collection_name not in collections:
        raise ValueError("Invalid collection name")
    collection = collections[collection_name]

    search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
    params = {
        "data": [embedding_data],
        "anns_field": "embedding",
        "param": search_params,
        "limit": 5,
        "expr": 'id > 0',
        "output_fields": ['id', 'content', 'title'],
        "consistency_level": "Strong",
        **kwargs
    }
    res = collection.search(**params)

    result = []
    for hits in res:  # type: ignore
        for hit in hits:
            result.append({
                "id": hit.entity.get('id'),
                "content": hit.entity.get('content'),
                "title": hit.entity.get('title'),
                "similarity": hits.distances
            })
    return result


# 向指定集合插入数据
def milvus_insert(collection_name, data):
    # 选择数据库
    if collection_name not in collections:
        raise ValueError("Invalid collection name")
    collection = collections[collection_name]

    # 查询最大id
    idQuery = milvus_query(collection_name)
    max_id = max(idQuery, key=lambda x: x['id'])['id']
    data['id'] = max_id + 1

    response = collection.insert([data])
    return response


# 删除指定集合的数据
def milvus_delete(collection_name, id):
    # 选择数据库
    if collection_name not in collections:
        raise ValueError("Invalid collection name")
    collection = collections[collection_name]

    response = collection.delete(expr=f"id in [{id}]")
    return response


# 更新指定集合的数据
def milvus_update(collection_name, data):
    # 选择数据库
    if collection_name not in collections:
        raise ValueError("Invalid collection name")
    collection = collections[collection_name]

    # 从记忆库中删除记忆片段
    collection.delete(expr=f"id in [{data['id']}]")

    # 从记忆库插入相同id记忆片段
    response = collection.insert([data])

    return response
