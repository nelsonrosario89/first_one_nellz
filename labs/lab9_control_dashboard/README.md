# Lab 9 – End-to-End ISO 27001 Control Dashboard (MVP)

This lab builds an **ISO 27001 control dashboard** by aggregating evidence from earlier labs and Security Hub into a compact JSON summary, then rendering it via a simple static HTML/JavaScript page.

The goal is not a huge UI project but a **minimum viable dashboard** that can answer:

- Which ISO 27001 controls have **recent evidence**?
- Which controls have **stale or missing evidence**?
- What is the **current Security Hub findings picture** (by severity)?

The backend Lambda writes a JSON file to S3. The frontend dashboard (a static HTML file) reads this JSON and displays status by control.

---

## 1. Architecture Overview

- **Evidence S3 bucket** – Same bucket used in prior labs (for example `aws-cloudtrail-logs-295070998992-4ab61dec`) containing:
  - Lab 1–7 evidence prefixes (`cloudtrail-validation/`, `ec2-inventory/`, `s3-public-audit/`, `mfa-evidence/`, `sg-drift-evidence/`, `continuous-monitoring/`, `grc-audit-evidence/lab7-`).
  - Lab 8 audit packs under `audit-packs/`.
- **Lambda: `lab9-control-dashboard`** – Periodically:
  - Scans S3 for the newest object per lab prefix.
  - Calculates evidence age (days) and classifies each control as **OK**, **Stale**, or **Missing**.
  - Calls Security Hub and summarizes active findings by severity.
  - Writes a compact JSON document into S3 (for example `dashboard/control-dashboard.json`).
- **EventBridge Schedule** – Triggers the Lambda daily (`rate(1 day)`) or hourly.
- **Static Dashboard (HTML/JS)** – Simple `dashboard.html` page hosted in S3 (or CloudFront) that runs JavaScript to fetch `control-dashboard.json` and render:
  - A table of controls with status and last evidence date.
  - A small summary of Security Hub findings by severity.

---

## 2. Implementation Steps

### 2.1 Directory & files in this repo

This lab lives in:

- `labs/lab9_control_dashboard/README.md` – this file.
- `labs/lab9_control_dashboard/lab9_control_dashboard.py` – Lambda backend code.
- `labs/lab9_control_dashboard/dashboard.html` – Static HTML/JS dashboard.

### 2.2 Configure Lambda `lab9-control-dashboard`

1. Create a new Lambda function:
   - Name: `lab9-control-dashboard`
   - Runtime: Python 3.x
   - Execution role: reuse an existing Security Hub + S3 role, **or** create one with:
     - `securityhub:GetFindings`
     - `s3:ListBucket` on the evidence bucket
     - `s3:GetObject` on evidence prefixes
     - `s3:PutObject` on the dashboard prefix (for `control-dashboard.json`).
2. Set the handler to:
   - `lab9_control_dashboard.lambda_handler`
3. Increase timeout to at least **2 minutes** and memory to **512 MB**.

### 2.3 Environment variables

Recommended environment variables for the Lambda:

- `EVIDENCE_BUCKET` – e.g. `aws-cloudtrail-logs-295070998992-4ab61dec`
- `DASHBOARD_PREFIX` – e.g. `dashboard/` (JSON will be `dashboard/control-dashboard.json`)
- `EVIDENCE_MAX_AGE_DAYS` – e.g. `45` (anything older is **Stale**)
- `CONTROLS_DEFINITION` – JSON array describing each control and its evidence prefix, for example:

```json
[
  {
    "id": "cloudtrail",
    "name": "CloudTrail Enabled & Multi-Region",
    "iso_control": "A.12.4.1",
    "evidence_prefix": "cloudtrail-validation/",
    "description": "Lab 1 – CloudTrail status report"
  },
  {
    "id": "ec2_inventory",
    "name": "EC2 Inventory & Scope Tagging",
    "iso_control": "A.8.1.1",
    "evidence_prefix": "ec2-inventory/",
    "description": "Lab 2 – EC2 inventory CSVs"
  },
  {
    "id": "s3_public",
    "name": "Public S3 Bucket Detection",
    "iso_control": "A.9.4.1",
    "evidence_prefix": "s3-public-audit/",
    "description": "Lab 3 – public bucket checks"
  },
  {
    "id": "mfa_enforcement",
    "name": "MFA Enforcement Evidence",
    "iso_control": "A.9.2.3",
    "evidence_prefix": "mfa-evidence/",
    "description": "Lab 4 – IAM users without MFA"
  },
  {
    "id": "sg_drift",
    "name": "Security Group Drift Detection",
    "iso_control": "A.13.1.1",
    "evidence_prefix": "sg-drift-evidence/",
    "description": "Lab 5 – SG drift snapshots"
  },
  {
    "id": "continuous_monitoring",
    "name": "Continuous Control Monitoring",
    "iso_control": "A.18.2.3",
    "evidence_prefix": "continuous-monitoring/",
    "description": "Lab 6 – Security Hub insights"
  },
  {
    "id": "iam_role_review",
    "name": "IAM Role Review (AssumeRole)",
    "iso_control": "A.9.1.2",
    "evidence_prefix": "grc-audit-evidence/lab7-",
    "description": "Lab 7 – AssumeRole CSV evidence"
  },
  {
    "id": "audit_pack",
    "name": "Monthly Audit Pack",
    "iso_control": "A.18.2.1",
    "evidence_prefix": "audit-packs/",
    "description": "Lab 8 – audit-pack ZIPs"
  }
]
```

