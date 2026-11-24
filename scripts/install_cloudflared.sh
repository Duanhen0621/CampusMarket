#!/usr/bin/env bash
set -euo pipefail

case "$(uname -m)" in
  x86_64|amd64) ASSET="cloudflared-linux-amd64" ;;
  aarch64|arm64) ASSET="cloudflared-linux-arm64" ;;
  *)
    echo "不支持的架构: $(uname -m)"
    exit 1
    ;;
esac

URL="${CLOUDFLARED_URL:-https://github.com/cloudflare/cloudflared/releases/latest/download/$ASSET}"
DEST="$HOME/.local/bin/cloudflared"
mkdir -p "$(dirname "$DEST")"

echo "下载 cloudflared:"
echo "  $URL"
echo "如果 GitHub 下载过慢，可以设置 CLOUDFLARED_URL 指向可信镜像后重试。"
echo

curl -fL --retry 5 --retry-delay 3 --max-time 1800 -o "$DEST.tmp" "$URL"
chmod +x "$DEST.tmp"
mv "$DEST.tmp" "$DEST"

echo "安装完成：$DEST"
"$DEST" --version
