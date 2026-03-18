# Lab 2 – EC2 Inventory & Categorization

This lab implements a Python Lambda/script that collects a **cross-region inventory of EC2 instances**, categorizes them by scope tags, and uploads a CSV evidence file to S3 for ISO 27001 asset inventory compliance.

## What the Lambda / script does

- Enumerates all available EC2 regions using `boto3.session.Session().get_available_regions("ec2")`.
- For each region, calls `DescribeInstances` via paginator to handle large result sets.
- Flattens instance data into a single-level dictionary with:
  - `region`, `instance_id`, `name` (from Name tag), `state`, `vpc_id`
  - `security_groups` – comma-separated security group IDs
  - `in_scope` – boolean indicating if instance matches scope criteria
  - All tags as `tag_{key}` columns for auditor context
- Computes in-scope status based on configurable tag filter (default: `Scope=In`).
- Writes a timestamped CSV file to S3 under the prefix:
  - `ec2-inventory/{timestamp}.csv`
- Logs a JSON summary with total instances and in-scope counts.

The Lambda entrypoint is the `handler(event, context)` function in `ec2_inventory.py`. A CLI entrypoint (`cli()`) allows the same file to be run locally.

## Compliance Mapping

| Framework | Control | Description |
|-----------|---------|-------------|
| **ISO 27001:2022** | A.8.1.1 | Inventory of assets – information assets are identified and an inventory is maintained |
| **SOC 2** | CC6.1.4 | Firewalls and security groups – network access is restricted using security controls |
| **PCI DSS** | Req. 2 | System component inventory |

## Required IAM permissions

At minimum, the execution role for this Lambda/Script needs:

- **EC2 read access**
  - `ec2:DescribeInstances`
  - `ec2:DescribeRegions` (for cross-region enumeration)
- **S3 write access** to the evidence bucket
  - `s3:PutObject` on `arn:aws:s3:::<EVIDENCE_BUCKET>/ec2-inventory/*`

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `EVIDENCE_BUCKET` | Yes | S3 bucket where CSV evidence will be written |
| `SCOPE_TAG` | No | Tag key=value for scoping (default: `Scope=In`) |

## How to deploy / invoke

### 1. As a Lambda function

1. Package the `ec2_inventory.py` file into a deployment ZIP.
2. Create a Lambda function in AWS using Python runtime.
3. Attach an IAM role with the permissions described above.
4. Set the handler to `ec2_inventory.handler`.
5. Configure environment variables (`EVIDENCE_BUCKET`, optional `SCOPE_TAG`).
6. Invoke manually, via schedule, or from a pipeline.

### 2. As a Python script (local or CI)

```bash
python ec2_inventory.py --bucket <EVIDENCE_BUCKET> [--scope-tag "Scope=In"]
```

Example:
```bash
python ec2_inventory.py --bucket my-audit-evidence-bucket --scope-tag "Environment=Production"
```

## Evidence output

### CSV columns

- `region` – AWS region where instance runs
- `instance_id` – EC2 instance identifier
- `name` – Value of Name tag (if any)
- `state` – Instance state (running, stopped, etc.)
- `vpc_id` – VPC identifier
- `security_groups` – Comma-separated security group IDs
- `in_scope` – Boolean (true if instance matches scope tag)
- `tag_*` – One column per tag key for full context

### Sample output

```csv
region,instance_id,name,state,vpc_id,security_groups,in_scope,tag_Name,tag_Environment
us-east-1,i-0abc123,web-server,running,vpc-123,sg-456|sg-789,true,web-server,Production
us-west-2,i-0def456,api-worker,stopped,vpc-789,sg-012,false,api-worker,Development
```

## Where evidence is stored

- **Primary evidence**: CSV files written to S3 at:
  - `s3://<EVIDENCE_BUCKET>/ec2-inventory/<timestamp>.csv`
- **CloudWatch Logs**: JSON summary with instance counts

These artifacts provide audit-ready evidence of asset inventory for ISO 27001 A.8.1.1 and can be referenced in control documentation.

## Why this matters for AI automation

1. **Structured asset data** – Normalized inventory feeds ML models for security baseline establishment
2. **Tag-based categorization** – Enables AI auto-classification of resources by risk profile
3. **Continuous collection** – Real-time inventory updates support predictive drift forecasting

## Related labs

- Lab 1 (CloudTrail Validation) – provides audit trail for instance launches
- Lab 5 (Security Group Drift) – monitors security group changes on inventoried instances
- Lab 8 (Audit Pack Generator) – packages this evidence with other control artifacts
