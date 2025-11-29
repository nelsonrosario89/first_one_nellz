# Lab 7 – Automated Role Review for ISO 27001 Access Control

This lab automates a recurring review of **who can assume critical IAM roles** across AWS accounts, using CloudTrail, Lambda, EventBridge, and S3 evidence reports. It supports ISO 27001 **A.9.1.2 – Access to networks and network services** by providing timestamped proof that only authorized principals can assume scoped roles.

---

## 1. Architecture Overview

- **CloudTrail (management account)** – Organization-wide, multi‑region trail capturing all `AssumeRole` events.
- **Lambda (`lab7-role-review`)** – Runs every 14 days, queries CloudTrail for `AssumeRole` events targeting roles in scope, enriches them with IAM trust‑policy data (for same‑account roles), and writes a CSV report to S3.
- **EventBridge Rule** – Schedules the Lambda using `rate(14 days)`.
- **S3 Evidence Bucket** – Stores CSV reports under `grc-audit-evidence/lab7-*` for auditors and portfolio screenshots.

```text
┌──────────────────────────┐          ┌──────────────────────────┐
│ AWS Organizations Trail  │          │ EventBridge Rule         │
│ (Org + Multi-region)     │          │ rate(14 days)            │
└─────────────┬────────────┘          └─────────────┬────────────┘
              │                                     │
              │ CloudTrail LookupEvents             │ Triggers
              ▼                                     ▼
       ┌──────────────────────────┐        ┌──────────────────────────┐
       │ Lambda: lab7-role-review │        │ Scoped IAM Roles         │
       │ (Mgmt account 2950...)   │  . . . │ - access-review-* (mgmt) │
       └─────────────┬────────────┘  . . . │ - GitHubActions* (prod)  │
                     │                     │ - lab6_continuous_*      │
                     │ Writes CSV          └──────────────────────────┘
                     ▼
       ┌──────────────────────────┐
       │ S3 Evidence Bucket       │
       │ aws-cloudtrail-logs-*   │
       │ grc-audit-evidence/lab7-│
       └──────────────────────────┘
```

---

## 2. Implementation Steps

### 2.1 Configure CloudTrail (management account)

- Enable an **organization**, **multi‑region** trail in the management account.
- Ensure **management events (Read/Write)** are enabled so `AssumeRole` is captured.
- Set the log destination to the evidence bucket `aws-cloudtrail-logs-295070998992-4ab61dec`.

### 2.2 Create the Lambda function `lab7-role-review`

- Runtime: Python 3.x.
- Execution role with at least:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "CloudTrailLookup",
      "Effect": "Allow",
      "Action": ["cloudtrail:LookupEvents"],
      "Resource": "*"
    },
    {
      "Sid": "IamReadRoles",
      "Effect": "Allow",
      "Action": ["iam:ListRoles", "iam:GetRole"],
      "Resource": "*"
    },
    {
      "Sid": "WriteReportsToS3",
      "Effect": "Allow",
      "Action": ["s3:PutObject", "s3:AbortMultipartUpload"],
      "Resource": "arn:aws:s3:::aws-cloudtrail-logs-295070998992-4ab61dec/grc-audit-evidence/*"
    }
  ]
}
```

- Environment variables:

| Name              | Example                                              | Purpose                                       |
|-------------------|------------------------------------------------------|-----------------------------------------------|
| `EVIDENCE_BUCKET` | `aws-cloudtrail-logs-295070998992-4ab61dec`         | Evidence bucket                               |
| `EVIDENCE_PREFIX` | `grc-audit-evidence/lab7-`                          | Prefix for CSV files                          |
| `TARGET_ROLE_ARNS`| Comma-separated ARNs of roles in scope              | Filter for `AssumeRole` events + trust policy |

- Handler code lives in [`lab7_role_review.py`](./lab7_role_review.py).

### 2.3 Schedule the Lambda with EventBridge

- Create a rule named `lab7-role-review-every-2-weeks`.
- **Schedule pattern:** `rate(14 days)`.
- **Target:** Lambda function `lab7-role-review`.
- Event payload can be `{}`; the function computes its own time window.

### 2.4 CSV report format

Each run writes a CSV to:

```text
s3://aws-cloudtrail-logs-295070998992-4ab61dec/grc-audit-evidence/lab7-role-review-<timestamp>.csv
```

Columns:

| Column          | Description                                               |
|-----------------|-----------------------------------------------------------|
| `RoleArn`       | IAM role that was (or could be) assumed                   |
| `PrincipalType` | Type of caller (User, Role, AssumedRole, Federated)      |
| `Principal`     | ARN / ID of the caller                                    |
| `SourceIp`      | Source IP address from the CloudTrail event               |
| `EventTime`     | Timestamp of the `AssumeRole` event                       |
| `InTrustPolicy` | `Yes/No` – whether the principal appears in trust policy  |
| `Notes`         | Free-form notes / anomaly flags                           |

---

## 3. Python Lambda Skeleton

See [`lab7_role_review.py`](./lab7_role_review.py) for full code. High‑level flow:

- Compute `start_time` / `end_time` (last 14 days).
- Call `cloudtrail.lookup_events` for `EventName = AssumeRole`, paginate, parse events.
- Filter to `TARGET_ROLE_ARNS`.
- Fetch IAM trust policies for same‑account roles.
- Evaluate `InTrustPolicy` and write CSV to S3.

---

## 4. ISO 27001 Mapping

| ISO 27001 Control | Implementation via Lab 7 |
|-------------------|--------------------------|
| **A.9.1.2 – Access to networks and network services** | Organization‑wide CloudTrail + scheduled Lambda provide recurring evidence of who can assume critical IAM roles, by principal and timestamp. The CSV reports and trust‑relationship diagram show that only defined GitHub OIDC identities, Lambda service principals, and management‑account roles can assume the in‑scope roles, and highlight any unexpected principals for investigation. |

---

## 5. Additional Notes

- The Lambda function is scheduled to run every 14 days using EventBridge.
- The CSV report is stored in the evidence bucket under `grc-audit-evidence/lab7-*`.
- `lab7_trust_diagram.mmd` and `lab7_trust_diagram.png` visualize the trust relationships between GitHub OIDC, Lambda, CloudTrail, and S3.
