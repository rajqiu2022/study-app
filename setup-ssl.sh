#!/bin/bash
# =============================================
# 腾讯云免费 SSL 证书部署脚本
# 用法: bash setup-ssl.sh <证书zip文件路径>
# =============================================

set -e

SSL_DIR="/opt/ssl-certs"
CONTAINER_NAME="study-app"

echo "=== 腾讯云 SSL 证书部署工具 ==="

# 检查参数
if [ -z "$1" ]; then
    echo ""
    echo "用法: bash setup-ssl.sh <证书zip文件路径>"
    echo ""
    echo "步骤说明:"
    echo "  1. 登录腾讯云控制台 -> SSL 证书 -> 申请免费证书"
    echo "  2. 选择 TrustAsia DV 型（免费3个月）"
    echo "  3. 填写域名，完成验证（DNS 验证最方便）"
    echo "  4. 下载证书，选择 Nginx 格式"
    echo "  5. 上传 zip 到服务器，执行本脚本"
    echo ""
    echo "示例: bash setup-ssl.sh ~/my_domain.com_nginx.zip"
    echo ""
    echo "证书续期: 到期前去腾讯云重新申请，下载后再执行本脚本即可"
    exit 1
fi

ZIP_FILE="$1"

if [ ! -f "$ZIP_FILE" ]; then
    echo "错误: 文件 $ZIP_FILE 不存在"
    exit 1
fi

# 创建证书目录
mkdir -p "$SSL_DIR"

# 解压证书
echo "[1/4] 解压证书文件..."
TMP_DIR=$(mktemp -d)
unzip -o "$ZIP_FILE" -d "$TMP_DIR"

# 查找证书文件（腾讯云 Nginx 格式的证书结构）
CERT_FILE=$(find "$TMP_DIR" -name "*.pem" -path "*/Nginx/*" | head -1)
KEY_FILE=$(find "$TMP_DIR" -name "*.key" -path "*/Nginx/*" | head -1)

# 如果 Nginx 目录下没有，尝试直接找
if [ -z "$CERT_FILE" ]; then
    CERT_FILE=$(find "$TMP_DIR" -name "*_bundle.pem" -o -name "*fullchain.pem" -o -name "*.pem" | head -1)
fi
if [ -z "$KEY_FILE" ]; then
    KEY_FILE=$(find "$TMP_DIR" -name "*.key" | head -1)
fi

if [ -z "$CERT_FILE" ] || [ -z "$KEY_FILE" ]; then
    echo "错误: 无法在 zip 中找到证书文件 (.pem) 或密钥文件 (.key)"
    echo "请确保下载的是 Nginx 格式的证书"
    rm -rf "$TMP_DIR"
    exit 1
fi

echo "[2/4] 安装证书..."
cp "$CERT_FILE" "$SSL_DIR/cert.pem"
cp "$KEY_FILE" "$SSL_DIR/key.pem"
chmod 644 "$SSL_DIR/cert.pem"
chmod 600 "$SSL_DIR/key.pem"
rm -rf "$TMP_DIR"

echo "  证书: $SSL_DIR/cert.pem"
echo "  密钥: $SSL_DIR/key.pem"

# 验证证书信息
echo "[3/4] 验证证书..."
echo "  域名: $(openssl x509 -in "$SSL_DIR/cert.pem" -noout -subject 2>/dev/null | sed 's/.*CN = //')"
echo "  到期: $(openssl x509 -in "$SSL_DIR/cert.pem" -noout -enddate 2>/dev/null | sed 's/notAfter=//')"

# 重启容器
echo "[4/4] 重启容器以应用新证书..."
if docker ps --format '{{.Names}}' | grep -q "$CONTAINER_NAME"; then
    docker restart "$CONTAINER_NAME"
    echo ""
    echo "=== 证书部署完成！==="
    echo "容器已重启，新证书已生效。"
else
    echo ""
    echo "=== 证书已安装！==="
    echo "容器 $CONTAINER_NAME 未运行，请使用以下命令启动："
    echo ""
    echo "docker run -d --name $CONTAINER_NAME \\"
    echo "  -p 80:80 -p 443:443 \\"
    echo "  -v /opt/ssl-certs:/etc/nginx/ssl:ro \\"
    echo "  -v /app/backend/data:/app/backend/data \\"
    echo "  study-app"
fi

echo ""
echo "提示: 证书到期后，去腾讯云重新申请，再执行本脚本即可续期。"
