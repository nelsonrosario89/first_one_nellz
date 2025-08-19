"""setup_check.py – quick environment validation

Checks:
1. Python runtime >= 3.11 (to match workflows)
2. AWS CLI available and can report its version.
3. boto3 package importable.

Exit codes:
 0 – all checks passed
 1 – one or more checks failed
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from importlib import metadata

REQUIRED_PYTHON_MAJOR = 3
REQUIRED_PYTHON_MINOR = 11


def check_python() -> bool:
    ver = sys.version_info
    ok = (ver.major, ver.minor) >= (REQUIRED_PYTHON_MAJOR, REQUIRED_PYTHON_MINOR)
    print(f"Python version: {ver.major}.{ver.minor}.{ver.micro} – {'OK' if ok else 'FAIL'}")
    return ok


def check_aws_cli() -> bool:
    aws_path = shutil.which("aws")
    if not aws_path:
        print("AWS CLI: not found – FAIL")
        return False
    try:
        output = subprocess.check_output([aws_path, "--version"], text=True)
        # sample output: aws-cli/2.15.0 Python/3.11.5 Linux/5.15.0 ...
        version = output.split()[0].split("/")[1]
        print(f"AWS CLI version: {version} – OK")
        return True
    except subprocess.CalledProcessError as exc:
        print(f"AWS CLI: error executing – {exc} – FAIL")
        return False


def check_boto3() -> bool:
    try:
        version = metadata.version("boto3")
        print(f"boto3 version: {version} – OK")
        return True
    except metadata.PackageNotFoundError:
        print("boto3: not installed – FAIL")
        return False


def main() -> None:
    checks = [check_python(), check_aws_cli(), check_boto3()]
    all_good = all(checks)
    print("✔ Environment looks good" if all_good else "✖ Environment validation failed")
    sys.exit(0 if all_good else 1)


if __name__ == "__main__":
    main()
