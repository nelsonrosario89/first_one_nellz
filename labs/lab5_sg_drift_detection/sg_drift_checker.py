"""Lab 5 – Security Group drift detection Lambda.

Triggered by AWS Config when a `AWS::EC2::SecurityGroup` resource configuration
changes. The function inspects ingress rules and publishes an alert to an SNS
Topic if it detects that a sensitive port (e.g. 22, 3389) is exposed to the
Internet (CIDR 0.0.0.0/0).

Environment variables required:
    SNS_TOPIC_ARN  – target topic for alerts
    SENSITIVE_PORTS – optional comma-separated list of additional ports (default
                      "22,3389")

This file purposefully contains **only code** – deployment steps are handled in
separate IaC or README instructions.
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List

import boto3
from botocore.exceptions import ClientError

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

SNS_TOPIC_ARN = os.getenv("SNS_TOPIC_ARN", "")
if not SNS_TOPIC_ARN:
    logger.warning("SNS_TOPIC_ARN env var is not set – alerts will be skipped")

# You can add more ports by setting the env var, e.g. "22,3389,3306"
DEFAULT_PORTS = {22, 3389}
_env_ports = os.getenv("SENSITIVE_PORTS")
if _env_ports:
    try:
        DEFAULT_PORTS.update({int(p.strip()) for p in _env_ports.split(",") if p.strip()})
    except ValueError:
        logger.error("Invalid SENSITIVE_PORTS value – must be comma-separated ints")

sns = boto3.client("sns")

def is_risky_permission(perm: Dict[str, Any]) -> bool:
    """Return True if the ingress permission is considered risky."""
    # IPv4 ranges
    for cidr_item in perm.get("IpRanges", []):
        if cidr_item.get("CidrIp") == "0.0.0.0/0":
            from_port = perm.get("FromPort")
            to_port = perm.get("ToPort")
            # Handle port ranges (AWS returns -1 for all ports when protocol is -1)
            if from_port is None or to_port is None:
                continue
            # Check any port in range intersects sensitive ports
            if any(p in DEFAULT_PORTS for p in range(from_port, to_port + 1)):
                return True
    return False

def detect_drift(sg_config: Dict[str, Any]) -> List[int]:
    """Return list of risky ports found (may be duplicates removed)."""
    risky_ports: set[int] = set()
    for perm in sg_config.get("ipPermissions", []):
        if is_risky_permission(perm):
            from_port = perm.get("FromPort")
            to_port = perm.get("ToPort")
            # Add all sensitive ports in the range
            for port in DEFAULT_PORTS:
                if from_port <= port <= to_port:
                    risky_ports.add(port)
    return sorted(risky_ports)

def publish_alert(security_group_id: str, ports: List[int], account_id: str, region: str) -> None:
    if not SNS_TOPIC_ARN:
        logger.debug("SNS topic not set – skipping publish")
        return
    message = (
        f"Security Group {security_group_id} in account {account_id}/{region} has "
        f"risky ingress rules: ports {ports} open to 0.0.0.0/0"
    )
    try:
        sns.publish(TopicArn=SNS_TOPIC_ARN, Message=message, Subject="SecurityGroup Drift Detected")
        logger.info("Published alert for %s – ports=%s", security_group_id, ports)
    except ClientError as exc:
        logger.error("Failed to publish SNS alert: %s", exc)

def lambda_handler(event: Dict[str, Any], _context: Any) -> Dict[str, Any]:
    """Entry point for AWS Lambda."""
    logger.debug("Received event: %s", json.dumps(event))

    invoking_event = json.loads(event.get("invokingEvent", "{}"))
    account_id = invoking_event.get("awsAccountId", "unknown")
    region = invoking_event.get("awsRegion", "unknown")

    # `configurationItem` is provided for configuration change notifications
    config_item = invoking_event.get("configurationItem")
    if not config_item or config_item.get("resourceType") != "AWS::EC2::SecurityGroup":
        logger.info("Non-security group invocation – nothing to do")
        return {"status": "ignored"}

    sg_id = config_item["resourceId"]
    # The full SG configuration is in configurationItem["configuration"]
    sg_conf = config_item.get("configuration", {})

    logger.info("Evaluating Security Group %s in %s/%s", sg_id, account_id, region)

    risky_ports = detect_drift(sg_conf)
    if risky_ports:
        logger.info("Risky ports detected for %s: %s", sg_id, risky_ports)
        publish_alert(sg_id, risky_ports, account_id, region)
        return {"status": "alert_published", "sg": sg_id, "ports": risky_ports}

    logger.info("No risky ingress found for %s", sg_id)
    return {"status": "clean", "sg": sg_id}


if __name__ == "__main__":  # pragma: no cover
    import argparse, sys, pathlib

    parser = argparse.ArgumentParser(description="Test sg_drift_checker locally with a sample event JSON.")
    parser.add_argument("event", type=pathlib.Path, help="Path to invokingEvent JSON file (as downloaded from AWS Config test)")
    args = parser.parse_args()

    with args.event.open("r", encoding="utf-8") as f:
        sample_event = json.load(f)

    # Wrap in fake Config wrapper
    event_wrapper = {
        "invokingEvent": json.dumps(sample_event)
    }

    result = lambda_handler(event_wrapper, None)
    print(json.dumps(result, indent=2))
