# AWS Architect Fundamentals — Quiz Study Guide

Generated: 2025-09-23 18:56 PT
Location: `labs/lab6_continuous_monitoring/aws_architect_fundamentals_quiz_study_guide.md`

---

## Q1. What permissions options does an AMI have?

Options:
- Public Access, Owner only, Specific AWS Accounts
- Public Access, Owner only, Specific IAM users
- Public Access, Owner only, Specific Regions
- Public Access, Specific AWS Accounts, Specific IAM users

Answer: Public Access, Owner only, Specific AWS Accounts

Explanation:
An Amazon Machine Image (AMI) can be shared in three ways:
- Owner only — Only the creating account can use it.
- Specific AWS Accounts — Share with one or more AWS account IDs.
- Public — Any AWS account can use it.
IAM users and Regions are not valid share targets.

---

## Q2. What is NOT stored in an AMI?

Options:
- Boot volume
- Data volumes
- AMI Permissions
- Block Device Mapping
- Instance settings
- Network Settings

Answer: Network Settings

Explanation:
An AMI includes root (boot) volume, optional data volumes, block device mappings, some instance attributes (e.g., architecture), and its sharing permissions. Network settings (VPC, subnets, security groups, Elastic IPs) are specified at launch time, not stored in the AMI.

---

## Q3. EC2 is an example of which service model?

Options: PaaS, IaaS, SaaS, DBaaS, FaaS

Answer: IaaS (Infrastructure as a Service)

Explanation:
EC2 provides virtual servers, networking, and storage primitives. You manage the OS, runtime, apps, and data. PaaS abstracts the OS/platform; SaaS is fully managed software; DBaaS is managed databases; FaaS is event-driven functions.

---

## Q4. What is true of an AWS Public Service?

Options:
- Located in the public internet zone
- Located in the AWS Public zone
- Located in a VPC
- Publicly accessible by anyone
- Anyone can connect, but permissions are required to access the service

Answer: Anyone can connect, but permissions are required to access the service

Explanation:
Public AWS services (e.g., S3, DynamoDB) expose public endpoints reachable over the internet, but access is governed by IAM/resource policies. They are not “in your VPC” (though VPC endpoints can provide private access). “Public internet zone/AWS Public zone” are not official constructs.

---

## Q5. What is true of an AWS Private Service?

Options:
- Located on the Public Internet
- Located in the AWS Public Zone
- Located in a VPC
- Accessible from the VPC it is located in
- Accessible from any other VPC
- Accessible from other VPCs or on-premises networks as long as private networking is configured

Answer: Accessible from other VPCs or on-premises networks as long as private networking is configured

Explanation:
Private services (e.g., EC2 instances, RDS) reside in a VPC and are not internet-accessible by default. They are reachable within the same VPC and can be exposed to other VPCs or on-prem via VPC peering, PrivateLink, Transit Gateway, VPN, or Direct Connect. Not automatically reachable from “any” VPC.

---

## Q6. What is true of Simple Storage Service (S3)?

Mark all that apply:
- [x] S3 is an AWS Public Service
- [ ] S3 is a private service
- [ ] S3 is a web-scale block storage system
- [x] S3 is an object storage system
- [ ] Buckets can store a limit of 100TB of data
- [x] Buckets can store an unlimited amount of data

Explanation:
S3 is object storage, publicly reachable via AWS endpoints, with effectively unlimited bucket capacity (each object up to 5 TB). It is not block storage—that’s EBS.

---

## Q7. What is a CloudFormation Logical Resource?

Options:
- A resource in a stack which hasn't been created yet
- A resource defined in a CloudFormation Template
- A resource created in an AWS Account by CloudFormation
- A name given to a resource created with best practice config

Answer: A resource defined in a CloudFormation Template

Explanation:
Logical resources are the template-defined entities (logical IDs) CloudFormation uses to create actual infrastructure. Their realized counterparts are physical resources.

---

## Q8. What is a CloudFormation Physical Resource?

Options:
- A resource defined in a CloudFormation template i.e EC2Instance
- A physical resource created by creating a CloudFormation stack
- A product in AWS which is a physical piece of hardware i.e a router
- None of the above

Answer: A physical resource created by creating a CloudFormation stack

Explanation:
Physical resources are the real AWS resources that exist in your account after the stack is created, corresponding to logical resources from the template.

---

## Q9. How many DNS root servers exist?

Answer: 13

Explanation:
There are 13 logical root servers (A–M). Each is backed by many globally distributed anycast instances.

---

## Q10. Who manages the DNS Root Servers?

Answer: 12 Large Organisations

Explanation:
The 13 logical root servers are operated by 12 independent organizations (e.g., Verisign, USC/ISI, ICANN, etc.).

---

## Q11. Who manages the DNS Root Zone?

