"""Lambda: continuous_control_monitor

Creates/updates a custom AWS Security Hub Insight scoped by resource tag and
publishes a CloudWatch metric that reports the number of matching ACTIVE
findings. Intended to run on a schedule (e.g. EventBridge cron) for continuous
control monitoring (ISO 27001 A.18.2.3).

Environment variables
--------------------
SH_TAG_KEY      Tag key used to scope resources (e.g. "Environment")
SH_TAG_VALUE    Tag value used to scope resources (e.g. "Prod")
INSIGHT_NAME    Friendly name for the insight (e.g. "Prod-OpenFindings")
CW_NAMESPACE    Optional CloudWatch namespace (default "Custom/SecurityHub")
CW_METRIC_NAME  Optional metric name (default "OpenFindings")

IAM permissions required
------------------------
securityhub:CreateInsight, UpdateInsight, GetInsights, GetInsightResults,
BatchGetFindings
cloudwatch:PutMetricData
"""
from __future__ import annotations

import os
import logging
from datetime import datetime, timezone
from typing import Any

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

sh = boto3.client("securityhub")
cw = boto3.client("cloudwatch")

TAG_KEY = os.getenv("SH_TAG_KEY", "Environment")
TAG_VALUE = os.getenv("SH_TAG_VALUE", "Prod")
INSIGHT_NAME = os.getenv("INSIGHT_NAME", f"{TAG_VALUE}-OpenFindings")
CW_NAMESPACE = os.getenv("CW_NAMESPACE", "Custom/SecurityHub")
CW_METRIC_NAME = os.getenv("CW_METRIC_NAME", "OpenFindings")

TAG_FILTER = {"TagKey": TAG_KEY, "TagValue": TAG_VALUE}
INSIGHT_FILTER = {"ResourceTags": [TAG_FILTER], "RecordState": ["ACTIVE"]}

def _find_existing_insight() -> str | None:
    """Return the ARN of an existing insight with the configured name."""
    paginator = sh.get_paginator("get_insights")
    for page in paginator.paginate():
        for insight in page.get("Insights", []):
            if insight.get("Name") == INSIGHT_NAME:
                return insight["InsightArn"]
    return None

def _create_or_update_insight() -> str:
    """Ensure an insight exists and return its ARN."""
    arn = _find_existing_insight()
    if arn:
        try:
            sh.update_insight(InsightArn=arn, Name=INSIGHT_NAME, Filters=INSIGHT_FILTER)
            logger.debug("Updated existing insight %s", arn)
        except ClientError as exc:
            logger.warning("Failed to update insight %s: %s", arn, exc)
        return arn

    resp = sh.create_insight(Name=INSIGHT_NAME, Filters=INSIGHT_FILTER, GroupByAttribute="Type")
    arn = resp["InsightArn"]
    logger.info("Created new insight %s", arn)
    return arn

def _get_open_findings(insight_arn: str) -> int:
    resp = sh.get_insight_results(InsightArn=insight_arn)
    return resp["InsightResults"]["TotalFindings"]

def _publish_metric(value: int) -> None:
    cw.put_metric_data(
        Namespace=CW_NAMESPACE,
        MetricData=[{
            "MetricName": CW_METRIC_NAME,
            "Timestamp": datetime.now(timezone.utc),
            "Value": value,
            "Unit": "Count"
        }]
    )
    logger.info("Published metric %s/%s=%s", CW_NAMESPACE, CW_METRIC_NAME, value)

def lambda_handler(event: dict[str, Any], _context: Any) -> dict[str, Any]:  # noqa: D401
    """Lambda entry point."""
    logger.debug("Event: %s", event)

    insight_arn = _create_or_update_insight()
    open_count = _get_open_findings(insight_arn)
    _publish_metric(open_count)

    return {"insight": insight_arn, "open_findings": open_count}
