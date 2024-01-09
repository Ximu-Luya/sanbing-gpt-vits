import psutil
from time import sleep
from milvus import default_server

def check_milvus():
    """
    检测 Milvus Lite 服务是否已启动，若已启动则结束进程
    """
    for proc in psutil.process_iter():
        if "milvus" in proc.name():
            print(f"检测到 Milvus Lite 服务已启动……进程名：{proc.name()}，PID：{proc.pid}")
            sleep(.5)
            proc.kill()
            print(f"已结束进程 {proc.name()}")
            sleep(.5)

def start_milvus():
    """
    启动 Milvus Lite 服务
    """
    check_milvus()
    print("正在启动 Milvus Lite 服务……")
    # 启动 Milvus Lite 服务
    default_server.set_base_dir('milvus_data')
    default_server.config.set("proxy_port", 19530)
    default_server.config.set('system_log_level', 'warn')
    default_server.start()
    print("启动 Milvus Lite 服务 成功")