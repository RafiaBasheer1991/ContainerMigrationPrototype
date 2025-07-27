import requests
import os
import time

LOCAL_URL = "http://localhost:5000/metrics"
EC2_INSTANCE_ID = "i-026ed76dc34e1c04d"  # Replace with your EC2 instance ID
AWS_REGION = "us-east-1"  # Replace with your region

def should_migrate():
    try:
        print("[Monitor] Checking request rate...")
        response = requests.get(LOCAL_URL, timeout=5)  # prevent freezing if server is unreachable
        rpm = response.json()["rpm"]
        print(f"[Monitor] Requests per minute: {rpm}")
        return rpm > 100
    except Exception as e:
        print(f"[Error] Failed to fetch metrics: {e}")
        return False

def start_ec2_instance():
    print("[Action] Starting EC2 instance...")
    cmd = "aws ec2 start-instances --instance-ids i-026ed76dc34e1c04d --region us-east-1"




    os.system(cmd)

# Monitor loop
if __name__ == "__main__":
    print("[System] Monitoring started...")
    while True:
        if should_migrate():
            start_ec2_instance()
            print("[System] Migration triggered. Exiting monitor.")
            break
        time.sleep(10)  # Wait 10 seconds before next check
