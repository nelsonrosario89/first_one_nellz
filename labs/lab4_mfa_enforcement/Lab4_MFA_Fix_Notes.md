# Lab 4 – MFA Enforcement Fix Log (26 Aug 2025)

## Context
Our Lab 4 workflow (`mfa_check.py` + GitHub Action) imports a Security Hub finding for **every IAM user** to show whether MFA is enabled.  
Only an old *Test MFA finding* ever appeared because Security Hub silently rejected the real findings.

## Problems Encountered
* **Invalid `Types` value** – We were sending:
  `Software and Configuration Checks/Industry and Regulatory Standards/ISO 27001/A.9.2.3`  
  This has **4 slash segments**; Amazon Finding Format allows **≤ 3**.
* **Stale dummy ARN** – The manual test finding still pointed at `user/does-not-exist`, masking the real bug.
* **Console confusion** – Custom findings don’t appear in CSPM by default; the *standard* Findings page must be used.

## Troubleshooting Steps & Work-arounds
1. Verified workflow logs – saw only `users=1` with no SH errors.
2. Queried Security Hub via CLI → confirmed zero real findings.
3. Reproduced with `batch-import-findings` CLI; captured `InvalidInput` error telling us the `Types` pattern was wrong.
4. **Patched `mfa_check.py`**
   * Replaced both `Types` arrays with valid value `Software and Configuration Checks/MFA`.
5. Re-imported test JSON → `SuccessCount = 1`.
6. Re-ran GitHub Action – the finding for `iamadmin` appeared with *Informational / PASSED*.

## Remaining Clean-up
* [x] Archive the old *Test MFA finding* in Security Hub.
* [x] Remove the temporary **Show role secret length** step from workflow YAML.
* [x] (Optional) add unit test that validates generated finding schema with regex.

## 27 Aug 2025 – AWS Config Recorder & Security Hub Config.1 Fix
1. Enabled customer-managed recorder in **us-east-1** – console now shows *Recording is on*.
2. Set delivery channel to S3 bucket `my-audit-evidence-bucket` with prefix `aws-config/`.
3. Verified via CLI:
   * `recording=true`, lastStatus **SUCCESS**.
   * Delivery channel status **SUCCESS**.
4. Confirmed first configuration file uploaded:
   `aws-config/AWSLogs/097089567108/Config/us-east-1/2025/8/27/ConfigHistory/…json.gz` (1 KiB).
5. No Config rule needed; Security Hub control **Config.1** will flip to PASSED on next evaluation cycle (~24 h).
6. Added **pytest** unit test `tests/test_mfa_finding_schema.py` to validate ASFF schema (checks `Types` format and required keys).
7. Updated `mfa_check.py` and the new test to use timezone-aware `datetime.now(datetime.timezone.utc)` to silence deprecation warnings.
8. Committed and pushed changes with message `"Lab4: add ASFF schema unit test and switch to timezone-aware datetime"`.

