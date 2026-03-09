#!/bin/bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$PROJECT_DIR/logs"
PID_FILE="$LOG_DIR/backend.pid"
LOG_FILE="$LOG_DIR/backend.log"
HOST="${BACKEND_HOST:-0.0.0.0}"
PORT="${BACKEND_PORT:-8000}"
HEALTH_URL="http://127.0.0.1:${PORT}/health"
PYTHON_BIN="$PROJECT_DIR/venv/bin/python"

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

wait_for_health() {
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

start_backend() {
  cleanup_stale_pid

  local pid
  pid="$(read_pid || true)"
  if [[ -n "${pid:-}" ]] && is_pid_running "$pid"; then
    echo "FastAPI 已在运行 (PID: $pid)"
    return 0
  fi

  if curl -fsS "$HEALTH_URL" >/dev/null 2>&1; then
    echo "FastAPI 正在运行，但未受当前脚本管理"
    return 0
  fi

  if [[ ! -x "$PYTHON_BIN" ]]; then
    echo "未找到虚拟环境 Python: $PYTHON_BIN"
    return 1
  fi

  cd "$PROJECT_DIR"
  : > "$LOG_FILE"
  pid="$(spawn_detached "$LOG_FILE" "$PYTHON_BIN" -m uvicorn backend.main:app --host "$HOST" --port "$PORT")"
  echo "$pid" > "$PID_FILE"

  if wait_for_health 20 1; then
    echo "FastAPI 启动成功 (PID: $pid, URL: http://127.0.0.1:${PORT})"
    return 0
  fi

  echo "FastAPI 启动失败，最近日志:"
  tail -n 40 "$LOG_FILE" || true
  rm -f "$PID_FILE"
  return 1
}

stop_backend() {
  cleanup_stale_pid

  local pid
  pid="$(read_pid || true)"

  if [[ -n "${pid:-}" ]] && is_pid_running "$pid"; then
    kill "$pid" 2>/dev/null || true

    local i
    for ((i = 1; i <= 10; i++)); do
      if ! is_pid_running "$pid"; then
        rm -f "$PID_FILE"
        echo "FastAPI 已停止"
        return 0
      fi
      sleep 1
    done

    kill -9 "$pid" 2>/dev/null || true
    rm -f "$PID_FILE"
    echo "FastAPI 已强制停止"
    return 0
  fi

  local existing
  existing="$(pgrep -f "uvicorn backend.main:app" || true)"
  if [[ -n "${existing:-}" ]]; then
    pkill -f "uvicorn backend.main:app" 2>/dev/null || true
    rm -f "$PID_FILE"
    echo "FastAPI 已停止"
    return 0
  fi

  echo "FastAPI 未运行"
}

status_backend() {
  cleanup_stale_pid

  local pid
  pid="$(read_pid || true)"

  if [[ -n "${pid:-}" ]] && is_pid_running "$pid"; then
    if curl -fsS "$HEALTH_URL" >/dev/null 2>&1; then
      echo "FastAPI 运行中 (PID: $pid, 健康检查通过)"
    else
      echo "FastAPI 进程存在但健康检查失败 (PID: $pid)"
    fi
    return 0
  fi

  if curl -fsS "$HEALTH_URL" >/dev/null 2>&1; then
    echo "FastAPI 正在运行，但未受当前脚本管理"
    return 0
  fi

  echo "FastAPI 未运行"
  return 1
}

case "${1:-}" in
  start)
    start_backend
    ;;
  stop)
    stop_backend
    ;;
  restart)
    stop_backend || true
    start_backend
    ;;
  status)
    status_backend
    ;;
  *)
    echo "用法: $0 {start|stop|restart|status}"
    exit 1
    ;;
esac
