"""Unit tests for mfa_check.create_finding schema compliance.

These tests focus on catching simple formatting errors – especially in the
`Types` array – that previously caused Security Hub to silently reject
findings. They do *not* attempt 100 % ASFF validation, just key fields.
"""
from __future__ import annotations

import re
from typing import Dict, Any

import pytest

# Import target module from labs path
import importlib.util
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "labs" / "lab4_mfa_enforcement" / "mfa_check.py"

spec = importlib.util.spec_from_file_location("mfa_check", MODULE_PATH)
assert spec and spec.loader, "Cannot load mfa_check.py"

mfa_check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mfa_check)  # type: ignore


@pytest.fixture(scope="module")
def sample_user() -> Dict[str, Any]:
    """Return minimal IAM user dict as returned by boto3 list_users."""
    return {
        "UserName": "testuser",
        "Arn": "arn:aws:iam::123456789012:user/testuser",
        "CreateDate": mfa_check.dt.datetime.now(mfa_check.dt.timezone.utc),
    }


def _assert_types_format(types):
    pattern = re.compile(r"^[^/]+/[^/]+(/[^/]+)?$")
    assert all(pattern.match(t) for t in types), "Invalid Types format found"


@pytest.mark.parametrize("mfa_enabled", [True, False])
def test_finding_schema_basic(sample_user, mfa_enabled):
    finding = mfa_check.create_finding(sample_user, region="us-east-1", mfa_enabled=mfa_enabled)

    # Required high-level keys
    for key in [
        "SchemaVersion",
        "Id",
        "ProductArn",
        "AwsAccountId",
        "Types",
        "Resources",
        "Compliance",
    ]:
        assert key in finding, f"Missing key {key}"

    # SchemaVersion
    assert finding["SchemaVersion"] == "2018-10-08"

    # Types formatting
    _assert_types_format(finding["Types"])
    _assert_types_format(finding["FindingProviderFields"]["Types"])  # type: ignore[index]

    # Compliance status matches flag
    expected_status = "PASSED" if mfa_enabled else "FAILED"
    assert finding["Compliance"]["Status"] == expected_status
