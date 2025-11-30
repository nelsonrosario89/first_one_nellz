import os
import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

import boto3
from botocore.exceptions import ClientError

s3 = boto3.client("s3")
securityhub = boto3.client("securityhub")


def _load_env() -> Dict[str, Any]:
    bucket = os.environ["EVIDENCE_BUCKET"]
    dashboard_prefix = os.environ.get("DASHBOARD_PREFIX", "dashboard/")
    raw_max_age = os.environ.get("EVIDENCE_MAX_AGE_DAYS", "45")
    try:
        max_age_days = int(raw_max_age)
    except ValueError:
        max_age_days = 45

    raw_controls = os.environ.get("CONTROLS_DEFINITION", "").strip()
    controls: List[Dict[str, Any]] = []
    if raw_controls:
        try:
            parsed = json.loads(raw_controls)
            if isinstance(parsed, list):
                controls = [c for c in parsed if isinstance(c, dict)]
        except json.JSONDecodeError:
            print("WARNING: CONTROLS_DEFINITION is not valid JSON; no controls loaded")

    return {
        "bucket": bucket,
        "dashboard_prefix": dashboard_prefix,
        "max_age_days": max_age_days,
        "controls": controls,
    }


def lambda_handler(event, context):
    cfg = _load_env()

    now = datetime.now(timezone.utc)
    controls_summary = summarize_controls(
        bucket=cfg["bucket"],
        controls=cfg["controls"],
        max_age_days=cfg["max_age_days"],
        now=now,
    )

    sh_summary = summarize_security_hub()

    payload = {
        "generated_at": now.isoformat(),
        "evidence_bucket": cfg["bucket"],
        "controls": controls_summary,
        "securityhub_summary": sh_summary,
    }

    key = build_dashboard_key(cfg["dashboard_prefix"])
    body = json.dumps(payload, indent=2, default=str).encode("utf-8")

    s3.put_object(
        Bucket=cfg["bucket"],
        Key=key,
        Body=body,
        ContentType="application/json",
    )

    return {
        "statusCode": 200,
        "body": {
            "message": "Lab 9 control dashboard summary written",
            "s3_object": f"s3://{cfg['bucket']}/{key}",
            "control_count": len(controls_summary),
            "securityhub_findings_total": sh_summary.get("total_active_findings", 0),
        },
    }


def summarize_controls(
    bucket: str,
    controls: List[Dict[str, Any]],
    max_age_days: int,
    now: datetime,
) -> List[Dict[str, Any]]:
    """For each control, find newest evidence object and classify status."""
    results: List[Dict[str, Any]] = []

    for ctrl in controls:
        prefix = ctrl.get("evidence_prefix")
        if not prefix:
            continue

        latest = find_latest_object(bucket, prefix)

        status = "Missing"
        age_days = None
        last_evidence_str = None

        if latest is not None:
            age = now - latest
            age_days = age.days
            last_evidence_str = latest.isoformat()
            status = "OK" if age <= timedelta(days=max_age_days) else "Stale"

        results.append(
            {
                "id": ctrl.get("id"),
                "name": ctrl.get("name"),
                "iso_control": ctrl.get("iso_control"),
                "description": ctrl.get("description"),
                "status": status,
                "age_days": age_days,
                "last_evidence": last_evidence_str,
                "evidence_prefix": prefix,
            }
        )

    return results


def find_latest_object(bucket: str, prefix: str):
    """Return the most recent LastModified datetime for objects under prefix, or None."""
    latest = None
    continuation_token = None

    while True:
        params: Dict[str, Any] = {"Bucket": bucket, "Prefix": prefix}
        if continuation_token:
            params["ContinuationToken"] = continuation_token

        resp = s3.list_objects_v2(**params)
        contents = resp.get("Contents", [])

        for obj in contents:
            lm = obj.get("LastModified")
            if lm is None:
                continue
            if latest is None or lm > latest:
                latest = lm

        if resp.get("IsTruncated"):
            continuation_token = resp.get("NextContinuationToken")
        else:
            break

    return latest


def summarize_security_hub() -> Dict[str, Any]:
    """Summarize active Security Hub findings by severity label.

    This is intentionally lightweight for the MVP: it pulls up to 100 active
    findings and groups them by Severity.Label.
    """

    try:
        resp = securityhub.get_findings(
            Filters={
                "RecordState": [{"Value": "ACTIVE", "Comparison": "EQUALS"}],
            },
            MaxResults=100,
        )
    except ClientError as e:
        print(f"Error calling Security Hub GetFindings: {e}")
        return {"total_active_findings": 0, "by_severity": {}}

    findings = resp.get("Findings", [])
    by_severity: Dict[str, int] = {}

    for f in findings:
        label = f.get("Severity", {}).get("Label") or "UNKNOWN"
        by_severity[label] = by_severity.get(label, 0) + 1

    total = sum(by_severity.values())

    return {
        "total_active_findings": total,
        "by_severity": by_severity,
    }


def build_dashboard_key(prefix: str) -> str:
    """Return the S3 key for the dashboard JSON, ensuring trailing slash in prefix."""
    if prefix and not prefix.endswith("/"):
        prefix = prefix + "/"
    return f"{prefix}control-dashboard.json"
