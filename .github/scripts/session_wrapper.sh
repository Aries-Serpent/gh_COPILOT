#!/bin/bash
# session_wrapper.sh
# Utilities for preserving command sessions and recovering metadata.

set -euo pipefail

SESSION_DIR="$HOME/.gh_copilot_sessions"

setup_session_preservation() {
    mkdir -p "$SESSION_DIR"
}

wrap_command() {
    setup_session_preservation
    local cmd="$*"
    local session_id
    if command -v uuidgen >/dev/null 2>&1; then
        session_id=$(uuidgen)
    else
        session_id=$(date +%s)
    fi
    local log_file="$SESSION_DIR/${session_id}.log"
    bash -c "$cmd" &> "$log_file"
    local status=$?
    cat >"$SESSION_DIR/${session_id}.json" <<METAEOF
{"session_id":"$session_id","command":"$cmd","status":$status,"log":"$log_file"}
METAEOF
    echo "$session_id"
    return $status
}

recover_session() {
    local session_id="$1"
    local file="$SESSION_DIR/${session_id}.json"
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
        setup_session_preservation)
            setup_session_preservation
            ;;
        wrap_command|wrap)
            wrap_command "$@"
            ;;
        recover_session)
            recover_session "$@"
            ;;
        *)
            echo "Usage: $0 {setup_session_preservation|wrap_command|recover_session}" >&2
            exit 1
            ;;
    esac
fi
