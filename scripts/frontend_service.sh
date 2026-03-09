#!/bin/bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
FRONTEND_DIR="$PROJECT_DIR/frontend"
LOG_DIR="$PROJECT_DIR/logs"
PID_FILE="$LOG_DIR/frontend.pid"
LOG_FILE="$LOG_DIR/frontend.log"
HOST="${FRONTEND_HOST:-0.0.0.0}"
PORT="${FRONTEND_PORT:-5173}"
HEALTH_URL="http://127.0.0.1:${PORT}"

mkdir -p "$LOG_DIR"

is_pid_running() {
  local pid="$1"
  [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null
}

read_pid() {
  [[ -f "$PID_FILE" ]] && cat "$PID_FILE"
}

cleanup_stale_pid() {
  local pid
  pid="$(read_pid || true)"
  if [[ -n "${pid:-}" ]] && ! is_pid_running "$pid"; then
    rm -f "$PID_FILE"
  fi
}

wait_for_frontend() {
  local attempts="${1:-20}"
  local delay="${2:-1}"
  local i

  for ((i = 1; i <= attempts; i++)); do
    if curl -fsS "$HEALTH_URL" >/dev/null 2>&1; then
      return 0
    fi
    sleep "$delay"
  done

  return 1
}

spawn_detached() {
  local log_file="$1"
  shift

  if command -v setsid >/dev/null 2>&1; then
    setsid "$@" >>"$log_file" 2>&1 < /dev/null &
  else
    nohup "$@" >>"$log_file" 2>&1 < /dev/null &
  fi
  echo $!
}

start_frontend() {
  cleanup_stale_pid

  local pid
  pid="$(read_pid || true)"
  if [[ -n "${pid:-}" ]] && is_pid_running "$pid"; then
    echo "前端已在运行 (PID: $pid)"
    return 0
  fi

  if curl -fsS "$HEALTH_URL" >/dev/null 2>&1; then
    echo "前端正在运行，但未受当前脚本管理"
    return 0
  fi

  if [[ ! -f "$FRONTEND_DIR/package.json" ]]; then
    echo "未找到前端目录: $FRONTEND_DIR"
    return 1
  fi

  : > "$LOG_FILE"
  pid="$(spawn_detached "$LOG_FILE" npm --prefix "$FRONTEND_DIR" run dev -- --host "$HOST" --port "$PORT")"
  echo "$pid" > "$PID_FILE"

  if wait_for_frontend 20 1; then
    echo "前端启动成功 (PID: $pid, URL: http://127.0.0.1:${PORT})"
    return 0
  fi

  echo "前端启动失败，最近日志:"
  tail -n 40 "$LOG_FILE" || true
  rm -f "$PID_FILE"
  return 1
}

stop_frontend() {
  cleanup_stale_pid

  local pid
  pid="$(read_pid || true)"

  if [[ -n "${pid:-}" ]] && is_pid_running "$pid"; then
    kill "$pid" 2>/dev/null || true

    local i
    for ((i = 1; i <= 10; i++)); do
      if ! is_pid_running "$pid"; then
        rm -f "$PID_FILE"
        echo "前端已停止"
        return 0
      fi
      sleep 1
    done

    kill -9 "$pid" 2>/dev/null || true
    rm -f "$PID_FILE"
    echo "前端已强制停止"
    return 0
  fi

  local existing
  existing="$(pgrep -f "vite --host|npm --prefix .* run dev -- --host" || true)"
  if [[ -n "${existing:-}" ]]; then
    pkill -f "vite --host|npm --prefix .* run dev -- --host" 2>/dev/null || true
    rm -f "$PID_FILE"
    echo "前端已停止"
    return 0
  fi

  echo "前端未运行"
}

status_frontend() {
  cleanup_stale_pid

  local pid
  pid="$(read_pid || true)"

  if [[ -n "${pid:-}" ]] && is_pid_running "$pid"; then
    if curl -fsS "$HEALTH_URL" >/dev/null 2>&1; then
      echo "前端运行中 (PID: $pid, 健康检查通过)"
    else
      echo "前端进程存在但健康检查失败 (PID: $pid)"
    fi
    return 0
  fi

  if curl -fsS "$HEALTH_URL" >/dev/null 2>&1; then
    echo "前端正在运行，但未受当前脚本管理"
    return 0
  fi

  echo "前端未运行"
  return 1
}

case "${1:-}" in
  start)
    start_frontend
    ;;
  stop)
    stop_frontend
    ;;
  restart)
    stop_frontend || true
    start_frontend
    ;;
  status)
    status_frontend
    ;;
  *)
    echo "用法: $0 {start|stop|restart|status}"
    exit 1
    ;;
esac
