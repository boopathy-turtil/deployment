#!/bin/bash
# Install Docker
sudo apt-get update -y
sudo apt-get install -y docker.io
sudo systemctl start docker
sudo usermod -aG docker ubuntu  # Ubuntu uses "ubuntu" user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Login to ECR and pull latest image
ECR_URI="033464272864.dkr.ecr.ap-south-1.amazonaws.com"  # e.g., 123456789.dkr.ecr.us-east-1.amazonaws.com
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin $ECR_URI
docker pull $ECR_URI/dev-fast-api-repo:latest

# Generate docker-compose.yml
cat <<EOT > /home/ubuntu/docker-compose.yml
services:
  web:
    image: $ECR_URI/dev-fast-api-repo:latest
    ports:
      - "8000:8000"
    environment:
      - PYTHONUNBUFFERED=1
    command: ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
    restart: always
EOT

# Start the app
docker-compose -f /home/ubuntu/docker-compose.yml up -d