# gunicorn配置文件
bind = "0.0.0.0:7777" # 监听内网端口7777
workers = 1 # 并行工作的进程数
loglevel = 'debug' # 设置日志输出等级
# daemon = 'true' # 设置守护进程,将进程交给supervisor管理
timeout = 90 # 进程超时时间
errorlog = './logs/app.log' # 错误信息日志