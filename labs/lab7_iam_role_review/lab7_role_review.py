import os
import csv
import io
import json
from datetime import datetime, timedelta, timezone

import boto3
from botocore.exceptions import ClientError

cloudtrail = boto3.client("cloudtrail")
iam = boto3.client("iam")
s3 = boto3.client("s3")
sts = boto3.client("sts")
ACCOUNT_ID = sts.get_caller_identity()["Account"]

EVIDENCE_BUCKET = os.environ["EVIDENCE_BUCKET"]
EVIDENCE_PREFIX = os.environ["EVIDENCE_PREFIX"]  # e.g. "grc-audit-evidence/lab7-"
TARGET_ROLE_ARNS = set(
    arn.strip()
    for arn in os.environ.get("TARGET_ROLE_ARNS", "").split(",")
    if arn.strip()
)


def lambda_handler(event, context):
    # 1. Define time window (last 14 days)
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(days=14)

    # 2. Look up AssumeRole events in CloudTrail
    assume_events = fetch_assumerole_events(start_time, end_time)

    # 3. Normalize events and filter to roles in scope
    normalized = normalize_events(assume_events, TARGET_ROLE_ARNS)

    # 4. Get trust policies for each role in scope
    trust_policies = fetch_trust_policies(TARGET_ROLE_ARNS)

    # 5. Build CSV report in memory
    csv_bytes = build_csv_report(normalized, trust_policies)

    # 6. Write report to S3
    key = build_s3_key(end_time)
    s3.put_object(Bucket=EVIDENCE_BUCKET, Key=key, Body=csv_bytes)

    return {
        "statusCode": 200,
        "body": {
            "message": "Lab 7 role review completed",
            "s3_object": f"s3://{EVIDENCE_BUCKET}/{key}",
            "event_count": len(normalized),
        },
    }


def fetch_assumerole_events(start_time, end_time):
    """Call CloudTrail LookupEvents for AssumeRole and paginate."""
    events = []
    params = {
        "LookupAttributes": [
            {"AttributeKey": "EventName", "AttributeValue": "AssumeRole"}
        ],
        "StartTime": start_time,
        "EndTime": end_time,
    }

    while True:
        resp = cloudtrail.lookup_events(**params)
        events.extend(resp.get("Events", []))

        token = resp.get("NextToken")
        if not token:
            break
        params["NextToken"] = token

    return events


def normalize_events(events, target_role_arns):
    """Extract key fields from raw CloudTrail events and keep only roles in scope."""
    normalized = []

    for e in events:
        detail_str = e.get("CloudTrailEvent", "{}")
        try:
            detail = json.loads(detail_str)
        except json.JSONDecodeError:
            continue

        event_time = e.get("EventTime")
        source_ip = detail.get("sourceIPAddress")

        user_identity = detail.get("userIdentity", {})
        principal_type = user_identity.get("type")
        principal = (
            user_identity.get("arn")
            or user_identity.get("principalId")
            or user_identity.get("userName")
        )

        resp = detail.get("responseElements", {}) or {}
        req = detail.get("requestParameters", {}) or {}

        role_arn = None
        assumed_role_user = resp.get("assumedRoleUser", {})
        if isinstance(assumed_role_user, dict):
            role_arn = assumed_role_user.get("arn")

        if not role_arn:
            role_arn = req.get("roleArn")

        if not role_arn:
            for r in e.get("Resources", []):
                if r.get("ResourceType") == "AWS::IAM::Role":
                    role_arn = r.get("ResourceName")
                    break

        if not role_arn:
            continue

        if target_role_arns and role_arn not in target_role_arns:
            continue

        normalized.append(
            {
                "RoleArn": role_arn,
                "PrincipalType": principal_type,
                "Principal": principal,
                "SourceIp": source_ip,
                "EventTime": event_time,
            }
        )

    return normalized


def fetch_trust_policies(role_arns):
    """Fetch AssumeRolePolicyDocument for roles in the SAME account as this Lambda."""
    policies = {}
    for arn in role_arns:
        parts = arn.split(":")
        if len(parts) < 5:
            continue
        account_id = parts[4]
        role_name = arn.split("/")[-1]

        if account_id != ACCOUNT_ID:
            print(f"Skipping trust policy fetch for cross-account role {arn}")
            continue

        try:
            resp = iam.get_role(RoleName=role_name)
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchEntity":
                print(f"Role not found in this account: {role_name}, skipping")
                continue
            raise

        policies[arn] = resp["Role"]["AssumeRolePolicyDocument"]

    return policies


def build_csv_report(events, trust_policies):
    """Create CSV bytes from normalized events and trust policies."""
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(
        [
            "RoleArn",
            "PrincipalType",
            "Principal",
            "SourceIp",
            "EventTime",
            "InTrustPolicy",
            "Notes",
        ]
    )

    for e in events:
        role_arn = e["RoleArn"]
        in_trust = evaluate_in_trust_policy(e, trust_policies.get(role_arn))

        writer.writerow(
            [
                role_arn,
                e["PrincipalType"],
                e["Principal"],
                e["SourceIp"],
                e["EventTime"].isoformat()
                if hasattr(e["EventTime"], "isoformat")
                else str(e["EventTime"]),
                "Yes" if in_trust else "No",
                "",
            ]
        )

    return output.getvalue().encode("utf-8")


def evaluate_in_trust_policy(event, trust_policy):
    """Return True if the event principal appears to be allowed by the trust policy."""
    if not trust_policy:
        return False

    principal = event.get("Principal")
    if not principal:
        return False

    statements = trust_policy.get("Statement", [])
    if isinstance(statements, dict):
        statements = [statements]

    for stmt in statements:
        if stmt.get("Effect") != "Allow":
            continue

        principals = stmt.get("Principal", {}) or {}
        if isinstance(principals, str):
            principals = {"AWS": principals}

        all_principals = []
        for key in ("AWS", "Service", "Federated"):
            value = principals.get(key)
            if not value:
                continue
            if isinstance(value, list):
                all_principals.extend(value)
            else:
                all_principals.append(value)

        for p in all_principals:
            if p == "*" or principal == p or principal.startswith(p):
                return True

    return False


def build_s3_key(timestamp):
    """Build S3 key like grc-audit-evidence/lab7-role-review-YYYYMMDDT...Z.csv."""
    ts = timestamp.strftime("%Y%m%dT%H%M%SZ")
    return f"{EVIDENCE_PREFIX}role-review-{ts}.csv"
