# Lab 5 – Security Group Drift Detection

This lab implements an AWS Lambda function that detects **risky security group changes** in real-time. When AWS Config detects a security group modification, this Lambda inspects ingress rules and publishes an alert to SNS if sensitive ports (SSH, RDP, etc.) are exposed to the Internet (0.0.0.0/0).

## What the Lambda does

- Triggered by AWS Config configuration change events for `AWS::EC2::SecurityGroup`.
- Extracts security group configuration from the Config event.
- Analyzes ingress rules for risky permissions:
  - Port 22 (SSH) open to 0.0.0.0/0
  - Port 3389 (RDP) open to 0.0.0.0/0
  - Configurable additional sensitive ports via `SENSITIVE_PORTS` env var
- Publishes an SNS notification with security group ID, risky ports, account, and region.

## Compliance Mapping

| Framework | Control | Description |
|-----------|---------|-------------|
| **SOC 2** | CC6.1.4 | Firewalls and security groups – network access restricted using security controls |
| **ISO 27001:2022** | A.8.1.1 | Inventory of assets with security group context |
| **ISO 27001:2022** | A.13.1.1 | Network controls – networks managed and controlled |
| **PCI DSS** | Req. 1 | Network security controls installed and maintained |

## Required IAM permissions

The Lambda execution role needs:

- **SNS publish access**
  - `sns:Publish` on the target SNS topic ARN
- **CloudWatch Logs** (for function logging)
  - `logs:CreateLogGroup`
  - `logs:CreateLogStream`
  - `logs:PutLogEvents`

Note: This Lambda is triggered by AWS Config, not by direct API calls, so no Config-specific permissions are required on the Lambda role itself. The Config rule that triggers this Lambda needs its own permissions.

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SNS_TOPIC_ARN` | Yes | SNS topic ARN where drift alerts are published |
| `SENSITIVE_PORTS` | No | Comma-separated list of additional ports to monitor (default: `22,3389`) |

## How to deploy

### 1. Create the SNS Topic

```bash
aws sns create-topic --name security-group-drift-alerts
```

Save the returned ARN for the `SNS_TOPIC_ARN` environment variable.

### 2. Package and deploy the Lambda

```bash
# Create deployment package
cd lab5_sg_drift_detection
zip sg_drift_checker.zip sg_drift_checker.py

# Create Lambda function
aws lambda create-function \
  --function-name sg-drift-detector \
  --runtime python3.9 \
  --role arn:aws:iam::<account>:role/lambda-sg-drift-role \
  --handler sg_drift_checker.lambda_handler \
  --zip-file fileb://sg_drift_checker.zip \
  --environment Variables={SNS_TOPIC_ARN=arn:aws:sns:us-east-1:<account>:security-group-drift-alerts}
```

### 3. Create AWS Config Rule (trigger)

```bash
# Create a Config rule that triggers on security group changes
aws config put-config-rule \
  --config-rule name=security-group-change-trigger \
  --source owner=AWS,sourceIdentifier=EC2_SECURITY_GROUP
```

### 4. Connect Config to Lambda

Use EventBridge or Config's direct Lambda invocation to trigger this function when the Config rule detects changes.

## Lambda handler

```python
def lambda_handler(event, context):
    """Handle AWS Config change event."""
    # Parse Config event
    sg_config = event['configurationItem']['configuration']
    
    # Detect drift
    risky_ports = detect_drift(sg_config)
    
    if risky_ports:
        # Publish alert
        publish_alert(
            security_group_id=sg_config['groupId'],
            ports=risky_ports,
            account_id=event['configurationItem']['awsAccountId'],
            region=event['configurationItem']['awsRegion']
        )
        return {'statusCode': 200, 'body': f'Alert sent for ports {risky_ports}'}
    
    return {'statusCode': 200, 'body': 'No drift detected'}
```

## Drift detection logic

The function flags a security group as "drifted" when:

1. An ingress rule has `IpRanges` containing `0.0.0.0/0` (Internet-facing)
2. AND the port range includes any sensitive port (22, 3389, or custom list)

Example risky configuration:
```json
{
  "IpPermissions": [{
    "IpProtocol": "tcp",
    "FromPort": 22,
    "ToPort": 22,
    "IpRanges": [{"CidrIp": "0.0.0.0/0"}]
  }]
}
```

## SNS alert format

```
Security Group sg-0123456789abcdef0 in account 123456789012/us-east-1 has 
risky ingress rules: ports [22, 3389] open to 0.0.0.0/0
```

## Extending the monitoring

Add more ports via environment variable:
```bash
SENSITIVE_PORTS=22,3389,3306,5432,1433
```

This monitors MySQL, PostgreSQL, and SQL Server default ports in addition to SSH and RDP.

## Why this matters for AI automation

1. **Change events as time-series** – Config change events create training data for predictive drift modeling
2. **Ground truth for classifiers** – Rule evaluations provide labeled outcomes for network policy violation detection
3. **Event-driven architecture** – Demonstrates how AI agents respond to infrastructure state changes in real-time

## Related labs

- Lab 2 (EC2 Inventory) – provides context on which instances use affected security groups
- Lab 6 (Continuous Monitoring) – aggregates security group findings into Security Hub
- Lab 8 (Audit Pack Generator) – captures Config history as evidence of drift detection coverage

## Files in this lab

| File | Description |
|------|-------------|
| `sg_drift_checker.py` | Lambda function code |
| `Lab5_SG_Drift_Fix_Notes.md` | Additional implementation notes |
