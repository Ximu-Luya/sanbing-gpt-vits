# AI散兵GPT实时语音

![cover](./cover.png)

## 介绍
拥有散兵的记忆，模仿散兵的口吻，使用散兵的声音，现在与散宝开始对话吧！


## 前置要求

### Node

`node` 需要 `^16 || ^18 || ^19` 版本（`node >= 14` 需要安装 [fetch polyfill](https://github.com/developit/unfetch#usage-as-a-polyfill)），使用 [nvm](https://github.com/nvm-sh/nvm) 可管理本地多个 `node` 版本

```shell
node -v
```

### 后端

进入文件夹 `/server` 安装python依赖
```shell
pip install -r requirements.txt
```

运行命令，启动服务
```shell
flask run
```

### 前端
根目录下运行以下命令启动前端开发服务器

```shell
npm run dev
```

## 打包

### 使用 Docker（暂未完成）

#### Docker build & Run

```bash
docker build -t chatgpt-web .

# 前台运行
docker run --name chatgpt-web --rm -it -p 3002:3002 --env OPENAI_API_KEY=your_api_key chatgpt-web

# 后台运行
docker run --name chatgpt-web -d -p 3002:3002 --env OPENAI_API_KEY=your_api_key chatgpt-web

# 运行地址
http://localhost:3002/
```

#### Docker compose

```yml
version: '3'

services:
  app:
    image: chenzhaoyu94/chatgpt-web # 总是使用 latest ,更新时重新 pull 该 tag 镜像即可
    ports:
      - 3002:3002
    environment:
      # 二选一
      OPENAI_API_KEY: xxxxxx
      # 二选一
      OPENAI_ACCESS_TOKEN: xxxxxx
      # API接口地址，可选，设置 OPENAI_API_KEY 时可用
      OPENAI_API_BASE_URL: xxxx
      # API模型，可选，设置 OPENAI_API_KEY 时可用
      OPENAI_API_MODEL: xxxx
      # 反向代理，可选
      API_REVERSE_PROXY: xxx
      # 访问权限密钥，可选
      AUTH_SECRET_KEY: xxx
      # 超时，单位毫秒，可选
      TIMEOUT_MS: 60000
      # Socks代理，可选，和 SOCKS_PROXY_PORT 一起时生效
      SOCKS_PROXY_HOST: xxxx
      # Socks代理端口，可选，和 SOCKS_PROXY_HOST 一起时生效
      SOCKS_PROXY_PORT: xxxx
      # HTTPS 代理，可选，支持 http，https，socks5
      HTTPS_PROXY: http://xxxx:7890
```
- `OPENAI_API_BASE_URL`  可选，设置 `OPENAI_API_KEY` 时可用
- `OPENAI_API_MODEL`  可选，设置 `OPENAI_API_KEY` 时可用

### 手动打包

#### 前端网页

1、根目录下运行以下命令，然后将 `dist` 文件夹内的文件复制到你网站服务的根目录下

[参考信息](https://cn.vitejs.dev/guide/static-deploy.html#building-the-app)

```shell
pnpm build
```

## 常见问题
Q: 前端没有打字机效果？

A: 一种可能原因是经过 Nginx 反向代理，开启了 buffer，则 Nginx 会尝试从后端缓冲一定大小的数据再发送给浏览器。请尝试在反代参数后添加 `proxy_buffering off;`，然后重载 Nginx。其他 web server 配置同理。

## License
MIT © [ChenZhaoYu](./license)
