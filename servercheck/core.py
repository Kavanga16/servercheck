import urllib.error
import urllib.request


def cpu_status(cpu: int, warn: int, alert: int) -> str:
    if cpu > alert:
        return "ALERT"
    if cpu > warn:
        return "WARN"
    return "OK"


def validate_cpu(cpu: int) -> None:
    if cpu < 0 or cpu > 100:
        raise ValueError("CPU must be in range 0-100")


def validate_thresholds(warn, alert) -> None:
    if not (0 < warn < alert < 100):
        raise ValueError("Thresholds must satisfy 0 < warn < alert < 100")


def exit_code(status: str) -> int:
    mapping = {"OK": 0, "WARN": 0, "ALERT": 1}
    return mapping.get(status, 3)


def check_url(url: str, timeout_s: float) -> tuple[str, int]:
    try:
        with urllib.request.urlopen(url, timeout=timeout_s) as resp:
            status_code = resp.getcode()
            if 200 <= status_code < 300:
                return ("OK", status_code)
            else:
                return ("ALERT", status_code)
    except urllib.error.HTTPError as e:
        return ("ALERT", e.code)
    except Exception:
        return ("ALERT", 0)
