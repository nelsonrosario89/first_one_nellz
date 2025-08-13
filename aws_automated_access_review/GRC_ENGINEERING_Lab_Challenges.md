# GRC Engineering Lab Challenges (ISO 27001-Focused)

A progressive set of hands-on challenges that demonstrate how to gather audit evidence, automate controls, and map AWS security services to ISO 27001 Annex A requirements.  Each lab entry provides:

* **Objective** – what you will achieve
* **AWS Services** – primary services used
* **Python Automation** – the script/Lambda goal
* **ISO 27001 Control** – mapped clause
* **Documentation Notes** – tips on what evidence to capture for the portfolio

---

## 🟢 Beginner Labs — Level 1: Foundational Evidence Collection

### Lab 1 – Validate CloudTrail is Enabled & Multi-Region
* **Objective:** Ensure CloudTrail records events in *all* regions.
* **AWS Services:** CloudTrail, AWS Config
* **Python Automation:** Lambda enumerates every region, verifies at least one *multi-region* trail is active, and logs results to S3/DynamoDB.
* **ISO 27001 Control:** A.12.4.1 – *Event Logging*
* **Documentation Notes:**  
  * Provide a region-by-region CSV/JSON showing trail status.  
  * Add screenshots of CloudTrail & Config rules for evidence.

---

### Lab 2 – Inventory & Categorize EC2 Instances
* **Objective:** Produce an asset inventory of EC2 instances with security-group and tag context.
* **AWS Services:** EC2, AWS Config
* **Python Automation:** Boto3 script pulls all instances, parses SG rules & tags, auto-labels items as **in-scope** / **out-of-scope** and exports CSV.
* **ISO 27001 Control:** A.8.1.1 – *Inventory of Assets*
* **Documentation Notes:**  
  * **Workflow triggers:** automatically on `push` to any file in `labs/lab2_ec2_inventory/**`, on a daily schedule at 06:00 UTC, or via the **Run workflow** button in the Actions tab.  
  * **Evidence location:** CSV files are written to `s3://my-audit-evidence-bucket/ec2-inventory/` (one per run, timestamp-keyed).  
  * **CSV columns:** `InstanceId`, `Name`, `State`, `VpcId`, `SecurityGroups`, `Tags`, `Scope` ("In" / "Out").  
  * **Scope logic:** any instance with tag `Scope=In` (case-insensitive) is flagged **in-scope** for compliance reporting; everything else is **out-of-scope**.  
  * **Successful run evidence:** GitHub Actions run `ec2-inventory` on commit `75fa812` (2025-08-10) finished green and uploaded `ec2-inventory-2025-08-10T23:21Z.csv` to S3.  
  * **Next improvements:** add unit tests with `pytest` + `moto`, consider deploying the script as a scheduled Lambda via EventBridge, and add a workflow-status badge to the project README.

---

## 🟡 Intermediate Labs — Level 2: Continuous Monitoring & Alerting

### Lab 3 – Auto-Detect Public S3 Buckets
* **Objective:** Identify and flag S3 buckets with public access.
* **AWS Services:** S3, Security Hub, GitHub Actions (OIDC-assumed role)
* **Python Automation:** Daily GitHub Actions job runs `s3_public_check.py`, scans bucket ACLs & policies, publishes **Security Hub** findings, and uploads a JSON summary to the evidence S3 bucket.
* **ISO 27001 Control:** A.9.4.1 – *Information Access Restriction*
* **Workflow triggers:** on any `push` to `labs/lab3_s3_public_check/**`, at 06:15 UTC daily, or manual **Run workflow** in the Actions tab.
* **Evidence location:** JSON summary written to `s3://<EVIDENCE_BUCKET>/s3-public-audit/` (timestamp-keyed).
* **Security Hub finding schema (trimmed):**
  ```json
  {
    "Id": "s3-public-access-example-bucket",
    "GeneratorId": "s3-public-access-check",
    "Title": "S3 bucket 'example-bucket' public access check",
    "Severity": {"Normalized": 8},
    "Compliance": {"Status": "FAILED"},
    "Resources": [{"Type": "AwsS3Bucket", "Id": "arn:aws:s3:::example-bucket"}]
  }
  ```
