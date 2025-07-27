# ContainerMigrationPrototype

This repository contains a prototype for a cloud computing project that demonstrates the automated migration of a Dockerized Flask application from a local server to an AWS EC2 instance when the request load exceeds a predefined threshold. The system monitors requests per minute (RPM) and triggers migration to the cloud to handle high workloads, showcasing key cloud computing concepts such as scalability, containerization, and automation.

This project was developed as part of a Master's-level Cloud Computing course to illustrate the integration of local and cloud-based infrastructure using Docker, AWS EC2, and Amazon Elastic Container Registry (ECR).

## Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
  - [Local Environment Setup](#local-environment-setup)
  - [AWS EC2 Setup](#aws-ec2-setup)
  - [Docker Image and Amazon ECR](#docker-image-and-amazon-ecr)
  - [Monitoring and Migration Script](#monitoring-and-migration-script)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)
- [Architecture](#architecture)
- [Future Improvements](#future-improvements)
- [Authors](#authors)
- [License](#license)

## Project Overview
This prototype simulates a workload migration scenario where a Flask application runs locally in a Docker container. A monitoring script checks the application's request rate (RPM) via a `/metrics` endpoint. If the RPM exceeds 100, the script triggers the start of an AWS EC2 instance, and traffic is rerouted to the EC2 instance running the same Dockerized Flask application. The Docker image is stored in Amazon ECR for seamless deployment to the cloud.

The project demonstrates:
- **Containerization**: Using Docker to package and deploy the Flask application.
- **Cloud Automation**: Starting an EC2 instance programmatically based on load.
- **Scalability**: Migrating workloads to the cloud to handle increased traffic.
- **Monitoring**: Real-time tracking of application metrics to trigger migration.

Result:
- Runs a Dockerized Flask app locally
- Measures request rate
- When load spikes:
  - Triggers EC2 instance to start
  - Pulls container from ECR
  - Reroutes or transfers workload to cloud container
- Demonstrates actual workload migration, not just data offloading

## Features
- Local Flask application running in a Docker container, exposing a `/compute` endpoint for processing requests and a `/metrics` endpoint for monitoring RPM.
- Automated monitoring script (`monitor_and_migrate.py`) that checks RPM and starts an EC2 instance when the load exceeds 100 RPM.
- Docker image management using Amazon ECR for storing and pulling the application image to EC2.
- Traffic rerouting from the local server to the EC2 instance after migration.
- Comprehensive troubleshooting steps to ensure smooth operation.

## Prerequisites
Before setting up the project, ensure the following are installed and configured:
- **Local Machine**:
  - Docker (for building and running the Flask app)
  - Python 3 (for running the monitoring script)
  - AWS CLI (configured with credentials having `AmazonEC2ContainerRegistryFullAccess` and `ec2:StartInstances` permissions)
  - `requests` Python library (`pip install requests`)
- **AWS Account**:
  - Access to AWS Management Console
  - IAM user or role with permissions for EC2 and ECR
  - Key pair for SSH access to EC2 instances
- **EC2 Instance**:
  - Amazon Linux 2 or Ubuntu Server (free tier eligible, e.g., `t2.micro` or `t3.micro`)
  - Security group allowing inbound TCP port 5000 for Flask API
- **Optional**:
  - Docker Hub account (for alternative image storage, if not using ECR)

## Setup Instructions

### Local Environment Setup
1. **Build and Run the Flask Application Locally**:
   - In a terminal, navigate to the project directory and build the Docker image:
     ```bash
     docker build -t local-workload-app .
     ```
   - Run the Docker container, mapping port 5000:
     ```bash
     docker run -p 5000:5000 local-workload-app
     ```
   - Test the `/compute` endpoint locally:
     ```bash
     curl -X POST http://localhost:5000/compute -H "Content-Type: application/json" -d '{"number": 3}'
     ```

2. **Simulate Traffic**:
   - In a second terminal, simulate load to increase RPM:
     ```bash
     for i in {1..120}; do
       curl -X POST http://localhost:5000/compute -H "Content-Type: application/json" -d '{"number": 5}'
       sleep 0.5
     done
     ```

### AWS EC2 Setup
1. **Launch an EC2 Instance**:
   - Log in to the AWS Management Console.
   - Navigate to EC2 > Launch Instance.
   - Select Amazon Linux 2 or Ubuntu Server (free tier eligible).
   - Choose `t2.micro` or `t3.micro`.
   - Configure a security group to allow inbound TCP port 5000.
   - Download the key pair for SSH access.
   - Launch the instance and note its public IP and instance ID.

2. **SSH into the EC2 Instance**:
   ```bash
   ssh -i /path/to/key.pem ec2-user@<EC2_PUBLIC_IP>
   ```

3. **Install Docker on EC2**:
   ```bash
   sudo yum update -y
   sudo amazon-linux-extras install docker
   sudo service docker start
   sudo usermod -a -G docker ec2-user
   ```
   - Log out and SSH again to apply Docker permissions.

### Docker Image and Amazon ECR
1. **Create an ECR Repository**:
   ```bash
   aws ecr create-repository --repository-name sky-app --region us-east-1
   ```
   - Note the repository URI (e.g., `058524301863.dkr.ecr.us-east-1.amazonaws.com/sky-app`).

2. **Authenticate Docker to ECR (Local Machine)**:
   ```bash
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 058524301863.dkr.ecr.us-east-1.amazonaws.com
   ```

3. **Tag and Push Docker Image to ECR**:
   ```bash
   docker tag local-workload-app:latest 058524301863.dkr.ecr.us-east-1.amazonaws.com/sky-app:latest
   docker push 058524301863.dkr.ecr.us-east-1.amazonaws.com/sky-app:latest
   ```

4. **Authenticate Docker to ECR on EC2**:
   - Configure AWS CLI on the EC2 instance:
     ```bash
     aws configure
     ```
     - Enter Access Key, Secret Key, region (`us-east-1`), and output format (`json`).
   - Authenticate Docker:
     ```bash
     aws ecr get-login-password --region us-east-1 | sudo docker login --username AWS --password-stdin 058524301863.dkr.ecr.us-east-1.amazonaws.com
     ```

5. **Pull and Run the Docker Image on EC2**:
   ```bash
   sudo docker pull 058524301863.dkr.ecr.us-east-1.amazonaws.com/sky-app:latest
   sudo docker run -d -p 5000:5000 058524301863.dkr.ecr.us-east-1.amazonaws.com/sky-app:latest
   ```
   - Verify the container is running:
     ```bash
     docker ps
     ```

### Monitoring and Migration Script
1. **Install Python Requirements**:
   ```bash
   pip install requests
   ```

2. **Configure the Monitoring Script**:
   - Edit `monitor_and_migrate.py` to include your EC2 instance ID and AWS region:
     ```python
     EC2_INSTANCE_ID = "i-xxxxxxxxxxxx"  # Replace with your EC2 instance ID
     AWS_REGION = "us-east-1"           # Replace with your AWS region
     ```

3. **Run the Monitoring Script**:
   ```bash
   python monitor_and_migrate.py
   ```
   - The script checks the `/metrics` endpoint every 10 seconds. If RPM > 100, it starts the EC2 instance:
     ```
     Requests per minute: 102 → Starting EC2 instance…
     ```

4. **Test the Metrics Endpoint**:
   ```bash
   curl http://localhost:5000/metrics
   ```
   - Expected output:
     ```json
     {"rpm": 120}
     ```

## Usage
1. Start the local Flask application and simulate traffic as described in [Local Environment Setup](#local-environment-setup).
2. Run the monitoring script to detect high load and trigger EC2 instance startup.
3. Once the EC2 instance is running, verify the container is active:
   ```bash
   docker ps
   ```
4. Reroute traffic to the EC2 instance:
   ```bash
   curl -X POST http://<EC2_PUBLIC_IP>:5000/compute -H "Content-Type: application/json" -d '{"number": 7}'
   ```
   - Example with provided IP:
     ```bash
     curl -X POST http://54.167.106.10:5000/compute -H "Content-Type: application/json" -d '{"number": 7}'
     ```
5. Confirm the results are returned from the cloud instance.

## Troubleshooting
If the migration does not occur as expected, follow these steps:
1. **Verify Monitoring Script**:
   - Ensure `monitor_and_migrate.py` is running and printing RPM logs:
     ```
     [Monitor] Requests per minute: XX
     ```
   - If silent, check for errors in the script or Python environment.

2. **Check Metrics Endpoint**:
   - Test the `/metrics` endpoint:
     ```bash
     curl http://localhost:5000/metrics
     ```
   - Ensure it returns valid JSON (e.g., `{"rpm": 45}`).
   - If it fails, verify the Flask app is running and updating metrics.

3. **Ensure Sufficient Load**:
   - The migration triggers only if RPM > 100. Simulate higher load:
     ```bash
     for i in {1..150}; do curl -s -X POST http://localhost:5000/compute -H "Content-Type: application/json" -d '{"number": 5}' & done
     ```

4. **Fix EC2 Start Command**:
   - Ensure `EC2_INSTANCE_ID` and `AWS_REGION` are correctly set as strings in `monitor_and_migrate.py`.
   - Correct example:
     ```python
     os.system(f"aws ec2 start-instances --instance-ids {EC2_INSTANCE_ID} --region {AWS_REGION}")
     ```

5. **Verify AWS CLI Configuration**:
   - Run `aws configure` on the machine running the script to ensure valid credentials with `ec2:StartInstances` permissions.

6. **Add Debugging Logs**:
   - Modify `start_ec2_instance` to include success/failure logs:
     ```python
     def start_ec2_instance():
         print("[Action] Starting EC2 instance...")
         ret = os.system(f"aws ec2 start-instances --instance-ids {EC2_INSTANCE_ID} --region {AWS_REGION}")
         if ret == 0:
             print("[Success] EC2 instance start command issued.")
         else:
             print("[Error] Failed to start EC2 instance.")
     ```

7. **ECR Authentication Issues**:
   - If the Docker image pull fails on EC2, re-authenticate:
     ```bash
     aws ecr get-login-password --region us-east-1 | sudo docker login --username AWS --password-stdin 058524301863.dkr.ecr.us-east-1.amazonaws.com
     ```

## Architecture
The system architecture consists of:
- **Local Server**: Runs a Dockerized Flask app exposing `/compute` and `/metrics` endpoints.
- **Monitoring Script**: Python script (`monitor_and_migrate.py`) that polls the `/metrics` endpoint and triggers EC2 startup via AWS CLI.
- **AWS EC2**: Hosts the same Dockerized Flask app, pulled from Amazon ECR, to handle migrated traffic.
- **Amazon ECR**: Stores the Docker image for consistent deployment across local and cloud environments.
- **Traffic Rerouting**: Manual or automated rerouting (e.g., via NGINX) directs requests to the EC2 instance after migration.

## Future Improvements
- **Automated Traffic Rerouting**: Implement a load balancer (e.g., AWS Application Load Balancer) to seamlessly redirect traffic to EC2.
- **Dynamic Scaling**: Use AWS Auto Scaling to launch multiple EC2 instances based on load.
- **Enhanced Monitoring**: Integrate Amazon CloudWatch for real-time metrics and alerts.
- **Improved Security**: Use AWS Secrets Manager for handling credentials and implement VPC security groups for tighter access control.
- **Cost Optimization**: Automatically terminate EC2 instances when load decreases.

## Authors
This project was developed by Rafia basheer, Fauzia Ehsan, Muneeb Ahmed, Tauqeer Ahmed Shaikh, Suhaib Khalid. Contributions and feedback are welcome!

## License
This project is licensed under the MIT License. 
---

