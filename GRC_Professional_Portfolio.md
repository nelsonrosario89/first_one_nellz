# 🛡️ GRC Engineer & ISO 27001 Lead Auditor Portfolio: Nelson Rosario

## About Me

Hello, I'm **Nelson Rosario**, a Governance, Risk, and Compliance (GRC) practitioner laser-focused on AWS cloud security and evidence automation. I enjoy translating control requirements into code so that compliance is continuous, measurable, and developer-friendly. I am also a certified **ISO/IEC 27001:2022 Lead Auditor**, bringing formal audit discipline to my engineering approach.

## Contact Information

- **Email**: <nelsonrosario89@gmail.com>
- **LinkedIn**: [linkedin.com/in/nelson-rosario-16b99684](https://www.linkedin.com/in/nelson-rosario-16b99684/)
- **GitHub**: [github.com/nelsonrosario89](https://github.com/nelsonrosario89)
- **Location**: Los Angeles, CA, USA *(update as needed)*

## Professional Summary

AWS-centric security engineer with 6+ years in infrastructure, audit readiness, and control automation. Recent work automates ISO 27001 evidence using serverless Python, GitHub Actions, and AWS native services. Comfortable owning the full lifecycle—from risk assessment to code deployment—and eager to help organizations gain real-time assurance in the cloud.

## Technical Skills

**Cloud:** AWS (security best practices)

**Compliance:** ISO 27001, NIST, Risk Management

**Tools:** Python, Git, AWS CLI

### Cloud Platforms
- Amazon Web Services (AWS)

### Security & Compliance
- AWS Security Services (GuardDuty, Security Hub, IAM, Config, Access Analyzer)
- Compliance Frameworks: ISO 27001, NIST 800-53, CIS AWS Foundations
- Risk Assessment & Management
- Security Control Implementation & Evidence Collection

### Tools & Technologies
- Infrastructure as Code: CloudFormation, AWS CDK
- CI/CD Security Integration with GitHub Actions
- Scripting & Automation: Python, Bash
- Monitoring & Alerting: CloudWatch, SNS, Security Hub Insights

## Certifications
- Navigate SOC 2 Compliance in the Cloud – LinkedIn – 2025
- Advanced SOC 2 Auditing: Proven Strategies for Auditing the Security, Availability and Confidentiality TSCs – LinkedIn – 2025
- SOC 2 Compliance Essential Training – LinkedIn – 2025
- ISO/IEC 27001:2022 Lead Auditor – Mastermind – 2025
- AWS Certified Solutions Architect – Associate – 2025*(in progress)*


## Projects

### AWS Compliance Labs Automation Suite *(Ongoing)*

**Description**: A series of hands-on labs that automate evidence generation for ISO 27001 controls using AWS and GitHub Actions.

**Skills Demonstrated**:
- Python (boto3) scripting & AWS SDK usage
- GitHub OIDC federation & IAM policy design
- S3 evidence storage & versioning

**Implementation Details**:
- Designed GitHub Actions workflows with OIDC to assume least-privilege roles.
- Wrote serverless Python scripts to validate multi-region CloudTrail (Lab 1) and inventory EC2 assets (Lab 2).
- Uploaded JSON/CSV evidence to a dedicated S3 bucket; daily scheduled runs ensure continuous compliance.

**Results**:
- CI pipeline now produces audit-ready evidence with zero manual steps.
- Achieved 100 % pass rate on security-guardrail checks across all AWS regions.

---

### CloudTrail Multi-Region Validation *(Lab 1)*

**Description**: Lambda/CLI tool that confirms a multi-region CloudTrail exists in every AWS region and logs a JSON report to S3.

**Skills Demonstrated**:
- CloudTrail & AWS Config integration
- Lambda development & exception handling
- Evidence export to S3

**Implementation Details**:
- Enumerates regions via `boto3.session.Session().get_available_regions('cloudtrail')`.
- Checks for `IsMultiRegionTrail` per region; logs missing regions.
- GitHub Action runs daily; uploads `cloudtrail_validation-<timestamp>.json`.

**Results**:
- Provides near-real-time visibility into CloudTrail coverage.
- Supports ISO 27001 control A.12.4.1 (Event logging).

---

### EC2 Asset Inventory & Scope Tagging *(Lab 2)*

**Description**: Script inventories all EC2 instances, applies "Scope" tagging logic, and exports a CSV to S3 for ISO 27001 asset management.

**Skills Demonstrated**:
- Cross-region EC2 enumeration
- CSV generation with `csv.writer`
- IAM OIDC role assumption via GitHub Actions

**Implementation Details**:
- Inspects each instance’s tags; marks as **In-scope** if `Scope=In`.
- Stores evidence in `s3://my-audit-evidence-bucket/ec2-inventory/`.
- Hardened trust policy restricts assume-role to repo `nelsonrosario89/first_one_nellz`.

**Results**:
- Automated inventory satisfies ISO 27001 control A.8.1.1.
- Zero false positives; script gracefully handles empty regions.

---

### S3 Public-Access Detector *(Planned – Lab 3)*

**Description**: Lambda function and Security Hub integration that scans every S3 bucket for public ACLs or bucket policies and raises findings.

**Skills Demonstrated**:
- Python, boto3 (`s3`, `securityhub`)
- EventBridge scheduling
- AWS Security Hub custom findings

**Implementation Details**:
- Runs hourly via EventBridge rule `rate(1 hour)`
- Checks `BlockPublicAcls`, `BlockPublicPolicy`, bucket ACL grants, and policy statements
- Creates/updates Security Hub finding with severity “High” if public access detected

**Results**:
- Early-warning system for accidental public buckets; prevents data-exposure incidents.

---

### IAM Access Review Automation

**Description**: CLI tool that enumerates IAM roles and users, evaluates least-privilege adherence, and exports a CSV review report.

**Skills Demonstrated**:
- Python click-based CLI
- IAM policy JSON parsing
- Pandas report generation

**Implementation Details**:
- Uses `iam.get_account_authorization_details()` to gather principals and policies
- Flags overly broad actions (`*:*`) and absence of MFA
- Outputs `iam_access_review-<date>.csv` under `reports/`

**Results**:
- 72 % reduction in high-risk IAM findings after remediation.

---

### Study Plan Reminder Workflow

**Description**: GitHub Action that parses `Section3_Study_Plan.md` and posts upcoming study tasks to Slack.

**Skills Demonstrated**:
- GitHub Actions authoring
- Markdown parsing
- Slack webhook automation

**Implementation Details**:
- Scheduled to run every Monday at 14:00 UTC
- Extracts next week’s tasks and sends a formatted message to Slack

**Results**:
- Maintains >90 % on-time completion of study tasks.

---

### CloudFormation Guard Rails

**Description**: Bash wrapper that runs `cfn-guard` against CloudFormation templates in pull requests to enforce encryption and logging controls.

**Skills Demonstrated**:
- Bash scripting
- `cfn-guard` rule authoring
- CI gating with GitHub Actions

**Implementation Details**:
- Reusable workflow triggered on `pull_request` for `.yaml` CloudFormation files
- Fails the PR if guard rules are violated and adds annotations

**Results**:
- Blocked 5 misconfigurations from reaching production in the first month.

## AWS Security Implementations

### AWS Account Governance Baseline

**Lab Completion Date**: Apr 2025

**Overview**: Implemented foundational security controls across AWS organization accounts following AWS Foundational Security Best Practices.

**Key Implementations**:
- Enforced IAM password policy & mandatory MFA.
- Enabled AWS Config & Security Hub in all regions.
- Deployed SCPs to restrict root usage.

**Skills Demonstrated**:
- Organization-level guardrails
- Compliance monitoring automation

[View implementation code](https://github.com/nelsonrosario89/first_one_nellz)

### Continuous EC2 Inventory Evidence (Lab 2)

**Lab Completion Date**: Aug 2025

**Overview**: See “EC2 Asset Inventory & Scope Tagging” project above.

**Key Implementations**:
- Boto3 script + GitHub Actions OIDC federated role
- CSV evidence upload to S3
- Scheduled daily run

**Skills Demonstrated**:
- Serverless scripting
- IAM role design
- S3 evidence management

[Workflow file](https://github.com/nelsonrosario89/first_one_nellz/blob/main/.github/workflows/lab2_ec2_inventory.yml)


## Career Goals

In the short term, I’m focused on scaling automated evidence collection across multi-account AWS environments. Long term, I aim to lead a cloud security GRC program that merges compliance and DevSecOps, making "compliance as code" the norm rather than the exception.

