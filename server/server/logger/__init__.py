import os
import logging
from logging.handlers import TimedRotatingFileHandler

def init_file_handler(logger_name: str, level=logging.WARNING):
    """
    初始化日志文件处理器
    参考博客：https://blog.csdn.net/turkeym4/article/details/113553247
    """
    # 日志等级与其后缀名映射
    level_map = {
        logging.DEBUG: ".debug",
        logging.INFO: "",
        logging.WARNING: ".warning",
        logging.ERROR: ".error",
    }
    # 日志文件夹名=/log/模块名
    log_folder_name = "logs" + os.sep + logger_name
    # 日志文件名
    log_file_name = f"{logger_name}{level_map[level]}.log"
    # 日志文件夹
    log_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)) + os.sep + log_folder_name
    # 文件夹不存在创建文件夹
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
    # 拼装日志文件路径
    log_file_path = log_folder + os.sep + log_file_name
    
    # 创建日志文件处理器，每天午夜轮换日志文件一次，最多保留30天的日志
    file_log_handler = TimedRotatingFileHandler(log_file_path, when='midnight', backupCount=30, encoding='UTF-8')
    # 设置日志文本的记录格式            发生时间         日志等级      日志信息文件名       函数名          行数        日志信息
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
    # 将日志记录器指定日志的格式
    file_log_handler.setFormatter(formatter)

    # 日志等级的设置
    file_log_handler.setLevel(level)

    return file_log_handler

def setup_logger(logger_name: str):
    """
    初始化日志记录器
    """
    logger = logging.getLogger(logger_name)
    debug_file_handler = init_file_handler(logger_name=logger_name, level=logging.DEBUG)
    info_file_handler = init_file_handler(logger_name=logger_name, level=logging.INFO)
    waring_file_handler = init_file_handler(logger_name=logger_name, level=logging.WARNING)

    logger.setLevel(logging.DEBUG)
    logger.addHandler(debug_file_handler)
    logger.addHandler(info_file_handler)
    logger.addHandler(waring_file_handler)

    return logger