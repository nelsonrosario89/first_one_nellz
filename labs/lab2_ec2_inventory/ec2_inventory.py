"""EC2 Inventory & Categorization – Lab 2

This script collects a cross-region inventory of EC2 instances and uploads a
CSV evidence file to an S3 bucket.  It can be executed either as an AWS Lambda
function (`handler`) or locally via the CLI entry-point (`python ec2_inventory.py …`).

ISO 27001 mapping: A.8.1.1 – Asset inventory
"""

# Import the `annotations` feature from the `__future__` module to allow forward-reference type hints (PEP 563)
from __future__ import annotations  

# ── Standard Library ──────────────────────────────────────────────────────────
# Import the `argparse` module to parse command-line arguments when run locally
import argparse                     
# Import the `csv` module to write the inventory output into CSV format
import csv                          
# Import the `datetime` module to provide UTC timestamps for filenames / logs
import datetime as dt               
# Import the `json` module to emit structured JSON logs (CloudWatch & CI)
import json                         
# Import the `os` module to read environment variables (bucket, tag, …)
import os                           
# Import the `typing` module to provide static type hints for clarity
from typing import Dict, List       

# ── Third-Party ───────────────────────────────────────────────────────────────
# Import the `boto3` module, the official AWS SDK for Python (Boto3)
import boto3                        
# Import the `ClientError` exception from the `botocore.exceptions` module, the base exception for AWS service errors
from botocore.exceptions import ClientError  

# We could configure Python's `logging` module; for this lightweight Lambda we
# simply use `print(json.dumps(…))`.  Creating a CloudWatch Logs client anyway
# lets us replace `print` with a structured logger in the future if desired.
# Create a CloudWatch Logs client
logger = boto3.client("logs")

# Enumerate **all** public AWS regions that support EC2 once at import time.
# Get the list of available regions for the EC2 service
REGIONS = boto3.session.Session().get_available_regions("ec2")

# ───────────────────────────── Helper Functions ──────────────────────────────

# Define a function to return a *flat* list of instance dictionaries for a single region
def list_instances(region: str) -> List[Dict]:
    """Return a *flat* list of instance dictionaries for a single region."""
    # Create a regional EC2 client
    ec2 = boto3.client("ec2", region_name=region)             
    # Create a paginator for the `describe_instances` method to handle >1k instances
    paginator = ec2.get_paginator("describe_instances")        
    # Initialize an empty list to accumulate results
    instances: List[Dict] = []                                 
    # Iterate over pages of results
    for page in paginator.paginate():                          
        # Iterate over reservations in the page
        for reservation in page["Reservations"]:               
            # Append instances from the reservation to the list
            instances.extend(reservation["Instances"])         
    # Return the list of instances
    return instances

# Define a function to return True when the instance has the designated *in-scope* tag
def is_in_scope(tags: Dict[str, str], scope_key: str, scope_value: str) -> bool:
    """Return True when the instance has the designated *in-scope* tag."""
    # Perform a simple key/value check
    return tags.get(scope_key) == scope_value                 

# Define a function to convert AWS's nested instance JSON into a single-level dictionary
def flatten_instance(
    region: str,
    instance: Dict,
    scope_key: str,
    scope_value: str,
) -> Dict:
    """Convert AWS's nested instance JSON into a single-level dictionary."""

    # Convert `[{'Key': 'Name', 'Value': 'web'}]` → `{'Name': 'web'}` for easy lookup
    tags = {t["Key"]: t["Value"] for t in instance.get("Tags", [])}

    # Initialize a dictionary to store the flattened instance data
    record: Dict = {
        # Store the AWS region code
        "region": region,                                        
        # Store the instance ID
        "instance_id": instance["InstanceId"],                  
        # Store the human-readable name tag
        "name": tags.get("Name", ""),                          
        # Store the instance state
        "state": instance.get("State", {}).get("Name"),        
        # Store the associated VPC ID
        "vpc_id": instance.get("VpcId"),                        
        # Concatenate security-group IDs; auditors often care
        "security_groups": ",".join(sg["GroupId"] for sg in instance.get("SecurityGroups", [])),
        # Store a boolean flag for ISO 27001 scoping
        "in_scope": is_in_scope(tags, scope_key, scope_value),
    }

    # Add one CSV column per *any* tag so auditors have full context
    for key, value in tags.items():
        record[f"tag_{key}"] = value

    # Return the flattened instance data
    return record

