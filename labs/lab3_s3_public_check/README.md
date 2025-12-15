# Lab 3 – Auto-Detect Public S3 Buckets

This lab’s script (`s3_public_check.py`) inspects every bucket in the account and publishes a **Security Hub** finding for each bucket that is publicly accessible (ACL or bucket policy).

## Architecture & Evidence Flow

- GitHub Actions workflow `lab3_s3_public_check` runs in the **Production** account using GitHub OIDC to assume the `lab3_s3_public_check` IAM role.
- The script calls `s3.list_buckets()`, inspects each bucket’s ACL and bucket policy for public (`"*"`) principals, and builds a summary of public buckets.
- Findings are pushed to **Security Hub** in the Production account via `BatchImportFindings`.
- When the `--evidence-bucket` parameter is provided (via the `LAB3_EVIDENCE_BUCKET` secret), the script uploads a JSON summary to the centralized evidence bucket in the **Management/General** account:
  - Bucket: `aws-cloudtrail-logs-295070998992-4ab61dec`
  - Key prefix: `s3-public-audit/summary-<timestamp>.json`

## How the Automation Maps to Security Hub

* Each non-compliant bucket is emitted as a **`Software and Configuration Checks/90000002`** finding (category *Security Best Practices*).
* The finding severity is set to **`HIGH`** and the `Compliance.RelatedRequirements` field is populated with `ISO_27001:A.9.4.1` (Information Access Restriction).

## Sample Finding (truncated)

```json
{
  "SchemaVersion": "2018-10-08",
  "Id": "arn:aws:s3:::public-website-bucket",
  "ProductArn": "arn:aws:securityhub:us-east-1:123456789012:product/123456789012/default",
  "GeneratorId": "lab3_s3_public_check",
  "AwsAccountId": "123456789012",
  "Types": [
    "Software and Configuration Checks/90000002"
  ],
  "CreatedAt": "2025-08-19T10:00:00Z",
  "UpdatedAt": "2025-08-19T10:00:00Z",
  "Severity": { "Label": "HIGH" },
  "Title": "S3 bucket public-website-bucket allows public access",
  "Description": "The bucket's ACL or bucket policy allows public read or write operations.",
  "Compliance": {
    "Status": "FAILED",
    "RelatedRequirements": [
      "ISO_27001:A.9.4.1"
    ]
  },
  "Resources": [
    {
      "Type": "AwsS3Bucket",
      "Id": "arn:aws:s3:::public-website-bucket",
      "Region": "us-east-1"
    }
  ]
}
```

> **Tip**  Copy the JSON above, modify the bucket name and account ID, and attach it to audit evidence packages for a ready-made example.
