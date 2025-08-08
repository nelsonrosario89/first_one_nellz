"""
Lambda: Validate every AWS region has at least one multi-region CloudTrail.

- Writes a JSON result to S3  (one object per run)
- Emits a structured CloudWatch log for quick evidence review
"""

import boto3, json, os, datetime, logging
from botocore.exceptions import ClientError
logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3          = boto3.client("s3")
ct_regions  = boto3.session.Session().get_available_regions("cloudtrail")
result      = {"timestamp": datetime.datetime.utcnow().isoformat() + "Z",
               "region_results": {}}

def handler(event, context):
    ok_regions, bad_regions = 0, 0

    for region in ct_regions:
        ct = boto3.client("cloudtrail", region_name=region)
        try:
            trails = ct.describe_trails(includeShadowTrails=False)["trailList"]
        except ClientError as e:
            # Some partitions (e.g., gov, iso) will raise UnrecognizedClientException
            logger.warning(f"{region}: {e.response['Error']['Code']} – skipping region")
            result["region_results"][region] = {
                "has_multi_region_trail": False,
                "error": e.response["Error"]["Code"]
            }
            bad_regions += 1
            continue
        active = [t for t in trails if t.get("IsMultiRegionTrail")]
        has_trail = len(active) > 0

        result["region_results"][region] = {
            "has_multi_region_trail": has_trail,
            "trails": [t["Name"] for t in active]
        }
        if has_trail:
            ok_regions += 1
        else:
            bad_regions += 1

    result["summary"] = {
        "regions_with_trail": ok_regions,
        "regions_missing":   bad_regions
    }

    # ---- Save evidence ----
    bucket = os.environ["EVIDENCE_BUCKET"]
    key    = f"cloudtrail-validation/{result['timestamp']}.json"
    s3.put_object(Body=json.dumps(result, indent=2).encode(),
                  Bucket=bucket, Key=key)
    logger.info(json.dumps(result))
    return {"status": "complete", **result["summary"]}