# Define a function to loop over every region, building a master inventory list
def gather_inventory(scope_tag: str) -> List[Dict]:
    """Loop over every region, building a master inventory list."""

    # Split "Scope=In" into key/value parts
    scope_key, scope_value = scope_tag.split("=", 1)
    # Initialize an empty list to store the inventory
    inventory: List[Dict] = []

    # Iterate over regions
    for region in REGIONS:                                     
        try:
            # Iterate over raw EC2 instances in the region
            for inst in list_instances(region):                 
                # Append the flattened instance data to the inventory
                inventory.append(
                    flatten_instance(region, inst, scope_key, scope_value)
                )
        except ClientError as err:                              
            # Handle AWS service errors
            print(f"{region}: {err.response['Error']['Code']} – skipping region")

    # Return the master inventory list
    return inventory

# Define a function to write the inventory list to a CSV file in /tmp (Lambda-writable)
def write_csv(records: List[Dict], tmp_path: str) -> None:
    """Write the inventory list to a CSV file in /tmp (Lambda-writable)."""
    # If no instances were found we still want an evidence artefact.  We’ll create
    # an empty CSV that only contains headers so auditors see explicit proof that
    # the query ran and the account had zero EC2 resources at this point in time.
    if not records:
        fieldnames = [
            "region",
            "instance_id",
            "name",
            "state",
            "vpc_id",
            "security_groups",
            "in_scope",
        ]
    else:
        # Gather a union of all keys to use as CSV columns (tags differ per instance)
        fieldnames = sorted({key for r in records for key in r})

    # Open the CSV file for writing
    with open(tmp_path, "w", newline="") as fp:
        # Create a `DictWriter` to write the inventory data to the CSV file
        writer = csv.DictWriter(fp, fieldnames=fieldnames)      
        # Write the column names row
        writer.writeheader()                                    
        # Write the inventory data rows
        writer.writerows(records)                               

# Define a function to upload the generated CSV evidence file to the designated S3 bucket
def upload_to_s3(bucket: str, key: str, local_path: str) -> None:
    """Upload the generated CSV evidence file to the designated S3 bucket."""
    # Create an S3 client
    s3 = boto3.client("s3")
    # Upload the CSV file to S3
    s3.upload_file(local_path, bucket, key)                     

# ─────────────────────────── Lambda Entrypoint ───────────────────────────────

# Define the AWS Lambda entry-point called by the scheduler / CI pipeline
def handler(event=None, context=None):
    """AWS Lambda entry-point called by the scheduler / CI pipeline."""
    # Get the destination S3 bucket for evidence from the environment variable
    bucket    = os.environ["EVIDENCE_BUCKET"]                    
    # Get the in-scope tag from the environment variable (default: "Scope=In")
    scope_tag = os.environ.get("SCOPE_TAG", "Scope=In")         
    # Get the current UTC timestamp
    timestamp = dt.datetime.utcnow().isoformat() + "Z"          

    # 1️⃣ Gather the data
    records = gather_inventory(scope_tag)

    # 2️⃣ Write to local disk (Lambda limits us to /tmp)
    tmp_file = f"/tmp/ec2-inventory-{timestamp}.csv"
    write_csv(records, tmp_file)

    # 3️⃣ Upload to S3 for permanent evidence storage
    key = f"ec2-inventory/{timestamp}.csv"
    upload_to_s3(bucket, key, tmp_file)

    # 4️⃣ Log a JSON summary for quick evidence review in CloudWatch & CI logs
    summary = {
        "instances_total": len(records),
        "instances_in_scope": sum(r["in_scope"] for r in records),
    }
    print(json.dumps({"status": "complete", **summary}))
    return {"status": "complete", **summary}

# ─────────────────────────── CLI Entrypoint ──────────────────────────────────

# Define the CLI entry-point to allow local execution via `python ec2_inventory.py --bucket …`
def cli() -> None:
    """Allow local execution via `python ec2_inventory.py --bucket …`."""
    # Create an argument parser
    parser = argparse.ArgumentParser(description="EC2 inventory & categorization")
    # Add a required argument for the S3 bucket
    parser.add_argument("--bucket", required=True, help="S3 bucket for evidence upload")
    # Add an optional argument for the in-scope tag (default: "Scope=In")
    parser.add_argument(
        "--scope-tag",
        default="Scope=In",
        help="Tag key=value identifying in-scope instances",
    )
    # Parse the command-line arguments
    args = parser.parse_args()

    # Re-use the Lambda logic by injecting env-vars then calling handler()
    os.environ["EVIDENCE_BUCKET"] = args.bucket
    os.environ["SCOPE_TAG"]      = args.scope_tag
    handler()

# Run `cli()` when executed as a standalone script
if __name__ == "__main__":
    cli()
