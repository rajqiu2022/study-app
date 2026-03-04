# ===== 阶段1: 构建前端 =====
FROM node:18-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install --registry=https://registry.npmmirror.com
COPY frontend/ ./
RUN npm run build

# ===== 阶段2: 运行环境 =====
FROM python:3.11-slim
WORKDIR /app

# 安装 nginx、openssl、ffmpeg（语音识别需要）、wget/unzip（下载模型用）
RUN apt-get update && apt-get install -y nginx openssl ffmpeg wget unzip && rm -rf /var/lib/apt/lists/*

# 创建 SSL 证书目录（实际证书通过 docker volume 挂载）
RUN mkdir -p /etc/nginx/ssl

# 安装 Python 依赖
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 下载 vosk 中文语音识别模型（约 42MB，离线识别无需外部服务）
RUN mkdir -p /app/vosk-model && \
    wget -q https://alphacephei.com/vosk/models/vosk-model-small-cn-0.22.zip -O /tmp/vosk-model.zip && \
    unzip -q /tmp/vosk-model.zip -d /tmp/ && \
    mv /tmp/vosk-model-small-cn-0.22/* /app/vosk-model/ && \
    rm -rf /tmp/vosk-model*

# 复制后端代码
COPY backend/ ./backend/

# 复制前端构建产物到 nginx
COPY --from=frontend-build /app/frontend/dist /usr/share/nginx/html

# nginx 配置（删除默认站点，避免冲突）
RUN rm -f /etc/nginx/sites-enabled/default
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 创建数据目录和上传目录
RUN mkdir -p /app/backend/data /app/backend/uploads

# 启动脚本
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

EXPOSE 80 443

CMD ["/app/start.sh"]
