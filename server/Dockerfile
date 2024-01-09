# 使用精简版镜像
FROM python:3.9-slim

# 代码包拷贝
ADD ./  /app/server
# 设置工作目录
WORKDIR /app/server
ENV PYTHONPATH /app

# 使用清华源
RUN pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/
RUN pip3 config set install.trusted-host pypi.tuna.tsinghua.edu.cn
# 安装依赖，取消缓存，取消版本检查
RUN pip3 install -r requirements.txt --no-cache-dir --disable-pip-version-check

# 时区设置
RUN /bin/cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
&& echo 'Asia/Shanghai' >/etc/timezone

# 端口
EXPOSE 7777

# CMD ["python3", "/app/app.py"]  py文件启动方式

# gunicorn 启动
ENTRYPOINT ["gunicorn", "--config", "gunicorn.py", "app:app"]