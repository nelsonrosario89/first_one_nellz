"""Lab 3 – S3 public-access detector.

Scans every S3 bucket in the account and region for public ACL grants or bucket
policies that allow public ("*") principals. If public access is detected a
Security Hub finding is created / updated. Optionally writes a JSON summary to
an evidence bucket.

Execution:
    python s3_public_check.py --evidence-bucket <bucket> [--region us-east-1]

When run in GitHub Actions the script assumes the role credentials provided by
`aws-actions/configure-aws-credentials`.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import logging
import os
import sys
from typing import List, Dict, Any

import boto3
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

ACCOUNT_ID = boto3.client("sts").get_caller_identity()["Account"]
PRODUCT_ARN_FMT = (
    "arn:aws:securityhub:{region}:{account}:product/{account}/default"
)
FINDING_ID_FMT = "s3-public-access-{bucket}"


# ------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------

def bucket_is_public(s3_client, bucket: str) -> bool:
    """Return True if bucket ACL or policy grants public access."""
    try:
        acl = s3_client.get_bucket_acl(Bucket=bucket)
    except ClientError as e:
        logger.warning("%s: unable to fetch ACL – %s", bucket, e.response["Error"]["Code"])
        acl = {"Grants": []}

    for grant in acl.get("Grants", []):
        uri = grant.get("Grantee", {}).get("URI", "")
        if uri.endswith("#AllUsers") or uri.endswith("#AuthenticatedUsers"):
            return True

    # Check bucket policy
    try:
        policy_str = s3_client.get_bucket_policy(Bucket=bucket)["Policy"]
        policy = json.loads(policy_str)
        for stmt in policy.get("Statement", []):
            principal = stmt.get("Principal", {})
            if principal == "*" or principal.get("AWS") == "*":
                return True
    except ClientError as e:
        if e.response["Error"]["Code"] != "NoSuchBucketPolicy":
            logger.warning("%s: unable to fetch policy – %s", bucket, e.response["Error"]["Code"])
    return False


def create_finding(bucket: str, region: str, public: bool) -> Dict[str, Any]:
    now = dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc).isoformat()
    sev = 8.0 if public else 0.0
    status = "FAILED" if public else "PASSED"
    return {
        "SchemaVersion": "2018-10-08",
        "Id": FINDING_ID_FMT.format(bucket=bucket),
        "ProductArn": PRODUCT_ARN_FMT.format(region=region, account=ACCOUNT_ID),
        "GeneratorId": "s3-public-access-check",
        "AwsAccountId": ACCOUNT_ID,
        "Types": [
            "Software and Configuration Checks/Industry and Regulatory Standards/ISO 27001/A.9.4.1"
        ],
        "FirstObservedAt": now,
        "CreatedAt": now,
        "UpdatedAt": now,
        "Severity": {"Normalized": int(sev)},
        "Title": f"S3 bucket '{bucket}' public access check",
        "Description": (
            f"Bucket '{bucket}' is public." if public else f"Bucket '{bucket}' is not public."
        ),
        "Resources": [
            {
                "Type": "AwsS3Bucket",
                "Id": f"arn:aws:s3:::{bucket}",
                "Region": region,
            }
        ],
        "Compliance": {"Status": status},
        "RecordState": "ACTIVE",
    }


# ------------------------------------------------------------
# Main logic
# ------------------------------------------------------------

def run(region: str, evidence_bucket: str | None) -> None:
    s3 = boto3.client("s3", region_name=region)
    sh = boto3.client("securityhub", region_name=region)

    buckets = [b["Name"] for b in s3.list_buckets()["Buckets"]]
    findings: List[Dict[str, Any]] = []
    summary: Dict[str, Any] = {"checked": len(buckets), "public": []}

    for bucket in buckets:
        public = bucket_is_public(s3, bucket)
        if public:
            summary["public"].append(bucket)
        findings.append(create_finding(bucket, region, public))
        logger.info("%s – public=%s", bucket, public)

    # Send findings to Security Hub (max 100 per call)
    for i in range(0, len(findings), 100):
        batch = findings[i : i + 100]
        sh.batch_import_findings(Findings=batch)

    # Upload summary evidence if requested
    if evidence_bucket:
        key = f"s3-public-audit/summary-{dt.datetime.utcnow().strftime('%Y-%m-%dT%H%M%SZ')}.json"
        s3.put_object(
            Bucket=evidence_bucket,
            Key=key,
            Body=json.dumps(summary, indent=2).encode(),
        )
        logger.info("Uploaded summary to s3://%s/%s", evidence_bucket, key)

    logger.info("Completed scan. Buckets checked=%d, public=%d", summary["checked"], len(summary["public"]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Detect public S3 buckets and create Security Hub findings.")
    parser.add_argument("--evidence-bucket", help="S3 bucket to upload summary (optional)")
    parser.add_argument("--region", default=os.getenv("AWS_REGION", "us-east-1"))
    args = parser.parse_args()

    try:
        run(region=args.region, evidence_bucket=args.evidence_bucket)
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Error running public S3 check: %s", exc)
        sys.exit(1)
