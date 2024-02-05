from pymilvus import CollectionSchema, Collection, FieldSchema, DataType
import csv
import json
import os

def init_collection(collection_name: str, description: str = None):
    """
    初始化集合数据
    """
    id = FieldSchema(
        name="id",
        dtype=DataType.INT64,
        is_primary=True,
    )
    content = FieldSchema(
        name="content",
        dtype=DataType.VARCHAR,
        max_length=20000,
    )
    title = FieldSchema(
        name="title",
        dtype=DataType.VARCHAR,
        max_length=200,
    )
    embedding = FieldSchema(
        name="embedding",
        dtype=DataType.FLOAT_VECTOR,
        dim=1536 # OpenAI 向量化后的向量list长度
    )
    schema = CollectionSchema(
        fields=[id, content, title, embedding],
        description=description,
        enable_dynamic_field=True
    )

    # 创建集合
    collection = Collection(
        name=collection_name,
        schema=schema,
        using='default',
        shards_num=2
    )
    collection.create_index(field_name="embedding", index_params={"metric_type": "L2"})

    # 计算数据文件路径
    relative_path = f"server/db/milvus/init_data/{collection_name}.csv"
    file_path = os.path.join(os.getcwd(), relative_path)
    
    # 读取数据文件，并导入数据
    try:
        with open(file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
            connetcion_data = []
            for index, row in enumerate(reader):
                # 使用行序号index作为id
                connetcion_data.append({
                    "id": index+1,
                    "content": row['content'],
                    "title": row['title'],
                    "embedding": json.loads(row['embedding'])
                })
            
            collection.insert(connetcion_data)
    except Exception as e:
        # 导入数据异常时，删除集合
        collection.drop()
        raise e         
    
    collection.flush()
    print(f"初始化集合 {collection_name} 录入了 {collection.num_entities} 条数据", )
