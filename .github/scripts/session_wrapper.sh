#!/bin/bash
# session_wrapper.sh
# Wrap commands with overflow protection and recover session output.

set -euo pipefail

SESSION_ROOT="${SESSION_WRAPPER_ROOT:-$HOME/.gh_copilot_sessions}"
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

wrap() {
    local cmd="$*"
    mkdir -p "$SESSION_ROOT"

    local session_id
    if command -v uuidgen >/dev/null 2>&1; then
        session_id=$(uuidgen)
    else
        session_id=$(date +%s)
    fi

    local session_dir="$SESSION_ROOT/$session_id"
    mkdir -p "$session_dir"
    local log_file="$session_dir/output.log"

    SESSION_ID="$session_id" MAX_LINE_LENGTH="${SESSION_WRAPPER_MAX_LINE_LENGTH:-1550}" \
        "$REPO_ROOT/tools/shell_buffer_manager.sh" "$cmd" >"$log_file" 2>&1
    local status=$?

    local chunk_size="${SESSION_WRAPPER_CHUNK_SIZE:-100000}"
    split -b "$chunk_size" -d -a 4 "$log_file" "$session_dir/chunk_" >/dev/null 2>&1
    rm "$log_file"

    cat >"$session_dir/metadata.json" <<EOF
{"session_id":"$session_id","command":"$cmd","status":$status}
EOF

    echo "$session_id"
    return $status
}

recover() {
    local session_id="$1"
    local session_dir="$SESSION_ROOT/$session_id"
    if [ ! -d "$session_dir" ]; then
        echo "Session $session_id not found" >&2
        return 1
    fi

    cat "$session_dir/metadata.json"
    for chunk in "$session_dir"/chunk_*; do
        [ -f "$chunk" ] && cat "$chunk"
    done
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

subcmd="$1"; shift
case "$subcmd" in
    setup_session_preservation)
        setup_session_preservation
        ;;
    wrap_command|wrap)
        wrap "$@"
        ;;
    recover_session|recover)
        recover "$@"
        ;;
    *)
        echo "Usage: $0 {setup_session_preservation|wrap_command|wrap|recover_session|recover}" >&2
        exit 1
        ;;
esac

