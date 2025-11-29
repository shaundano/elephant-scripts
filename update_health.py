import sys
import os
import time

print("--- STARTING WARM-UP SEQUENCE ---")

# ==============================================================================
# PART 1: WARM UP HEAVY LIBRARIES
# We import strictly what is used in recorder.py to force disk-to-RAM loading.
# ==============================================================================
print("... Loading Heavy Libraries ...")

try:
    # Standard Imports (Fast, but good to prime)
    import contextlib
    import pathlib
    import queue
    import typing
    
    # Third-Party Imports (The actual slow part)
    # These are explicitly listed in your recorder.py
    import typer
    import loguru
    import tqdm
    import mediaref
    import typing_extensions
    
    # OWA Specifics (Critical for loading GStreamer plugins dynamically)
    import mcap_owa
    import mcap_owa.highlevel
    import owa.core
    import owa.core.time
    
    # We do NOT import cv2, numpy, or pyaudio because 
    # they are not explicitly in recorder.py.
    
    print("... Libraries Loaded Successfully.")

except ImportError as e:
    # We catch errors so the script continues to the Health Check
    print(f"WARNING: Warm-up import mismatch: {e}")
    print("Continuing to Health Check...")


# ==============================================================================
# PART 2: DYNAMODB HEALTH CHECK
# ==============================================================================
import boto3
import requests

# --- CONFIG ---
TABLE_NAME = "elephant-meetings"
REGION = "us-west-2"
METADATA_PATH = r"C:\scripts\meeting\metadata.env"

def get_instance_id():
    try:
        token = requests.put("http://169.254.169.254/latest/api/token", 
                           headers={"X-aws-ec2-metadata-token-ttl-seconds": "21600"}, timeout=2).text
        return requests.get("http://169.254.169.254/latest/meta-data/instance-id", 
                          headers={"X-aws-ec2-metadata-token": token}, timeout=2).text
    except:
        return "UNKNOWN_HOST"

def get_session_id():
    if not os.path.exists(METADATA_PATH): return None
    with open(METADATA_PATH, 'r') as f:
        for line in f:
            if line.startswith("SESSION_ID="):
                return line.strip().split("=")[1]
    return None

if __name__ == "__main__":
    session_id = get_session_id()
    instance_id = get_instance_id()
    
    if session_id:
        print(f"Flagging Session {session_id} as HEALTHY on host {instance_id}...")
        try:
            dynamodb = boto3.client('dynamodb', region_name=REGION)
            dynamodb.update_item(
                TableName=TABLE_NAME,
                Key={'id': {'S': session_id}},
                UpdateExpression="SET #s = :status, instance_id = :inst",
                ExpressionAttributeNames={'#s': 'status'},
                ExpressionAttributeValues={':status': {'S': 'HEALTHY'}, ':inst': {'S': instance_id}}
            )
            print("DynamoDB update successful.")
        except Exception as e:
            print(f"Error updating DynamoDB: {e}")
    else:
        print("Warning: No Session ID found.")