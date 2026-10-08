![ci](https://github.com/Kavanga16/servercheck/actions/workflows/ci.yml/badge.svg)

# servercheck

A small Python command-line tool that classifies a server's CPU usage as `OK`, `WARN` or `ALERT`.
It prints plain text or JSON and returns exit codes, so it can be used in scripts and CI.

> Status: work in progress. The core CLI is finished and tested; a URL health-check command is planned (see Roadmap).

## Features

- CPU status: `OK`, `WARN` or `ALERT` (default thresholds: warn above 50, alert above 75)
- Text or JSON output (`--json`)
- Configurable thresholds through flags or environment variables
- Exit codes suitable for scripts and CI
- Verbose and quiet logging to stderr (`-v`, `-q`)
- Tested with `pytest`, linted and formatted with `ruff`, CI on GitHub Actions
- Makefile shortcuts (`make check`, `make fix`)

## Requirements

- Python 3.10 or newer
- (Optional) GNU Make for `make check`

## Install

PowerShell (Windows):

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

Git Bash:

```bash
py -m venv .venv
source .venv/Scripts/activate
python -m pip install -e .
```

## Usage

```bash
servercheck -n api -c 60          # text output
servercheck -n api -c 90 --json   # JSON output
python -m servercheck -n api -c 60
```

Example output:

```text
api        | CPU:  60% | STATUS: WARN
```

```json
{"name": "api", "cpu": 90, "status": "ALERT", "exit_code": 1}
```

## Thresholds

Thresholds can be set with `--warn` and `--alert` (highest priority) or with the environment
variables `SERVERCHECK_WARN` and `SERVERCHECK_ALERT`. They must satisfy `0 < warn < alert < 100`.

```bash
SERVERCHECK_WARN=10 SERVERCHECK_ALERT=20 servercheck -n api -c 15
```

## Exit codes

| Code | Meaning                                      |
|------|----------------------------------------------|
| 0    | OK or WARN                                   |
| 1    | ALERT                                        |
| 2    | Invalid arguments (CPU not in 0-100, bad thresholds) |

## Development

```bash
make check          # lint + format check + tests
make fix            # auto-fix lint and reformat
python -m pytest -q # tests only
```

## Project structure

- `servercheck/core.py`: pure logic (status, validation, URL check helper)
- `servercheck/cli.py`: argument parsing and output formatting
- `tests/`: unit tests, CLI tests and local HTTP server tests

## Roadmap

- URL health-check subcommand using the existing `check_url` helper
- More output formats and clearer error messages
