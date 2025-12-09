# Lab 6 – Continuous Control Monitoring with Custom Security Hub Insights

> **Goal:** build continuous technical-compliance monitoring by authoring *custom* AWS Security Hub Insights and visualising their trend over time.

| Item | Details |
|------|---------|
| **AWS Services** | Security Hub, AWS Lambda, Amazon CloudWatch (Events + Dashboards) |
| **Primary ISO 27001 Control** | **A.18.2.3 – Technical Compliance Review** |
| **Language / Runtime** | Python 3.11 (AWS Lambda) |

---

## 1  Architecture Overview
```
┌────────────┐    Scheduled Event      ┌─────────────┐
│ CloudWatch │ ───────────────────────▶│  Lambda     │
│  Events    │  (e.g. cron @ daily)   │  generate   │
└────────────┘                         │  insights   │
                                       └──────┬──────┘
                                              │
                                              │  Security Hub `BatchUpdateFindings`,
                                              │  `CreateInsight`, `UpdateInsight`
                                              ▼
                                       ┌─────────────┐
                                       │ Security    │
                                       │  Hub        │
                                       └─────────────┘
                                              │
                                              │  `GetInsights` metrics put to
                                              │  CloudWatch via the same function
                                              ▼
                                       ┌─────────────┐
                                       │  CW Dash   │
                                       │  boards     │
                                       └─────────────┘
```

* **Lambda** runs on a schedule, queries Security Hub findings **scoped by tag** (e.g. `Environment=Prod`) and:
  1. Creates or updates a custom *Insight* (API: `CreateInsight` / `UpdateInsight`).
  2. Publishes the count of matching findings as a CloudWatch custom metric.
* A CloudWatch **Dashboard** plots the metric so you can watch control effectiveness drift over weeks.

---

## 2  Implementation Steps

1. **Create a new Lambda function**  `continuous_control_monitor`  with the following IAM permissions:
   ```yaml
   Effect: Allow
   Action:
     - securityhub:CreateInsight
     - securityhub:UpdateInsight
     - securityhub:GetInsights
     - securityhub:GetInsightResults
     - cloudwatch:PutMetricData
   Resource: "*"
   ```
2. **Environment variables** for the function:
   | Name | Example | Purpose |
   |------|---------|---------|
   | `SH_TAG_KEY` | `Environment` | Tag key used for scoping |
   | `SH_TAG_VALUE` | `Prod` | Tag value |
   | `INSIGHT_NAME` | `Prod-Findings-Open` | Friendly name |
3. **Schedule** the function via EventBridge rule (cron `0 */6 * * ? *` = every 6 hours).
4. **CloudWatch Dashboard**: add a single-value and line chart for namespace `Custom/SecurityHub` metric `OpenFindings`.

---

## 3  Python Lambda Skeleton
```python
import os, boto3, time
from datetime import datetime, timezone

sh = boto3.client("securityhub")
cw = boto3.client("cloudwatch")

TAG_FILTER = {
    "TagKey": os.environ["SH_TAG_KEY"],
    "TagValue": os.environ["SH_TAG_VALUE"],
}
INSIGHT_NAME = os.environ["INSIGHT_NAME"]

INSIGHT_FILTER = {
    "ResourceTags": [TAG_FILTER],
    "RecordState": ["ACTIVE"],
}

def ensure_insight():
    insights = sh.get_insights()['Insights']
    for ins in insights:
        if ins['Name'] == INSIGHT_NAME:
            return ins['InsightArn']
    resp = sh.create_insight(
        Name=INSIGHT_NAME,
        Filters=INSIGHT_FILTER,
        GroupByAttribute="Type"
    )
    return resp['InsightArn']

def lambda_handler(event, _):
    arn = ensure_insight()
    count = sh.get_insight_results(InsightArn=arn)['InsightResults']['TotalFindings']

    cw.put_metric_data(
        Namespace="Custom/SecurityHub",
        MetricData=[{
            "MetricName": "OpenFindings",
            "Timestamp": datetime.now(timezone.utc),
            "Value": count,
            "Unit": "Count"
        }]
    )
    return {"insight": arn, "open_findings": count}
```

---

## 4  ISO 27001 Mapping
| ISO 27001 Control | Implementation via Lab |
|-------------------|------------------------|
| **A.18.2.3 – Technical Compliance Review** | Regular, automated validation of AWS resources against Security Hub controls, filtered to production scope. Custom insight + dashboard provides ongoing evidence of compliance or drift. |

---

## 5  Deliverables
* Terraform / SAM / CDK stack (optional) that deploys the Lambda, role, schedule, and dashboard.
* Screenshot of the CloudWatch dashboard after several runs.
* This README explaining the linkage to ISO 27001.
