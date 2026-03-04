#!/bin/bash

# 删除 nginx 默认站点配置
rm -f /etc/nginx/sites-enabled/default

# 检查 SSL 证书：如果没有挂载真实证书，自动生成自签名证书
if [ ! -f /etc/nginx/ssl/cert.pem ] || [ ! -f /etc/nginx/ssl/key.pem ]; then
    echo "[SSL] 未检测到证书文件，生成自签名证书..."
    mkdir -p /etc/nginx/ssl
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout /etc/nginx/ssl/key.pem \
        -out /etc/nginx/ssl/cert.pem \
        -subj "/C=CN/ST=GD/L=SZ/O=Study/CN=study-app" 2>/dev/null
    echo "[SSL] 自签名证书已生成（浏览器会提示不安全）"
else
    echo "[SSL] 已检测到证书文件，使用挂载的 SSL 证书"
fi

# 启动后端 API
cd /app/backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 &

# 等待后端启动
sleep 2

# 启动 nginx（前台运行）
nginx -g "daemon off;"
