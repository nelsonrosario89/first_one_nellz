# Lab 6 – Postmortem: Issues Encountered and How We Fixed Them

This document captures the problems we hit while implementing Lab 6 (Continuous Control Monitoring with a custom Security Hub Insight), the root causes, and the exact fixes we applied.

Key files:
- Workflow: `.github/workflows/lab6_continuous_monitoring.yml`
- Lambda: `labs/lab6_continuous_monitoring/continuous_control_monitor.py`
- README: `labs/lab6_continuous_monitoring/README.md`
- Dashboard JSON: `dashboards/continuous_monitor_dashboard.json`

## Summary Timeline
- Fixed YAML syntax in GitHub Actions.
- Corrected IAM trust for Lambda execution role and permissions.
- Made the workflow idempotent for first deploys (no update while create is Pending).
- Created EventBridge rule and permission to invoke Lambda.
- Debugged Lambda runtime errors (filter schema, logging, result parsing) until the metric published successfully.
- Built CloudWatch Dashboard, Alarm, and SNS notifications.
- Updated README to reflect final implementation actions.

---

## Issues and Fixes

- **YAML parse error in workflow**
  - Symptom: “Implicit map keys need to be followed by map values” at the “Create Lambda if it doesn't exist” step.
  - Cause: Misindented `env:` block in `.github/workflows/lab6_continuous_monitoring.yml`.
  - Fix: Align `env:` under the step (same indentation level as `name:` and `run:`).

- **Lambda role cannot be assumed**
  - Symptom: `InvalidParameterValueException: The role defined for the function cannot be assumed by Lambda` on `create-function`.
  - Cause: The execution role trust policy only allowed GitHub OIDC; it did not allow the Lambda service principal.
  - Fix: Combined trust policy allowing both:
    ```json
    {"Effect":"Allow","Principal":{"Service":"lambda.amazonaws.com"},"Action":"sts:AssumeRole"}
    ```
    plus the existing GitHub OIDC federated principal.

- **First deploy race (Pending state)**
  - Symptom: `ResourceConflictException: The operation cannot be performed at this time... state 'Pending'` on `update-function-code`.
  - Cause: Attempting to update immediately after creating the function.
  - Fix: Make the workflow idempotent:
    - Detect whether the function existed; only run `update-function-code` if it did.
    - Use `--publish` on `create-function` and skip immediate update.

- **Invalid IAM action in inline policy**
  - Symptom: Console error: `Invalid Action: securityhub:BatchGetFindings`.
  - Cause: We needed `securityhub:GetInsightResults` (not BatchGetFindings).
  - Fix: Inline policy now includes:
    - `securityhub:CreateInsight`, `securityhub:UpdateInsight`, `securityhub:GetInsights`, `securityhub:GetInsightResults`, `cloudwatch:PutMetricData`.

- **EventBridge CLI usage mistakes**
  - Symptoms: Cron syntax typos; `$FUNCTION` unset; commands concatenated on one line.
  - Fix: Use valid cron `cron(0 */6 * * ? *)`, set variables first, then:
    - `aws events put-rule ...`
    - `aws events put-targets ...` with resolved `LAMBDA_ARN`
    - `aws lambda add-permission ...` (principal `events.amazonaws.com`).

- **No CloudWatch logs (Unhandled with no details)**
  - Symptom: Log group `/aws/lambda/continuous_control_monitor` did not exist.
  - Cause: Execution role missing `AWSLambdaBasicExecutionRole`.
  - Fix: Attached AWS managed policy `service-role/AWSLambdaBasicExecutionRole` to the role.

- **Security Hub filter schema incorrect**
  - Symptoms: `ParamValidationError` complaining about `TagKey`/`TagValue` and `RecordState` types; then `InvalidInputException` requiring `Comparison`.
  - Cause: Incorrect `Filters` structure for `CreateInsight`.
  - Fix in `continuous_control_monitor.py`:
    ```python
    TAG_FILTER = {"Key": TAG_KEY, "Value": TAG_VALUE, "Comparison": "EQUALS"}
    INSIGHT_FILTER = {
        "ResourceTags": [TAG_FILTER],
        "RecordState": [{"Value": "ACTIVE", "Comparison": "EQUALS"}],
    }
    ```