The Lambda code in `lab9_control_dashboard.py` expects this structure and will:

- For each entry, list S3 objects under `evidence_prefix` and find the newest `LastModified`.
- Calculate `age_days` and assign a `status`:
  - `OK` if age ≤ `EVIDENCE_MAX_AGE_DAYS`.
  - `Stale` if age > `EVIDENCE_MAX_AGE_DAYS`.
  - `Missing` if no objects exist.

### 2.4 EventBridge schedule

Create an EventBridge rule such as `lab9-control-dashboard-hourly` or `lab9-control-dashboard-daily` with:

- **Schedule:** `rate(1 day)` or `rate(1 hour)`.
- **Target:** the `lab9-control-dashboard` Lambda.

Each run overwrites the JSON summary in S3 (idempotent).

---

## 3. Python Lambda Skeleton

See [`lab9_control_dashboard.py`](./lab9_control_dashboard.py) for full implementation. High‑level flow:

1. Load configuration from environment variables.
2. For each control in `CONTROLS_DEFINITION`:
   - List objects in S3 under `evidence_prefix`.
   - Track the most recent `LastModified` timestamp.
   - Compute `age_days` and `status` (`OK` / `Stale` / `Missing`).
3. Call Security Hub `GetFindings` for active findings and summarize by severity label.
4. Build a JSON document like:

```json
{
  "generated_at": "2025-11-29T23:59:01Z",
  "evidence_bucket": "aws-cloudtrail-logs-295070998992-4ab61dec",
  "controls": [
    {
      "id": "cloudtrail",
      "name": "CloudTrail Enabled & Multi-Region",
      "iso_control": "A.12.4.1",
      "status": "OK",
      "age_days": 3,
      "last_evidence": "2025-11-26T10:15:00Z"
    }
  ],
  "securityhub_summary": {
    "total_active_findings": 12,
    "by_severity": {
      "CRITICAL": 1,
      "HIGH": 3,
      "MEDIUM": 4,
      "LOW": 4
    }
  }
}
```

5. Write JSON to S3 at `s3://<EVIDENCE_BUCKET>/<DASHBOARD_PREFIX>control-dashboard.json`.

The static dashboard reads this JSON and renders it for auditors / stakeholders.

---

## 4. Static HTML Dashboard (MVP)

`dashboard.html` is a simple static page that:

- Uses JavaScript `fetch('control-dashboard.json')` to load the JSON file from the same S3 prefix.
- Renders:
  - A table of controls with columns: ISO control, control name, status, last evidence, age (days).
  - A small summary of Security Hub findings by severity (cards or rows).
- Colors status values (e.g., green for `OK`, orange for `Stale`, red for `Missing`).

### Hosting options

- **Simplest:**
  - Upload `dashboard.html` and let the Lambda write `control-dashboard.json` into the **same S3 prefix** (for example `dashboard/`).
  - Enable **static website hosting** on the bucket.
  - Access the dashboard via the S3 website endpoint: `http://<bucket-website-endpoint>/dashboard/dashboard.html`.

For a production portfolio, you could later front this with CloudFront and add authentication, but that is **optional** for this lab.

---

## 5. ISO 27001 Mapping

This lab does not introduce a *new* control; instead it stitches together evidence from multiple controls into a single view:

- **A.12.4.1 – Event Logging** (CloudTrail validation – Lab 1)
- **A.8.1.1 – Inventory of Assets** (EC2 inventory – Lab 2)
- **A.9.4.1 – Information Access Restriction** (S3 public access – Lab 3)
- **A.9.2.3 – Management of Privileged Access Rights** (MFA enforcement – Lab 4)
- **A.13.1.1 – Network Controls** (SG drift – Lab 5)
- **A.18.2.3 – Technical Compliance Review** (continuous monitoring – Lab 6)
- **A.9.1.2 – Access to Networks & Network Services** (IAM role review – Lab 7)
- **A.18.2.1 – Independent Review of Information Security** (monthly audit pack – Lab 8)

By putting these into **one JSON summary + dashboard**, you demonstrate the ability to:

- Aggregate evidence across multiple technical controls.
- Present control effectiveness at a glance for auditors and management.
- Show where evidence is missing or stale so follow‑up actions can be prioritized.

---

## 6. Portfolio Evidence

For your portfolio, capture:

- **Screenshot** of the Lambda configuration and environment variables for `lab9-control-dashboard`.
- **Screenshot** of the EventBridge schedule for the dashboard refresh.
- **Screenshot** of the S3 `dashboard/` prefix showing `control-dashboard.json`.
- **Screenshot** of `dashboard.html` in the browser with control statuses and Security Hub summary.

This completes the progression from individual control automations (Labs 1–8) to a **single-pane-of-glass ISO 27001 control dashboard** in Lab 9.
