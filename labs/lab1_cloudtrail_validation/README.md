# Lab 1 – CloudTrail Multi-Region Validation

This lab implements a Python Lambda/script that validates **every AWS region** has at least one **multi-region CloudTrail** and writes a JSON evidence file to an S3 bucket.

## What the Lambda / script does

- Enumerates all available CloudTrail regions using `boto3.session.Session().get_available_regions("cloudtrail")`.
- For each region, calls `DescribeTrails` and filters for trails where `IsMultiRegionTrail` is `True`.
- Builds a `region_results` map with:
  - `has_multi_region_trail` (boolean)
  - `trails` (list of trail names) or an `error` code if the region cannot be queried.
- Computes a `summary` with counts of:
  - `regions_with_trail`
  - `regions_missing`
- Writes a timestamped JSON object to the evidence S3 bucket under the prefix:
  - `cloudtrail-validation/<timestamp>.json`
- Logs the full JSON to CloudWatch Logs when run as a Lambda.

The Lambda entrypoint is the `handler(event, context)` function in `cloudtrail_validator.py`. A small `main()` wrapper allows the same file to be run as a standalone script.

## Required IAM permissions

At minimum, the execution role for this Lambda/Script needs:

- **CloudTrail read access**
  - `cloudtrail:DescribeTrails`
- **S3 write access** to the evidence bucket
  - `s3:PutObject` on `arn:aws:s3:::<EVIDENCE_BUCKET>/cloudtrail-validation/*`

This lab folder includes an example IAM policy document:

- `cloudtrail-read-s3put.json` – allows `DescribeTrails` and `s3:PutObject` to the evidence bucket.

## Environment variable: `EVIDENCE_BUCKET`

The Lambda/script expects an environment variable:

- `EVIDENCE_BUCKET` – name of the S3 bucket where JSON evidence will be written.

When deployed as a Lambda, configure this environment variable in the Lambda console or via IaC. When run from GitHub Actions, `EVIDENCE_BUCKET` is provided via a GitHub secret (see below).

## How to deploy / invoke

### 1. As a Lambda function

1. Package the `cloudtrail_validator.py` file (and any dependencies) into a deployment ZIP.
2. Create a Lambda function in AWS using Python runtime.
3. Attach an IAM role that has the permissions described above.
4. Set the handler to `cloudtrail_validator.handler`.
5. Configure the `EVIDENCE_BUCKET` environment variable.
6. Invoke the Lambda manually, via a schedule, or from a pipeline. Each invocation writes a new JSON file to S3.

### 2. As a Python script (local or CI)

You can also run the validator directly as a script using the `main()` entrypoint:

```bash
export EVIDENCE_BUCKET=<your-evidence-bucket>
python labs/lab1_cloudtrail_validation/labs/lab1_cloudtrail_validation/cloudtrail_validator.py
```

This will execute the same logic as the Lambda handler and print a JSON summary to stdout. The full evidence JSON is still written to S3 using the `EVIDENCE_BUCKET` value.

## GitHub Actions workflow (CI automation)

This repository includes a GitHub Actions workflow that runs the CloudTrail validation on a schedule and on manual trigger:

- File: `.github/workflows/lab1_cloudtrail_validation.yml`
- Triggers:
  - `schedule`: daily at 06:00 UTC
  - `workflow_dispatch`: manual run from the Actions tab

### OIDC role assumption

The workflow uses **GitHub OIDC** to assume an AWS IAM role with least privilege. It expects the following secrets to be defined in the GitHub repository:

- `LAB1_AWS_ROLE_ARN` – ARN of the IAM role that trusts GitHub OIDC and has the required CloudTrail + S3 permissions.
- `LAB1_EVIDENCE_BUCKET` – name of the S3 bucket used for evidence.

The workflow:

1. Checks out the repo.
2. Configures AWS credentials via `aws-actions/configure-aws-credentials@v4` using `LAB1_AWS_ROLE_ARN`.
3. Sets up Python.
4. Installs `boto3` and `botocore`.
5. Runs `cloudtrail_validator.py` as a script, which writes the evidence JSON to S3 and prints the summary.
6. Captures the printed summary into `labs/lab1_cloudtrail_validation/out.json` and uploads it as a workflow artifact.

## Where evidence is stored

- **Primary evidence**: JSON objects written to S3 at:
  - `s3://<EVIDENCE_BUCKET>/cloudtrail-validation/<timestamp>.json`
- **Summary evidence in CI**: `out.json` file stored under `labs/lab1_cloudtrail_validation/out.json` and attached to each GitHub Actions run as an artifact.

These artifacts provide audit-ready evidence that CloudTrail is configured across regions and can be referenced in your ISO 27001 control documentation.
