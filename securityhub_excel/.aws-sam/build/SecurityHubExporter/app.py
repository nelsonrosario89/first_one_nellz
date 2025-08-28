"""
Lambda entry point that:
1. Pulls ACTIVE findings from AWS Security Hub
2. Writes them into an Excel workbook (openpyxl)
3. Uploads the workbook to a versioned S3 bucket
"""

import datetime
import io
import os

import boto3
from openpyxl import Workbook

# ---------- AWS clients ----------
SECURITY_HUB = boto3.client("securityhub")
S3 = boto3.client("s3")

# Bucket is injected via environment variable in the template
BUCKET = os.environ["REPORT_BUCKET"]


def handler(event, context):
    """Main Lambda handler"""
    findings = _get_active_findings()
    wb = _build_workbook(findings)
    key = _upload_to_s3(wb)

    # Log where the report is stored for troubleshooting
    print(f"Report saved to s3://{BUCKET}/{key} ({len(findings)} findings)")
    return {"key": key, "count": len(findings)}


# ---------- Helper functions ----------


def _get_active_findings():
    """Return a flat list of ACTIVE Security Hub findings"""
    paginator = SECURITY_HUB.get_paginator("get_findings")
    pages = paginator.paginate(
        Filters={"RecordState": [{"Value": "ACTIVE", "Comparison": "EQUALS"}]}
    )
    findings = [f for page in pages for f in page["Findings"]]
    return findings


def _build_workbook(findings):
    """Convert findings list into an Excel workbook object"""
    wb = Workbook()
    ws = wb.active
    ws.title = "Findings"

    # Column headers
    headers = [
        "Id",
        "Title",
        "Severity",
        "Compliance (first)",
        "FirstObserved",
        "ResourceId",
    ]
    ws.append(headers)
    for cell in ws[1]:
        cell.font = cell.font.copy(bold=True)

    # Data rows
    for f in findings:
        ws.append(
            [
                f["Id"],
                f["Title"][:250],
                f["Severity"]["Label"],
                (f.get("Compliance") or {}).get("RelatedRequirements", [""])[0],
                (f.get("FirstObservedAt") or f.get("CreatedAt") or "")[:10],
                f["Resources"][0]["Id"],
            ]
        )
    return wb


def _upload_to_s3(wb):
    """Upload workbook bytes to S3 and return the object key"""
    today = datetime.date.today()
    key = f"reports/{today}/securityhub.xlsx"

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)

    S3.put_object(
        Bucket=BUCKET,
        Key=key,
        Body=buf.getvalue(),
        ACL="bucket-owner-full-control",
    )
    return key