* **Next improvements:**
  * Convert script to Lambda + EventBridge hourly trigger for faster detection.
  * Add unit tests with `moto` mocking bucket ACL/policy scenarios.
  * Build a Security Hub **Insight** to track public buckets over time.


---

### Lab 4 – MFA Enforcement Evidence Collection
* **Objective:** Detect IAM users without MFA.
* **AWS Services:** IAM, Lambda, AWS Config
* **Python Automation:** Scheduled Lambda lists IAM users, filters non-MFA users, stores results in Security Hub or DynamoDB.
* **ISO 27001 Control:** A.9.2.3 – *Management of Privileged Access Rights*
* **Documentation Notes:**  
  * Describe scan frequency & retention.  
  * Include a 30-day compliance trend graph.

---

### Lab 5 – Security Group Drift Detection
* **Objective:** Alert on security-group changes (e.g., port 22 opened).
* **AWS Services:** AWS Config, CloudWatch, Lambda
* **Python Automation:** Custom Config rule triggers Lambda that inspects diff and publishes alerts to SNS.
* **ISO 27001 Control:** A.13.1.1 – *Network Controls*
* **Documentation Notes:**  
  * Provide screenshots of CloudWatch alarms & SNS topics.  
  * Link to related network policy.

---

## 🔴 Advanced Labs — Level 3: Automated Audit Evidence & Risk-Based Alerts

### Lab 6 – Continuous Control Monitoring with Custom Security Hub Insights
* **Objective:** Track control effectiveness via custom insights.
* **AWS Services:** Security Hub, Lambda, CloudWatch
* **Python Automation:** Lambda builds tag-based insights (e.g., *production* resources) and pushes metrics to CloudWatch.
* **ISO 27001 Control:** A.18.2.3 – *Technical Compliance Review*
* **Documentation Notes:**  
  * Include insight queries & resulting graphs.  
  * Map each insight to the control narrative.

---

### Lab 7 – Automated Role Review for ISO 27001 Access Control
* **Objective:** Audit who can assume every IAM role.
* **AWS Services:** IAM, Lambda, CloudTrail
* **Python Automation:** Analyze CloudTrail `AssumeRole` events, generate cross-account access report with timestamps.
* **ISO 27001 Control:** A.9.1.2 – *Access to Networks & Network Services*
* **Documentation Notes:**  
  * Provide a trust-relationship diagram.  
  * Attach CSV report; optionally email to reviewers.

---

### Lab 8 – Lambda-Powered Audit Pack Generator
* **Objective:** Monthly ZIP of ISO 27001 evidence artifacts.
* **AWS Services:** Lambda, S3, AWS Config, Security Hub, CloudTrail
* **Python Automation:** Lambda compiles key reports (CloudTrail status, IAM users, MFA logs, Config snapshots) into one ZIP in S3 with a README mapping each file to controls.
* **ISO 27001 Control:** A.18.2.1 – *Independent Review of Information Security*
* **Documentation Notes:**  
  * Show README sample with control-to-file mapping.  
  * Include retention policy for evidence.

---

## 🧠 Bonus Challenge — Certification-Level Project

### Lab 9 – End-to-End ISO 27001 Control Dashboard
* **Objective:** Real-time dashboard of ISO 27001 compliance status.
* **AWS Services:** Lambda, Security Hub, DynamoDB, CloudWatch, Amplify / React
* **Python Automation:** Backend aggregates findings → maps to ISO 27001 Annex A controls → stores in DynamoDB; frontend reads data to display interactive compliance view.
* **ISO 27001 Controls:** Multiple (full coverage)
* **Documentation Notes:**  
  * Treat deliverables like an audit: include screenshots, audit trails, timestamps.  
  * Add “evidence quality” comments for each control.

---

*Happy building & auditing!*
