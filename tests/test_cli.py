import json
import os
import subprocess
import sys


def run_cli(*args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, "-m", "servercheck", *args]
    merged = os.environ.copy()
    if env:
        merged.update(env)
    return subprocess.run(cmd, capture_output=True, text=True, env=merged)


def test_cli_warn_text():
    r = run_cli("-n", "api", "-c", "60")
    assert r.returncode == 0
    assert "STATUS: WARN" in r.stdout
    assert r.stderr == ""


def test_cli_alert_json():
    r = run_cli("-n", "api", "-c", "90", "--json")
    assert r.returncode == 1
    data = json.loads(r.stdout)
    assert data["name"] == "api"
    assert data["cpu"] == 90
    assert data["status"] == "ALERT"
    assert data["exit_code"] == 1
    assert r.stderr == ""


def test_cli_out_of_range():
    r = run_cli("-n", "api", "-c", "200")
    assert r.returncode == 2
    assert r.stdout == ""
    assert "CPU must be in range 0-100" in r.stderr


def test_cli_verbose():
    r = run_cli("-n", "api", "-c", "60", "--verbose")
    assert r.returncode == 0
    assert "STATUS: WARN" in r.stdout
    assert "INFO:" in r.stderr


def test_cli_quiet_suppresses_info_logs():
    r = run_cli("-n", "api", "-c", "60", "--quiet")
    assert r.returncode == 0
    assert "STATUS: WARN" in r.stdout
    assert r.stderr.strip() == ""


def test_cli_thresholds_from_env_change_status():
    r = run_cli(
        "-napi",
        "-c",
        "60",
        env={"SERVERCHECK_WARN": "10", "SERVERCHECK_ALERT": "20"},
    )
    assert r.returncode == 1
    assert "STATUS: ALERT" in r.stdout


def test_cli_args_override_env_thresholds():
    r = run_cli(
        "-n",
        "api",
        "-c",
        "60",
        "--warn",
        "50",
        "--alert",
        "75",
        env={"SERVERCHECK_WARN": "10", "SERVERCHECK_ALERT": "20"},
    )
    assert r.returncode == 0
    assert "STATUS: WARN" in r.stdout


def test_cli_invalid_env_threshold():
    r = run_cli("-n", "api", "-c", "60", env={"SERVERCHECK_WARN": "abc"})
    assert r.returncode == 2
    assert r.stdout == ""
    assert "SERVERCHECK_WARN must be an integer" in r.stderr