Answer: IANA

Explanation:
IANA (operated by ICANN) maintains and publishes the root zone file and coordinates TLD changes.

---

## Q12. Which type of organization maintains the zones for a TLD (e.g., .ORG)?

Answer: Registry

Explanation:
A registry (e.g., PIR for .org) operates the authoritative name servers and maintains the TLD’s zone data.

---

## Q13. Which type of organization can register domains under .org via agreements with the registry?

Answer: Registrar

Explanation:
Accredited registrars (e.g., GoDaddy, Namecheap) sell domains to end users and interface with the registry.

---

## Q14. How many subnets are in a default VPC?

Answer: Equal to the number of Availability Zones (AZs) in the region where the VPC exists

Explanation:
AWS creates one default subnet per AZ in the region for the default VPC, enabling high availability across AZs.

---

## IAM & Orgs Section Quiz

### Q1. Is there a limit to the number of IAM users in an AWS Account? If so, how many?

Options: No Limit, 1,000 per region, 3,000 per account, 5,000 per account, 5,000 per region

Answer: 5,000 per account

Explanation:
IAM is a global service. The default, fixed limit is 5,000 IAM users per AWS account (not per region).

---

### Q2. Which of the following are features of IAM Groups?

Options:
- Admin groupings of IAM Users
- Can hold Identity Permissions
- Can be used to login (Access Keys)
- Can be used to login (Username and password)
- Can be nested

Answer: Admin groupings of IAM Users; Can hold Identity Permissions

Explanation:
Groups organize users and can have policies attached that members inherit. Groups are not identities (no credentials) and cannot be nested.

---

### Q3. Within AWS policies, what is always a priority?

Options: Explicit Allow, Explicit Deny, Depends on the order in the policy, No priority

Answer: Explicit Deny

Explanation:
Evaluation order: implicit deny by default; explicit allow grants access; any explicit deny overrides all allows.

---

### Q4. What two policies are assigned to an IAM Role?

Options: Permissions Policy, Assumption Policy, Resource Policy, Trust Policy

Answer: Permissions Policy; Trust Policy (aka Assumption Policy)

Explanation:
Permissions policy defines what the role can do. Trust policy defines who can assume the role (principals allowed to call sts:AssumeRole).

---

### Q5. Which of the following are true for IAM Roles?

Options:
- Roles have associated Long Term Credentials (Access Keys)
- Roles can be assumed
- When assumed — temporary credentials are generated
- Roles can be logged into
- When an identity logs into a role — temporary credentials are generated

Answer: Roles can be assumed; When assumed — temporary credentials are generated; When an identity assumes a role — temporary credentials are generated

Explanation:
Roles don’t have long-term credentials and you don’t log into a role directly. You authenticate as a user/service, then assume the role to receive temporary STS credentials.

---

### Q6. What three features are provided by AWS Organizations? (pick all that apply)

Options:
- Consolidated billing
- Managed assistance for company and AWS account mergers
- AWS Account restrictions using SCP
- Account organisation via OU's
- Protection against credential leaks
- Company ID reports

Answer: Consolidated billing; AWS Account restrictions using SCP; Account organisation via OU's

Explanation:
Organizations provides consolidated billing, policy guardrails via SCPs, and hierarchical account grouping with OUs. The other options are not features of Organizations.

---

### Q7. What functionality is provided by CloudTrail?

Options: Log Ingestion, Metrics management, Account Restrictions, Account wide Auditing and API Logging

Answer: Account wide Auditing and API Logging

Explanation:
CloudTrail records account activity and API events across services. Log ingestion and metrics are CloudWatch concerns; account restrictions are via IAM/SCPs.

---

### Q8. Is it possible to restrict what the Account Root User can do?

Options: Always, Never, If AWS Organizations are used, If AWS Organizations are used .. but not the management account

Answer: If AWS Organizations are used .. but not the management account

Explanation:
SCPs can restrict root users of member accounts in an Organization. SCPs do not apply to the management account’s root user.

---

### Q9. What is Role Switching?

Options:
- Changing the permissions on an IAM Role
- Changing the TRUST on a Role
- Changing who can assume a Role
- Logging into a Role
- Assuming a role in another AWS account to access that account via the console UI

Answer: Assuming a role in another AWS account to access that account via the console UI

Explanation:
Role switching lets a signed-in user assume a role (often in another account) via the console to operate with the role’s permissions, without separate login.

---

### Q10. What are valid IAM Policy types? (choose all that apply)

Options: AWS Managed Policy, Customer Managed Policy, Self-Managed Policy, Inline Policies, External Policies

Answer: AWS Managed Policy; Customer Managed Policy; Inline Policies

Explanation:
Valid IAM policy types are AWS managed, customer managed, and inline. “Self-Managed” and “External Policies” are not IAM policy types.