- **NameError: logger undefined**
  - Symptom: `NameError: name 'logger' is not defined`.
  - Cause: Variable name drift (`LOGGER` vs `logger`).
  - Fix: Standardized on `logger = logging.getLogger(__name__)` and used consistently.

- **Insight results parsing**
  - Symptom: `KeyError: 'TotalFindings'` and handled fallback metric of 0.
  - Cause: For custom insights grouped by `Type`, `get_insight_results` returns an array in `ResultValues`, not `TotalFindings`.
  - Fix in `_get_open_findings()` to sum counts:
    ```python
    values = resp.get("InsightResults", {}).get("ResultValues", [])
    total = sum(int(v.get("Count", 0)) for v in values)
    ```

- **Dashboard widget naming**
  - Symptom: Could not find “Single value” widget.
  - Cause: In the new UI it is called “Number”.
  - Fix: Use “Number” for single value and “Line” for trend; metric `Custom/SecurityHub -> OpenFindings`.

- **SNS email / Alarm visibility**
  - Symptom: No email received; alarm not visible.
  - Causes: Subscription pending/unconfirmed; viewing wrong region; alarm not wired to topic.
  - Fix: Subscribed in `us-east-1`, confirmed the email, recreated alarm `OpenFindingsGreaterThanZero` wired to topic `lab6-open-findings-alerts`.

---

## Final State

- Lambda `continuous_control_monitor` publishes `Custom/SecurityHub: OpenFindings`.
- Security Hub insight filter uses tag scope `Environment=Prod` and `RecordState=ACTIVE`.
- EventBridge rule `lab6_control_monitor_schedule` invokes every 6 hours.
- Dashboard created (Number + Line) and exported to `dashboards/continuous_monitor_dashboard.json`.
- Log retention 14 days for `/aws/lambda/continuous_control_monitor`.
- Alarm `OpenFindingsGreaterThanZero` wired to SNS topic `lab6-open-findings-alerts` (email `nelson.rosario89@gmail.com`).
- README corrected to use `securityhub:GetInsightResults`.

---

## Useful Commands

- Describe insight and results:
```bash
aws securityhub get-insights --region us-east-1 --query "Insights[?Name=='Prod-OpenFindings'].[Name,InsightArn]" --output table
aws securityhub get-insight-results --insight-arn <INSIGHT_ARN> --region us-east-1 --output json
```

- EventBridge wiring (reference):
```bash
RULE=lab6_control_monitor_schedule
FUNCTION=continuous_control_monitor
LAMBDA_ARN=$(aws lambda get-function --function-name "$FUNCTION" --query 'Configuration.FunctionArn' --output text --region us-east-1)
aws events put-rule --name "$RULE" --schedule-expression "cron(0 */6 * * ? *)" --state ENABLED --region us-east-1
aws events put-targets --rule "$RULE" --targets "Id"="1","Arn"="$LAMBDA_ARN" --region us-east-1
aws lambda add-permission --function-name "$FUNCTION" --statement-id eventbridge-invoke --action "lambda:InvokeFunction" --principal events.amazonaws.com --source-arn "$(aws events describe-rule --name "$RULE" --query 'Arn' --output text --region us-east-1)" --region us-east-1
```

- SNS + alarm (reference):
```bash
TOPIC_ARN=$(aws sns create-topic --name lab6-open-findings-alerts --region us-east-1 --query 'TopicArn' --output text)
aws sns subscribe --topic-arn "$TOPIC_ARN" --protocol email --notification-endpoint "nelson.rosario89@gmail.com" --region us-east-1
aws cloudwatch put-metric-alarm --alarm-name "OpenFindingsGreaterThanZero" --namespace "Custom/SecurityHub" --metric-name "OpenFindings" --statistic Maximum --period 300 --evaluation-periods 1 --threshold 0 --comparison-operator GreaterThanThreshold --treat-missing-data notBreaching --alarm-actions "$TOPIC_ARN" --region us-east-1
```

---

## Lessons Learned

- Indentation errors in workflow YAML can cause confusing parse failures.
- Lambda needs the correct trust principal; OIDC trust is separate from service trust.
- Make first-time deploys idempotent to avoid the `Pending` update race.
- Use the documented API shapes (Security Hub filters and results structure).
- Always check CloudWatch logs (`aws logs tail`) before guessing.
- UI labels change (e.g., “Number” instead of “Single value”).
