# Lab 5 – SG Drift Detection: Fix Notes

Date: 2025-09-10

This note records the steps required to unblock the **Lab 5 SG Drift Detection** workflow after the initial *`sts:AssumeRoleWithWebIdentity`* failure.

## Root cause
The GitHub Actions workflow tried to assume an IAM role that lacked a matching **OIDC trust policy** and permissions to update the Lambda function.

## Fix summary
1. **Created a dedicated OIDC role** `github-actions-sg-drift`.
2. **Trust policy** – allows GitHub OIDC tokens from this repository:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::097089567108:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:nelsonrosario89/first_one_nellz:*"
        }
      }
    }
  ]
}
```
3. **Inline permissions policy** – least-privilege Lambda access:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "lambda:UpdateFunctionCode",
        "lambda:GetFunction",
        "lambda:InvokeFunction"
      ],
      "Resource": "arn:aws:lambda:us-east-1:097089567108:function:sg_drift_checker"
    }
  ]
}
```
4. **Repository secret** – updated `AWS_ASSUME_ROLE_ARN` with the new role ARN.
5. **Result** – Workflow run #17 completed successfully; Lambda code updated and test event invoked.

## Future hardening
* Change `StringLike` wildcard to the exact branch when ready (e.g. `...:ref:refs/heads/main`).
* Rotate to a managed policy only if more Lambda permissions are needed.
