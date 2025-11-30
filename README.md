# Python GRC Automation Toolkit
 
 [![Lab 3 – S3 Public Check](https://github.com/nelsonrosario89/first_one_nellz/actions/workflows/lab3_s3_public_check.yml/badge.svg)](https://github.com/nelsonrosario89/first_one_nellz/actions/workflows/lab3_s3_public_check.yml)
 
This repository is a **Python GRC Automation Toolkit** plus a set of **AWS labs** that demonstrate how to automate ISO 27001–aligned controls using CloudTrail, IAM, S3, Security Hub, Lambda, EventBridge, and GitHub Actions.

The labs under `labs/` map directly to specific ISO 27001 Annex A controls and are designed to be portfolio‑ready.

## Labs

| Path | Lab | Summary |
|------|-----|---------|
| `labs/lab1_cloudtrail_validation/` | **Lab 1 – Validate CloudTrail is Enabled & Multi‑Region** | Verifies there is an organization‑wide, multi‑region CloudTrail capturing management events in all regions. Supports ISO 27001 A.12.4.1 (Event Logging). |
| `labs/lab2_ec2_inventory/` | **Lab 2 – Inventory & Categorize EC2 Instances** | Builds an EC2 asset inventory with tags and security‑group context, flagging instances as in‑scope or out‑of‑scope for compliance. Maps to A.8.1.1 (Inventory of Assets). |
| `labs/lab3_s3_public_check/` | **Lab 3 – Auto‑Detect Public S3 Buckets** | GitHub Actions workflow runs `s3_public_check.py`, finds publicly accessible buckets, and publishes Security Hub findings plus JSON evidence to S3. Implements A.9.4.1 (Information Access Restriction). |
| `labs/lab4_mfa_enforcement/` | **Lab 4 – MFA Enforcement Evidence Collection** | Scheduled Lambda enumerates IAM users, identifies accounts without MFA, and records evidence for privileged access reviews. Supports A.9.2.3 (Management of Privileged Access Rights). |
| `labs/lab5_sg_drift_detection/` | **Lab 5 – Security Group Drift Detection** | AWS Config and Lambda detect risky security‑group changes (for example, port 22 opened to the world) and raise alerts. Aligns with A.13.1.1 (Network Controls). |
| `labs/lab6_continuous_monitoring/` | **Lab 6 – Continuous Control Monitoring with Security Hub** | Lambda builds tag‑based Security Hub insights, pushes metrics to CloudWatch, and tracks control effectiveness over time. Maps to A.18.2.3 (Technical Compliance Review). |
| `labs/lab7_iam_role_review/` | **Lab 7 – Automated Role Review for ISO 27001 Access Control** | Lambda analyzes CloudTrail `AssumeRole` events and IAM trust policies to show who can assume critical IAM roles, exporting CSV evidence and a trust‑relationship diagram. Supports A.9.1.2 (Access to Networks & Network Services). |
| `labs/lab8_audit_pack_generator/` | **Lab 8 – Lambda‑Powered Audit Pack Generator** | Monthly Lambda job packages key evidence artifacts (from Labs 1–7 and other sources) into a single S3 ZIP with a README mapping each file to ISO 27001 controls. Implements A.18.2.1 (Independent Review of Information Security). |

Each lab directory contains its own `README.md`, Python code, and screenshots that you can reference directly during audits or interviews.

## Utility Scripts

Outside the lab folders, this repo also includes standalone scripts used in earlier exercises and case studies:

| Path | Purpose |
|------|---------|
| `scripts/list_s3_buckets.py` | Collects all S3 bucket names & creation dates, exports `s3_buckets_report.xlsx`, and writes `s3_audit.log`. |
| `scripts/fafo_checker.py` | “FAFO” case‑study control check – lists IAM users without MFA, exports `iam_users_without_mfa.xlsx`, and logs to `fafo_audit.log`. |
| `scripts/ec2_compliance_check.py` | Multi‑region EC2 compliance checker – evaluates termination protection, public IP exposure, and EBS encryption; writes `ec2_compliance_report.xlsx` and `ec2_audit.log`, exits 2 if violations exist. |
| `scripts/config_noncompliant_rules.py` | AWS Config non‑compliant rules report – lists NON_COMPLIANT rules and exports `config_noncompliant_rules.xlsx`, exits 2 if any rules have violations. |
| `scripts/guardduty_findings_summary.py` | GuardDuty findings summary – collects recent findings, groups by severity, exports `guardduty_findings_summary.xlsx`, exits 2 if findings are present. |
| `scripts/unused_iam_access_keys.py` | Unused IAM access keys check – flags active keys unused for 90+ days, exports `iam_unused_access_keys.xlsx`, exits 2 if any unused keys are found. |
| `.vscode/settings.json` | VS Code workspace settings enabling Black formatting, Flake8 linting, import‑organise‑on‑save, and pytest integration. |
| `requirements.txt` | Runtime dependencies (boto3, pandas, openpyxl, etc.). |
| `requirements-dev.txt` | Dev‑only tools (black, flake8, isort, pytest). |

## Quick start

1. **Create & activate the virtual environment**:

   ```bash
   python3 -m venv .venv        # create isolated environment
   source .venv/bin/activate    # activate it (use Scripts\activate on Windows)
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt         # runtime libs
   pip install -r requirements-dev.txt     # formatting / linting / tests
   ```

3. **Run selected scripts or labs locally** (for ad‑hoc checks or demos):

   ```bash
   python scripts/list_s3_buckets.py
   python scripts/fafo_checker.py
   ```

## Development workflows

* **Format & lint**: `black . && flake8` (inside `.venv`).
* **Run tests**: `pytest` (add tests alongside new labs and scripts).
* **VS Code** will auto‑format and lint on save thanks to `.vscode/settings.json`.

## Versioning

This project follows **SemVer‑style** tagging (for example, `v0.1`, `v0.2`) to track changes across labs and scripts.

---

Use this repo as a starting point for additional AWS control checks (GuardDuty, Config rules, KMS key rotation, etc.) and for building out a full ISO 27001 GRC engineering portfolio.
