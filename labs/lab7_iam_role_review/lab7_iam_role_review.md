**Lab 7 – IAM Role Review (ISO 27001 A.9.1.2)**  
In this lab I treat AWS IAM roles as the primary entry points to networked services and automate a recurring review of who can assume them. An organization‑wide, multi‑region CloudTrail trail in the management account (295070998992) captures all `AssumeRole` activity across member accounts. A scheduled Lambda function (`lab7-role-review`) runs every 14 days, queries CloudTrail for `AssumeRole` events targeting my scoped roles (access‑review Lambda in the management account and two production roles used by GitHub Actions and continuous monitoring), and enriches each event with IAM trust‑policy data where available. The function writes a CSV report to an evidence bucket (`s3://aws-cloudtrail-logs-295070998992-4ab61dec/grc-audit-evidence/lab7-*`) with columns for `RoleArn`, `PrincipalType`, `Principal`, `SourceIp`, `EventTime`, and `InTrustPolicy`. This provides timestamped, repeatable evidence that only defined principals can assume critical roles and that any unexpected access paths would be surfaced for investigation, supporting ISO 27001 A.9.1.2.

**Lab 7 Evidence Artifacts**

- **Scope table:** IAM role scope worksheet covering management and production roles (saved in portfolio notes).
- **Automation code:** Screenshot of the `lab7-role-review` Lambda configuration and Python handler.
- **Schedule:** Screenshot of EventBridge rule `lab7-role-review-every-2-weeks` (enabled, `rate(14 days)`).
- **CSV report:** `lab7-role-review-<timestamp>.csv` in  
  `s3://aws-cloudtrail-logs-295070998992-4ab61dec/grc-audit-evidence/`  
  (screenshot of the CSV header in Numbers/Excel).
- **Trust diagram:** `lab7_trust_diagram.png` showing CloudTrail → Lambda → S3, plus GitHub OIDC and Lambda service principals mapped to the in‑scope roles.
