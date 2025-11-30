import os
import io
import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List
import zipfile

import boto3
from botocore.exceptions import ClientError


s3 = boto3.client("s3")


def _load_env() -> Dict[str, Any]:
    bucket = os.environ["EVIDENCE_BUCKET"]
    output_prefix = os.environ.get("OUTPUT_PREFIX", "audit-packs/")
    days_back_str = os.environ.get("DAYS_BACK", "30")
    try:
        days_back = int(days_back_str)
    except ValueError:
        days_back = 30

    raw_sources = os.environ.get("SOURCE_DEFINITIONS", "").strip()
    sources: List[Dict[str, Any]] = []
    if raw_sources:
        try:
            parsed = json.loads(raw_sources)
            if isinstance(parsed, list):
                sources = [s for s in parsed if isinstance(s, dict)]
        except json.JSONDecodeError:
            print("WARNING: SOURCE_DEFINITIONS is not valid JSON; no sources loaded")

    return {
        "bucket": bucket,
        "output_prefix": output_prefix,
        "days_back": days_back,
        "sources": sources,
    }


def lambda_handler(event, context):
    cfg = _load_env()

    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(days=cfg["days_back"])

    objects = collect_evidence_objects(
        bucket=cfg["bucket"],
        sources=cfg["sources"],
        start_time=start_time,
        end_time=end_time,
    )

    zip_bytes, file_count = build_audit_zip(
        bucket=cfg["bucket"],
        sources=cfg["sources"],
        objects=objects,
        start_time=start_time,
        end_time=end_time,
    )

    key = build_s3_key(cfg["output_prefix"], end_time)

    s3.put_object(Bucket=cfg["bucket"], Key=key, Body=zip_bytes)

    return {
        "statusCode": 200,
        "body": {
            "message": "Lab 8 audit pack generated",
            "s3_object": f"s3://{cfg['bucket']}/{key}",
            "file_count": file_count,
            "time_window": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
            },
        },
    }


def collect_evidence_objects(
    bucket: str,
    sources: List[Dict[str, Any]],
    start_time: datetime,
    end_time: datetime,
) -> List[Dict[str, Any]]:
    """List S3 objects for each configured prefix within the time window."""
    collected: List[Dict[str, Any]] = []

    if not sources:
        print("No SOURCE_DEFINITIONS provided; nothing to collect")
        return collected

    for src in sources:
        prefix = src.get("prefix")
        if not prefix:
            continue

        description = src.get("description")
        iso_control = src.get("iso_control")

        continuation_token = None
        while True:
            params: Dict[str, Any] = {
                "Bucket": bucket,
                "Prefix": prefix,
            }
            if continuation_token:
                params["ContinuationToken"] = continuation_token

            resp = s3.list_objects_v2(**params)
            contents = resp.get("Contents", [])

            for obj in contents:
                last_modified = obj.get("LastModified")
                if not isinstance(last_modified, datetime):
                    continue

                if not (start_time <= last_modified <= end_time):
                    continue

                collected.append(
                    {
                        "bucket": bucket,
                        "key": obj["Key"],
                        "size": obj.get("Size"),
                        "last_modified": last_modified,
                        "description": description,
                        "iso_control": iso_control,
                    }
                )

            if resp.get("IsTruncated"):
                continuation_token = resp.get("NextContinuationToken")
            else:
                break

    return collected


def build_audit_zip(
    bucket: str,
    sources: List[Dict[str, Any]],
    objects: List[Dict[str, Any]],
    start_time: datetime,
    end_time: datetime,
) -> (bytes, int):
    """Create an in-memory ZIP of all collected evidence and a README file."""
    buffer = io.BytesIO()
    zf = zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED)

    lines: List[str] = []
    lines.append("AWS GRC Audit Pack")
    lines.append("")
    lines.append(f"Time window: {start_time.isoformat()} to {end_time.isoformat()}")
    lines.append("")
    lines.append("Included evidence files:")

    file_count = 0

    for obj in objects:
        key = obj["key"]
        description = obj.get("description")
        iso_control = obj.get("iso_control")

        try:
            resp = s3.get_object(Bucket=bucket, Key=key)
            body = resp["Body"].read()
        except ClientError as e:
            print(f"Failed to fetch object {key}: {e}")
            continue

        zip_path = f"evidence/{key}"
        zf.writestr(zip_path, body)
        file_count += 1

        lines.append(f"- {zip_path}")
        if description:
            lines.append(f"  Description: {description}")
        if iso_control:
            lines.append(f"  ISO 27001: {iso_control}")

    if not objects:
        lines.append("(No evidence files found for the configured time window.)")

    lines.append("")
    lines.append("Source configuration summary:")
    for src in sources:
        prefix = src.get("prefix", "(missing prefix)")
        description = src.get("description") or ""
        iso_control = src.get("iso_control") or ""
        line = f"- Prefix: {prefix}"
        if description:
            line += f" | Description: {description}"
        if iso_control:
            line += f" | ISO 27001: {iso_control}"
        lines.append(line)

    readme_text = "\n".join(lines) + "\n"
    zf.writestr("README_AUDIT_PACK.txt", readme_text.encode("utf-8"))

    zf.close()
    buffer.seek(0)
    return buffer.read(), file_count


def build_s3_key(output_prefix: str, timestamp: datetime) -> str:
    """Build S3 key like audit-packs/audit-pack-YYYYMMDDTHHMMSSZ.zip."""
    if output_prefix and not output_prefix.endswith("/"):
        output_prefix = output_prefix + "/"
    ts = timestamp.strftime("%Y%m%dT%H%M%SZ")
    return f"{output_prefix}audit-pack-{ts}.zip"
