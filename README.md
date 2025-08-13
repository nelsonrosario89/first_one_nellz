# Python GRC Automation Toolkit

[![Lab 3 – S3 Public Check](https://github.com/nelsonrosario89/first_one_nellz/actions/workflows/lab3_s3_public_check.yml/badge.svg)](https://github.com/nelsonrosario89/first_one_nellz/actions/workflows/lab3_s3_public_check.yml)

This repository contains hands-on examples from **Section 3: Python for GRC Engineering**.

## Contents
| Path | Purpose |
|------|---------|
| `scripts/list_s3_buckets.py` | Collects all S3 bucket names & creation dates, exports `s3_buckets_report.xlsx`, and writes `s3_audit.log`. |
| `scripts/fafo_checker.py` | Week-3 (FAFO Case Study) control check – lists IAM users without MFA, exports `iam_users_without_mfa.xlsx`, and logs to `fafo_audit.log`. |
| `.vscode/settings.json` | VS Code workspace settings enabling Black formatting, Flake8 linting, import-organise-on-save, and pytest integration. |
| `requirements.txt` | Runtime dependencies (boto3, pandas, openpyxl, etc.). |
| `requirements-dev.txt` | Dev-only tools (black, flake8, isort, pytest). |

## Quick-start
1. **Create & activate the virtual environment** (already done once, repeat when you clone):
   ```bash
   python3 -m venv .venv        # create isolated environment
   source .venv/bin/activate    # activate it (use Scripts\activate on Windows)
   ```
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt         # runtime libs
   pip install -r requirements-dev.txt     # formatting / linting / tests
   ```
3. **Run the S3 bucket audit**:
   ```bash
   python scripts/list_s3_buckets.py
   ```
   • Output: `s3_buckets_report.xlsx` + `s3_audit.log`
4. **Run the IAM MFA compliance check**:
   ```bash
   python scripts/fafo_checker.py
   ```
   • Output: `iam_users_without_mfa.xlsx` + `fafo_audit.log`
5. **Exit codes for CI pipelines**
   | Script | Exit 0 | Exit 2 |
   |--------|--------|--------|
   | `fafo_checker.py` | All users compliant | One or more users lack MFA |

## Development workflows
* **Format & lint**: `black . && flake8` (runs inside `.venv`).
* **Run tests**: `pytest` (placeholder – add tests as scripts grow).
* **VS Code** will auto-format and lint on save thanks to `.vscode/settings.json`.

## Versioning
Tag conventions follow *SemVer* beginning with `v0.1`.

---
Feel free to extend these scripts with additional AWS controls (GuardDuty alerts, Config rule checks, etc.). Pull requests and issues are welcome!
