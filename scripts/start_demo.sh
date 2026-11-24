#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$ROOT/backend"
FRONTEND_DIR="$ROOT/frontend"
LOG_DIR="${TMPDIR:-/tmp}/campus_market_demo"
mkdir -p "$LOG_DIR"
export PATH="$HOME/.local/bin:$PATH"

BACKEND_PID=""
PREVIEW_PID=""
TUNNEL_PID=""

cleanup() {
  echo
  echo "正在停止演示服务..."
  if [ -n "$TUNNEL_PID" ]; then kill "$TUNNEL_PID" 2>/dev/null || true; fi
  if [ -n "$PREVIEW_PID" ]; then kill "$PREVIEW_PID" 2>/dev/null || true; fi
  if [ -n "$BACKEND_PID" ]; then kill "$BACKEND_PID" 2>/dev/null || true; fi
  wait 2>/dev/null || true
}
trap cleanup EXIT INT TERM

cd "$BACKEND_DIR"
if [ ! -x .venv/bin/python ]; then
  echo "未找到 backend/.venv，请先创建虚拟环境并安装依赖。"
  exit 1
fi

echo "启动后端 (127.0.0.1:8000)..."
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 \
  >"$LOG_DIR/backend.log" 2>&1 &
BACKEND_PID=$!

for _ in $(seq 1 30); do
  if curl -sf --max-time 1 http://127.0.0.1:8000/api/v1/health >/dev/null; then
    break
  fi
  sleep 1
done
if ! curl -sf --max-time 2 http://127.0.0.1:8000/api/v1/health >/dev/null; then
  echo "后端启动失败，日志：$LOG_DIR/backend.log"
  tail -n 30 "$LOG_DIR/backend.log" || true
  exit 1
fi
echo "后端就绪：http://127.0.0.1:8000"

echo "构建前端..."
cd "$FRONTEND_DIR"
npm run build >"$LOG_DIR/frontend-build.log" 2>&1 || {
  echo "前端构建失败，日志：$LOG_DIR/frontend-build.log"
  tail -n 30 "$LOG_DIR/frontend-build.log" || true
  exit 1
}

echo "启动前端预览 (127.0.0.1:8080)..."
npm run preview -- --host 127.0.0.1 --port 8080 \
  >"$LOG_DIR/frontend.log" 2>&1 &
PREVIEW_PID=$!

for _ in $(seq 1 30); do
  if curl -sf --max-time 1 http://127.0.0.1:8080/ >/dev/null; then
    break
  fi
  sleep 1
done
if ! curl -sf --max-time 2 http://127.0.0.1:8080/ >/dev/null; then
  echo "前端预览启动失败，日志：$LOG_DIR/frontend.log"
  tail -n 30 "$LOG_DIR/frontend.log" || true
  exit 1
fi
echo "本地演示地址：http://127.0.0.1:8080"

if [ "${1:-}" = "--no-tunnel" ]; then
  echo
  echo "已跳过 Cloudflare Tunnel，按 Ctrl+C 停止服务。"
  wait
  exit 0
fi

if ! command -v cloudflared >/dev/null 2>&1; then
  echo
  echo "未找到 cloudflared。可执行 scripts/install_cloudflared.sh 安装，"
  echo "或先使用 ./scripts/start_demo.sh --no-tunnel 在本机演示。"
  exit 1
fi

echo
echo "启动 Cloudflare Quick Tunnel..."
echo "提示：公网链接有效期内，任何拿到链接的人都可以访问，请演示结束后 Ctrl+C 关闭。"
echo
cloudflared tunnel --url http://127.0.0.1:8080 --no-autoupdate 2>&1 \
  | tee "$LOG_DIR/tunnel.log"
