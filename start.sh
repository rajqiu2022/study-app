#!/bin/bash

# 删除 nginx 默认站点配置
rm -f /etc/nginx/sites-enabled/default

# 启动后端 API
cd /app/backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 &

# 等待后端启动
sleep 2

# 启动 nginx（前台运行）
nginx -g "daemon off;"
