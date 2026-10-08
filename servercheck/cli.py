import argparse
import json
import logging
import os
import sys

from servercheck import __version__
from servercheck.core import cpu_status, exit_code, validate_cpu, validate_thresholds


def _env_int(name: str, default: int) -> int:
    """Read an integer from an environment variable, or return the default."""
    raw = os.getenv(name)
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        raise ValueError(f"{name} must be an integer, got {raw!r}") from None


def main() -> int:
    parser = argparse.ArgumentParser(description="Check server CPU and return status")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("-n", "--name", required=True, help="server name")
    parser.add_argument("-c", "--cpu", required=True, type=int, help="cpu usage (0-100)")
    parser.add_argument("--json", action="store_true", help="output in json")
    parser.add_argument("-v", "--verbose", action="store_true", help="verbose logs to stderr")
    parser.add_argument("-q", "--quiet", action="store_true", help="only errors to stderr")
    parser.add_argument("--warn", type=int, default=None, help="warn threshold (0-100)")
    parser.add_argument("--alert", type=int, default=None, help="alert threshold (0-100)")

    args = parser.parse_args()

    try:
        warn = args.warn if args.warn is not None else _env_int("SERVERCHECK_WARN", 50)
        alert = args.alert if args.alert is not None else _env_int("SERVERCHECK_ALERT", 75)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 2

    try:
        validate_thresholds(warn, alert)
    except ValueError:
        print("Invalid thresholds", file=sys.stderr)
        return 2

    level = logging.WARNING
    if args.verbose:
        level = logging.INFO
    if args.quiet:
        level = logging.ERROR

    logging.basicConfig(
        level=level,
        stream=sys.stderr,
        format="%(levelname)s: %(message)s",
    )

    name = args.name
    cpu = args.cpu

    logging.info("Parsed args: name=%s cpu=%s json=%s", name, cpu, args.json)

    try:
        validate_cpu(cpu)
    except ValueError:
        print("CPU must be in range 0-100", file=sys.stderr)
        return 2

    status = cpu_status(cpu, warn=warn, alert=alert)
    code = exit_code(status)

    if args.json:
        print(json.dumps({"name": name, "cpu": cpu, "status": status, "exit_code": code}))
    else:
        print(f"{name:10} | CPU: {cpu:>3}% | STATUS: {status}")

    return code


def cli() -> None:
    raise SystemExit(main())
