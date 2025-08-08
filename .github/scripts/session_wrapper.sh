#!/bin/bash
# session_wrapper.sh
# Utilities for wrapping commands with buffering and recovering session metadata.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BUFFER_MANAGER="$REPO_ROOT/tools/shell_buffer_manager.sh"
META_DIR="$REPO_ROOT/.session_meta"

wrap_command() {
    local cmd="$*"
    local session_id
    if command -v uuidgen >/dev/null 2>&1; then
        session_id=$(uuidgen)
    else
        session_id=$(date +%s)
    fi
    mkdir -p "$META_DIR"
    bash "$BUFFER_MANAGER" "$cmd"
    local status=$?
    cat >"$META_DIR/${session_id}.json" <<METAEOF
{"session_id":"$session_id","command":"$cmd","status":$status}
METAEOF
    echo "$session_id"
    return $status
}

recover_session() {
    local session_id="$1"
    local file="$META_DIR/${session_id}.json"
    if [ -f "$file" ]; then
        cat "$file"
    else
        echo "Session $session_id not found" >&2
        return 1
    fi
}

if [ "$#" -gt 0 ]; then
    cmd="$1"; shift
    case "$cmd" in
        wrap_command)
            wrap_command "$@"
            ;;
        recover_session)
            recover_session "$@"
            ;;
        *)
            echo "Unknown command: $cmd" >&2
            exit 1
            ;;
    esac
fi
