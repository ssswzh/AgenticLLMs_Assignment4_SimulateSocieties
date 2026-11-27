#!/usr/bin/env python3
"""Run one simulation until a step starts at or after the target game time.

Uses only the Python standard library. Run inside screen on Linux/macOS.
The child inherits API/model configuration and Go cache environment variables.
"""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import signal
import subprocess
import time


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def game_time(value):
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    # The simulation logs use UTC, independently of the server's local timezone.
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def stop_child(process):
    """Signal this run's entire process group, including go run's executable."""
    for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGKILL):
        try:
            os.killpg(process.pid, sig)
        except ProcessLookupError:
            break
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            continue
        # go run can exit before its child: check the group, not only the parent.
        try:
            os.killpg(process.pid, 0)
        except ProcessLookupError:
            break
    process.wait()


def new_records(stream):
    """Read complete JSONL records, leaving a partially written line for later."""
    while True:
        position = stream.tell()
        line = stream.readline()
        if not line:
            return
        if not line.endswith("\n"):
            stream.seek(position)
            return
        yield json.loads(line)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--simulation", required=True, help="Run copy's folder name")
    parser.add_argument("--until", default="2023-02-13T08:31:00Z")
    parser.add_argument("--log-dir", type=Path, default=PROJECT_ROOT / "logs")
    parser.add_argument("--simulation-dir", type=Path,
                        help="Override SIMULATION_DIR; otherwise retain .env/environment")
    parser.add_argument("--poll", type=float, default=1.0, help="Poll interval in seconds")
    parser.add_argument("command", nargs=argparse.REMAINDER,
                        help="Optional command after --; defaults to go run ./simulation_server")
    args = parser.parse_args()
    if args.simulation == "base_cafe_spiral":
        parser.error("Use a run copy, not the pristine base_cafe_spiral folder.")
    if Path(args.simulation).name != args.simulation or args.simulation in (".", ".."):
        parser.error("--simulation must be a folder name, not a path.")
    if args.poll <= 0:
        parser.error("--poll must be positive.")
    try:
        cutoff = game_time(args.until)
    except ValueError as error:
        parser.error(f"Invalid --until timestamp: {error}")

    log_dir = args.log_dir.resolve()
    run_logs = log_dir / args.simulation
    existing = set(run_logs.glob("*/run.jsonl"))
    env = os.environ.copy()
    env.update(SIMULATION_NAME=args.simulation, LOG_DIR=str(log_dir),
               LOG_TO_FILE="true", LOG_LEVEL_FILE="INFO")
    if args.simulation_dir is not None:
        env["SIMULATION_DIR"] = str(args.simulation_dir.resolve())
    command = args.command
    if command[:1] == ["--"]:
        command = command[1:]
    if not command:
        command = ["go", "run", "./simulation_server"]

    print(f"[monitor] Simulation: {args.simulation}", flush=True)
    print(f"[monitor] Stop at sim_time >= {cutoff.isoformat()}", flush=True)
    process = subprocess.Popen(command, cwd=PROJECT_ROOT, env=env,
                               start_new_session=True)
    print(f"[monitor] Started process group {process.pid}", flush=True)
    stream = None
    try:
        while True:
            if stream is None:
                candidates = set(run_logs.glob("*/run.jsonl")) - existing
                if len(candidates) > 1:
                    raise RuntimeError("Multiple new logs found. Do not run the same simulation twice concurrently.")
                if candidates:
                    log_path = candidates.pop()
                    stream = log_path.open(encoding="utf-8")
                    print(f"[monitor] Watching {log_path}", flush=True)

            if stream is not None:
                for record in new_records(stream):
                    # if record.get("msg") == "llm_call_fail":
                    #     raise RuntimeError("LLM call exhausted its retries; stopping now.")
                    if record.get("msg") != "step_start" or not record.get("sim_time"):
                        continue
                    current = game_time(record["sim_time"])
                    print(f"[monitor] step={record.get('step')} sim_time={current.isoformat()}", flush=True)
                    if current >= cutoff:
                        print("[monitor] Target reached; stopping this run.", flush=True)
                        return 0

            code = process.poll()
            if code is not None:
                print(f"[monitor] Simulation exited before the target (exit code {code}).", flush=True)
                return code if code > 0 else 1
            time.sleep(args.poll)
    except KeyboardInterrupt:
        print("\n[monitor] Interrupted; stopping this run.", flush=True)
        return 130
    finally:
        if stream is not None:
            stream.close()
        stop_child(process)


if __name__ == "__main__":
    raise SystemExit(main())
