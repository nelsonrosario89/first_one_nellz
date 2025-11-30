# Lab 8 – Lambda-Powered Audit Pack Generator

This lab builds a **monthly ZIP “audit pack”** of ISO 27001 evidence artifacts by collecting key reports from an S3 evidence bucket and packaging them into a single compressed file. The ZIP includes a `README_AUDIT_PACK.txt` that maps each file to the relevant ISO 27001 control.

This supports **ISO 27001 A.18.2.1 – Independent Review of Information Security** by making it easy for auditors and management to review a consistent, timestamped bundle of technical evidence.

---

## 1. Architecture Overview

- **Evidence S3 bucket** – Central bucket that already stores outputs from Labs 1–7 (CloudTrail validation, EC2 inventory, S3 public checks, MFA scans, SG drift, continuous monitoring, IAM role review), plus any other compliance reports.
- **Lambda: `lab8-audit-pack-generator`** – Runs on a monthly schedule, queries S3 for recent evidence objects by prefix (e.g., `ec2-inventory/`, `s3-public-audit/`, `grc-audit-evidence/lab7-`), downloads them, and builds a single ZIP file in memory.
- **EventBridge Schedule** – Triggers the Lambda monthly using a `cron` or `rate(30 days)` expression.
- **Audit Pack ZIP in S3** – Written to a dedicated prefix like `audit-packs/audit-pack-YYYYMMDDTHHMMSSZ.zip`, containing:
  - Raw evidence artifacts (CSV, JSON, etc.) from prior labs.
  - `README_AUDIT_PACK.txt` summarizing each file and its mapped ISO 27001 control.

---

## 2. Implementation Steps

### 2.1 Evidence Bucket and Prefixes

- Reuse your existing evidence bucket (for example):
  - `aws-cloudtrail-logs-295070998992-4ab61dec`
- Ensure the bucket already contains evidence for earlier labs under clear prefixes, such as:
  - `cloudtrail-validation/` – Lab 1 CloudTrail status report
  - `ec2-inventory/` – Lab 2 EC2 asset inventory
  - `s3-public-audit/` – Lab 3 S3 public-access checks
  - `mfa-evidence/` – Lab 4 MFA enforcement results
  - `sg-drift-evidence/` – Lab 5 security-group drift snapshots
  - `continuous-monitoring/` – Lab 6 Security Hub insights or metrics
  - `grc-audit-evidence/lab7-` – Lab 7 IAM role review CSV reports

You do **not** need every single prefix to exist for the Lambda to work; it will simply skip any prefixes with no objects.

### 2.2 Create Lambda `lab8-audit-pack-generator`

- Runtime: **Python 3.x**.
- Recommended environment variables:

  - `EVIDENCE_BUCKET` – Name of the central evidence bucket (e.g. `aws-cloudtrail-logs-295070998992-4ab61dec`).
  - `OUTPUT_PREFIX` – Where to store audit packs (e.g. `audit-packs/`).
  - `DAYS_BACK` – Number of days of evidence to include (e.g. `30`).
  - `SOURCE_DEFINITIONS` – JSON string defining which S3 prefixes to include and how each maps to ISO controls. Example:

    ```json
    [
      {
        "prefix": "cloudtrail-validation/",
        "description": "Lab 1  CloudTrail multi-region status report",
        "iso_control": "A.12.4.1"
      },
      {
        "prefix": "ec2-inventory/",
        "description": "Lab 2  EC2 asset inventory",
        "iso_control": "A.8.1.1"
      },
      {
        "prefix": "s3-public-audit/",
        "description": "Lab 3  S3 public-access findings",
        "iso_control": "A.9.4.1"
      },
      {
        "prefix": "mfa-evidence/",
        "description": "Lab 4  IAM users without MFA",
        "iso_control": "A.9.2.3"
      },
      {
        "prefix": "sg-drift-evidence/",
        "description": "Lab 5  Security group drift detection",
        "iso_control": "A.13.1.1"
      },
      {
        "prefix": "continuous-monitoring/",
        "description": "Lab 6  Continuous control monitoring",
        "iso_control": "A.18.2.3"
      },
      {
        "prefix": "grc-audit-evidence/lab7-",
        "description": "Lab 7  IAM role review AssumeRole evidence",
        "iso_control": "A.9.1.2"
      }
    ]
    ```

- Minimum IAM permissions for the Lambda execution role:

  - `s3:ListBucket` on the evidence bucket
  - `s3:GetObject` on evidence prefixes
  - `s3:PutObject` on the `OUTPUT_PREFIX` where audit packs will be stored

### 2.3 EventBridge Schedule

- Create a rule such as `lab8-audit-pack-generator-monthly`.
- Example schedule options:
  - `rate(30 days)`
  - or `cron(0 6 1 * ? *)` to run at 06:00 UTC on the 1st of every month.
- Target: the `lab8-audit-pack-generator` Lambda.
- No special event payload is required; the function will compute its own time window based on `DAYS_BACK`.

---

## 3. Python Lambda Skeleton

The Lambda implemented in [`lab8_audit_pack_generator.py`](./lab8_audit_pack_generator.py) follows this flow:

1. Parse configuration from environment variables (`EVIDENCE_BUCKET`, `OUTPUT_PREFIX`, `DAYS_BACK`, `SOURCE_DEFINITIONS`).
2. Compute a time window (e.g., last 30 days).
3. For each `prefix` in `SOURCE_DEFINITIONS`:
   - Call `ListObjectsV2` on the evidence bucket.
   - Filter objects whose `LastModified` falls within the time window.
4. Download each matching object and add it to an in-memory ZIP file using `zipfile`.
5. Generate a `README_AUDIT_PACK.txt` summarizing:
   - The time window covered.
   - Each file path in the ZIP.
   - The description and `iso_control` from `SOURCE_DEFINITIONS`.
6. Write the ZIP back to S3 at:

   ```text
   s3://<EVIDENCE_BUCKET>/<OUTPUT_PREFIX>/audit-pack-YYYYMMDDTHHMMSSZ.zip
   ```

7. Return a JSON response including the S3 path and number of files included.

---

## 4. ISO 27001 Mapping

| ISO 27001 Control | Implementation via Lab 8 |
|-------------------|--------------------------|
| **A.18.2.1 – Independent Review of Information Security** | The monthly Lambda job automatically compiles technical evidence from multiple controls (e.g., CloudTrail logging, EC2 inventory, S3 public access checks, MFA enforcement, network controls, IAM role reviews) into a single, timestamped audit pack. The included README maps each file to its ISO 27001 control, making independent review and audit sampling faster and less error-prone. |

---

## 5. Deliverables & Portfolio Evidence

For your portfolio, capture:

- **Screenshot** of the EventBridge rule and its schedule.
- **Screenshot** of the Lambda configuration, environment variables, and recent CloudWatch logs showing a successful run.
- **Screenshot** of the `audit-packs/` prefix in S3 showing at least one generated ZIP.
- **Excerpt** from `README_AUDIT_PACK.txt` inside the ZIP, highlighting the control-to-file mapping.

Together with Labs 1–7, this lab shows how you can move from **individual control checks** to a **curated monthly audit pack** that makes formal ISO 27001 reviews much more efficient.
