# 启动chatgpt-web
sudo docker run \
    --name chatgpt-explore \
    -d \
    -p 3002:3002 \
    --env OPENAI_API_KEY=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 \
    --env SOCKS_PROXY_HOST=192.168.0.102 \
    --env SOCKS_PROXY_PORT=7890 \
    --env HTTPS_PROXY_HOST=192.168.0.102 \
    --env HTTPS_PROXY_PORT=7890 \
    --env HTTP_PROXY_HOST=192.168.0.102 \
    --env HTTP_PROXY_PORT=7890 \
    chatgpt-explore