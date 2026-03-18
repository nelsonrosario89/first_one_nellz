# Lab 4 – IAM MFA Enforcement Audit

This lab implements a Python script that lists every IAM user in an AWS account, checks for MFA device enrollment, publishes Security Hub findings, and optionally writes a CSV summary to an evidence bucket for SOC 2 and ISO 27001 compliance.

## What the script does

- Enumerates all IAM users using paginated `ListUsers` API calls.
- For each user, checks for attached MFA devices via `ListMFADevices`.
- Creates a Security Hub finding per user with:
  - `PASSED` status if MFA is enabled
  - `FAILED` status + `HIGH` severity if MFA is missing
- Generates a CSV report with `UserName`, `CreateDate`, `PasswordEnabled`, `MFAEnabled`.
- Optionally uploads CSV evidence to S3.

The script can run as a standalone CLI tool, from GitHub Actions, or as an AWS Lambda function.

## Compliance Mapping

| Framework | Control | Description |
|-----------|---------|-------------|
| **SOC 2** | CC6.1.2 | Multi-factor authentication – logical access protected using MFA |
| **ISO 27001:2022** | A.9.2.3 | Management of secret authentication information |
| **ISO 27001:2022** | A.9.4.1 | Information access restriction |
| **PCI DSS** | Req. 7/8 | Access control & authentication – restrict access and identify/authenticate users |

## Required IAM permissions

At minimum, the execution role needs:

- **IAM read access**
  - `iam:ListUsers`
  - `iam:ListMFADevices`
- **Security Hub write access**
  - `securityhub:BatchImportFindings`
- **S3 write access** (optional, for evidence upload)
  - `s3:PutObject` on `arn:aws:s3:::<EVIDENCE_BUCKET>/iam-mfa-audit/*`

## CLI usage

```bash
python mfa_check.py --evidence-bucket <bucket> [--region us-east-1]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--evidence-bucket` | No | S3 bucket to upload CSV evidence (optional) |
| `--region` | No | AWS region (default: `us-east-1` or `AWS_REGION` env var) |

### Examples

```bash
# Run locally, print to console only
python mfa_check.py

# Run and upload evidence to S3
python mfa_check.py --evidence-bucket my-audit-evidence-bucket --region us-east-1
```

## Environment variables

| Variable | Description |
|----------|-------------|
| `AWS_REGION` | Default region if `--region` not specified |
| `AWS_DEFAULT_REGION` | Fallback region |

## Security Hub findings

Each user generates a finding with this structure:

```json
{
  "SchemaVersion": "2018-10-08",
  "Id": "iam-user-mfa-{username}",
  "Title": "IAM user '{username}' MFA enforcement check",
  "Description": "User has MFA enabled." | "User does NOT have MFA enabled.",
  "Severity": {"Normalized": 0} | {"Normalized": 80},
  "Compliance": {"Status": "PASSED"} | {"Status": "FAILED"},
  "Resources": [{"Type": "AwsIamUser", "Id": "arn:aws:iam::..."}]
}
```

## Evidence output

### CSV columns

- `UserName` – IAM user name
- `CreateDate` – Account creation date
- `PasswordEnabled` – Whether user has console password
- `MFAEnabled` – Boolean indicating MFA device presence

### S3 upload path

```
s3://<EVIDENCE_BUCKET>/iam-mfa-audit/mfa-users-<timestamp>.csv
```

## Running as Lambda

The script is idempotent and safe to run from Lambda:

1. Package `mfa_check.py` as a Lambda deployment ZIP
2. Set handler to `mfa_check.run` or wrap in a Lambda handler
3. Configure environment variables
4. Schedule via EventBridge (e.g., daily) or invoke manually

## Why this matters for AI automation

1. **Binary outcomes** – MFA pass/fail creates clean supervised learning datasets
2. **Identity risk scores** – Identity posture data trains user behavior analytics models
3. **Automated evidence** – Removes human judgment variance from compliance training data

## Related labs

- Lab 7 (IAM Role Review) – extends identity security to role trust policies
- Lab 6 (Continuous Monitoring) – aggregates MFA findings into Security Hub insights
- Lab 8 (Audit Pack Generator) – packages MFA evidence with other control artifacts
