"""Run a Python script or module with session logging."""

import argparse
import subprocess
import sys
import uuid

from codex.logging.session_logger import SessionLogger


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run a Python script or module with session logging.",
    )
    parser.add_argument("--session-id", default="auto", help="UUID or 'auto'")
    parser.add_argument(
        "--user-msg",
        action="append",
        default=[],
        help="Optional user message(s) to record before running the target",
    )
    parser.add_argument("dash", nargs=1, help="-- separator")
    parser.add_argument(
        "target_and_args",
        nargs=argparse.REMAINDER,
        help="Python script path or '-m module' followed by arguments",
    )
    args = parser.parse_args()

    session_id = str(uuid.uuid4()) if args.session_id == "auto" else args.session_id
    if not args.target_and_args:
        print("No target provided. Example:")
        print("  python scripts/with_session_logging.py -- -- scripts/run_checks.py")
        sys.exit(2)

    logger = SessionLogger(session_id=session_id)
    with logger.session_context():
        for msg in args.user_msg:
            logger.log_message("user", msg)

        if args.target_and_args[0] == "-m":
            cmd = [sys.executable] + args.target_and_args
        else:
            target = args.target_and_args[0]
            rest = args.target_and_args[1:]
            cmd = [sys.executable, target, *rest]

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        assert proc.stdout is not None
        for line in proc.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()
            logger.log_message("assistant", line.rstrip("\n"))
        return_code = proc.wait()
        if return_code != 0:
            logger.log_message("system", f"child.exit_code={return_code}")
        sys.exit(return_code)


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()

