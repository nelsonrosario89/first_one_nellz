"""Lab 4 – IAM MFA enforcement evidence collector.

Lists every IAM user in the account, determines whether they have at least one
MFA device assigned, publishes a Security Hub finding per user, and optionally
writes a CSV summary to an evidence bucket.

CLI usage::

    python mfa_check.py --evidence-bucket <bucket> [--region us-east-1]

Environment variables respected:
    AWS_REGION, AWS_DEFAULT_REGION

The script is idempotent and safe to run from GitHub Actions or Lambda.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import logging
import os
import sys
from io import StringIO
from typing import Dict, List, Any, Optional

import boto3
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

ACCOUNT_ID = boto3.client("sts").get_caller_identity()["Account"]
PRODUCT_ARN_FMT = (
    "arn:aws:securityhub:{region}:{account}:product/{account}/default"
)
FINDING_ID_FMT = "iam-user-mfa-{user}"

CSV_HEADERS = [
    "UserName",
    "CreateDate",
    "PasswordEnabled",
    "MFAEnabled",
]


def list_users(iam_client) -> List[Dict[str, Any]]:
    paginator = iam_client.get_paginator("list_users")
    users: List[Dict[str, Any]] = []
    for page in paginator.paginate():
        users.extend(page["Users"])
    return users


def user_has_mfa(iam_client, username: str) -> bool:
    try:
        resp = iam_client.list_mfa_devices(UserName=username)
        return len(resp["MFADevices"]) > 0
    except ClientError as e:
        logger.error("Could not list MFA devices for %s – %s", username, e)
        return False


def create_finding(user: Dict[str, Any], region: str, mfa_enabled: bool) -> Dict[str, Any]:
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    sev = 0.0 if mfa_enabled else 8.0
    status = "PASSED" if mfa_enabled else "FAILED"
    username = user["UserName"]
    return {
        "SchemaVersion": "2018-10-08",
        "Id": FINDING_ID_FMT.format(user=username),
        "ProductArn": PRODUCT_ARN_FMT.format(region=region, account=ACCOUNT_ID),
        "GeneratorId": "iam-mfa-enforcement-check",
        "AwsAccountId": ACCOUNT_ID,
        "Types": [
            "Software and Configuration Checks/MFA"
        ],
        "FirstObservedAt": now,
        "CreatedAt": now,
        "UpdatedAt": now,
        "Severity": {"Normalized": int(sev)},
        "FindingProviderFields": {
            "Severity": {"Label": "INFORMATIONAL" if mfa_enabled else "HIGH"},
            "Types": [
                "Software and Configuration Checks/MFA"
            ]
        },
        "Title": f"IAM user '{username}' MFA enforcement check",
        "Description": (
            "User has MFA enabled." if mfa_enabled else "User does NOT have MFA enabled."
        ),
        "Resources": [
            {
                "Type": "AwsIamUser",
                "Id": user["Arn"],
                "Region": region,
            }
        ],
        "Compliance": {"Status": status},
        "RecordState": "ACTIVE",
    }


def write_csv(rows: List[Dict[str, Any]]) -> str:
    buf = StringIO()
    writer = csv.DictWriter(buf, fieldnames=CSV_HEADERS)
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


def _sanitize_bucket_name(value: str) -> str:
    v = value.strip()
    if v.startswith("s3://"):
        v = v[len("s3://") :]
    v = v.split("/", 1)[0]
    return v


def run(region: str, evidence_bucket: Optional[str]) -> None:
    iam = boto3.client("iam", region_name=region)
    s3 = boto3.client("s3", region_name=region)
    sh = boto3.client("securityhub", region_name=region)

    users = list_users(iam)
    findings: List[Dict[str, Any]] = []
    csv_rows: List[Dict[str, Any]] = []

    for user in users:
        username = user["UserName"]
        mfa_enabled = user_has_mfa(iam, username)
        findings.append(create_finding(user, region, mfa_enabled))
        csv_rows.append(
            {
                "UserName": username,
                "CreateDate": user["CreateDate"].strftime("%Y-%m-%d"),
                "PasswordEnabled": "true" if user.get("PasswordLastUsed") else "false",
                "MFAEnabled": str(mfa_enabled).lower(),
            }
        )
        logger.info("%s – MFA enabled=%s", username, mfa_enabled)

    # Batch import findings
    for i in range(0, len(findings), 100):
        sh.batch_import_findings(Findings=findings[i : i + 100])

    if evidence_bucket:
        evidence_bucket = _sanitize_bucket_name(evidence_bucket)
    if evidence_bucket:
        key_prefix = "iam-mfa-audit/"
        timestamp = dt.datetime.utcnow().strftime("%Y-%m-%dT%H%M%SZ")
        key = f"{key_prefix}mfa-users-{timestamp}.csv"
        s3.put_object(
            Bucket=evidence_bucket,
            Key=key,
            Body=write_csv(csv_rows).encode(),
        )
        logger.info("Uploaded CSV evidence to s3://%s/%s", evidence_bucket, key)

    logger.info("Completed MFA check: users=%d", len(users))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Detect IAM users without MFA and create Security Hub findings.")
    parser.add_argument("--evidence-bucket", help="S3 bucket to upload CSV (optional)")
    parser.add_argument("--region", default=os.getenv("AWS_REGION", "us-east-1"))
    args = parser.parse_args()

    try:
        run(region=args.region, evidence_bucket=args.evidence_bucket)
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Error running MFA check: %s", exc)
        sys.exit(1)
