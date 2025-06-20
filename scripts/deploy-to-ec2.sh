#!/bin/bash

set -e

# Variables
EC2_USER="ubuntu"
EC2_PUBLIC_IP=$EC2_PUBLIC_IP
APP_DIR="/home/$EC2_USER/app"
APP_FILE="main.py"
REQUIREMENTS_FILE="requirements.txt"
VENV_DIR="$APP_DIR/venv"

# Validate local files
echo "Checking for $APP_FILE in local repository..."
if [ ! -f "$APP_FILE" ]; then
  echo "Error: $APP_FILE not found in repository root"
  exit 1
fi

# Test SSH connectivity
echo "Testing SSH connectivity to $EC2_PUBLIC_IP..."
if ! ssh -o StrictHostKeyChecking=no -i ~/.ssh/id_rsa $EC2_USER@$EC2_PUBLIC_IP "echo 'SSH connection successful'" 2>/dev/null; then
  echo "Error: SSH connection to $EC2_PUBLIC_IP failed"
  exit 1
fi

# Copy application to EC2
echo "Creating $APP_DIR on EC2 instance..."
ssh -o StrictHostKeyChecking=no -i ~/.ssh/id_rsa $EC2_USER@$EC2_PUBLIC_IP "mkdir -p $APP_DIR && chmod 755 $APP_DIR && chown $EC2_USER:$EC2_USER $APP_DIR" || {
  echo "Error: Failed to create or set permissions for $APP_DIR on EC2"
  exit 1
}

echo "Copying $APP_FILE to $EC2_PUBLIC_IP:$APP_DIR/..."
scp -o StrictHostKeyChecking=no -i ~/.ssh/id_rsa $APP_FILE $EC2_USER@$EC2_PUBLIC_IP:$APP_DIR/$APP_FILE || {
  echo "Error: Failed to copy $APP_FILE to EC2"
  exit 1
}
ssh -o StrictHostKeyChecking=no -i ~/.ssh/id_rsa $EC2_USER@$EC2_PUBLIC_IP "chmod 644 $APP_DIR/$APP_FILE && chown $EC2_USER:$EC2_USER $APP_DIR/$APP_FILE"

# Copy requirements.txt if it exists
if [ -f "$REQUIREMENTS_FILE" ]; then
  echo "Copying $REQUIREMENTS_FILE to $EC2_PUBLIC_IP:$APP_DIR/..."
  scp -o StrictHostKeyChecking=no -i ~/.ssh/id_rsa $REQUIREMENTS_FILE $EC2_USER@$EC2_PUBLIC_IP:$APP_DIR/$REQUIREMENTS_FILE || {
    echo "Error: Failed to copy $REQUIREMENTS_FILE to EC2"
    exit 1
  }
  ssh -o StrictHostKeyChecking=no -i ~/.ssh/id_rsa $EC2_USER@$EC2_PUBLIC_IP "chmod 644 $APP_DIR/$REQUIREMENTS_FILE && chown $EC2_USER:$EC2_USER $APP_DIR/$REQUIREMENTS_FILE"
fi

# Set up EC2 instance and restart application
echo "Setting up EC2 instance and restarting application..."
ssh -o StrictHostKeyChecking=no -i ~/.ssh/id_rsa $EC2_USER@$EC2_PUBLIC_IP << EOF
  set -e
  set -x

  # Export variables
  export APP_DIR="$APP_DIR"
  export EC2_USER="$EC2_USER"
  export VENV_DIR="$VENV_DIR"

  # Debug: Log environment
  echo "APP_DIR is set to: \$APP_DIR"
  echo "EC2_USER is set to: \$EC2_USER"
  echo "VENV_DIR is set to: \$VENV_DIR"
  echo "Current user: \$(whoami)"
  echo "Python version:"
  python3 --version || echo "Python3 not installed"
  echo "Pip version:"
  pip3 --version || echo "Pip3 not installed"

  # Debug: List files in APP_DIR
  echo "Listing files in \$APP_DIR..."
  ls -la \$APP_DIR || {
    echo "Error: Failed to list \$APP_DIR"
    exit 1
  }

  # Debug: Check directory and file permissions
  echo "Checking permissions of \$APP_DIR..."
  ls -ld \$APP_DIR
  echo "Checking permissions of \$APP_DIR/main.py..."
  ls -l \$APP_DIR/main.py || echo "main.py not found"

  # Verify main.py exists on EC2
  echo "Checking for \$APP_DIR/main.py on EC2..."
  if [ ! -f "\$APP_DIR/main.py" ]; then
    echo "Error: \$APP_DIR/main.py not found on EC2"
    exit 1
  fi

  # Install Python3, pip, and venv
  echo "Installing python3, pip, and venv..."
  sudo apt update -y || {
    echo "Error: Failed to update apt package index"
    exit 1
  }
  sudo apt install -y python3 python3-pip python3-venv python3-full || {
    echo "Error: Failed to install python3 packages"
    exit 1
  }

  # Verify python3-venv installation
  echo "Verifying python3-venv installation..."
  dpkg -l | grep python3-venv || {
    echo "Error: python3-venv not installed"
    exit 1
  }

  # Install nodejs and pm2 if not present
  if ! command -v pm2 >/dev/null 2>&1; then
    echo "Installing nodejs, npm, and pm2..."
    sudo apt update -y || {
      echo "Error: Failed to update apt package index"
      exit 1
    }
    sudo apt install -y nodejs npm || {
      echo "Error: Failed to install nodejs and npm"
      exit 1
    }
    sudo npm install -g pm2 || {
      echo "Error: Failed to install pm2"
      exit 1
    }
  fi

  # Uninstall pm2 from pip if installed via pip
  if pip3 show pm2 >/dev/null 2>&1; then
    echo "Uninstalling pip-installed pm2..."
    pip3 uninstall -y pm2
  fi

  # Create and activate virtual environment
  echo "Creating virtual environment in \$VENV_DIR..."
  python3 -m venv \$VENV_DIR || {
    echo "Error: Failed to create virtual environment"
    python3 -m ensurepip --version || echo "ensurepip not available"
    exit 1
  }
  source \$VENV_DIR/bin/activate

  # Verify virtual environment
  echo "Verifying virtual environment..."
  which python || {
    echo "Error: Python not found in virtual environment"
    exit 1
  }
  which pip || {
    echo "Error: Pip not found in virtual environment"
    exit 1
  }

  # Install requirements if requirements.txt exists
  if [ -f "\$APP_DIR/requirements.txt" ]; then
    echo "Listing contents of \$APP_DIR/requirements.txt..."
    cat \$APP_DIR/requirements.txt
    echo "Installing dependencies from \$APP_DIR/requirements.txt..."
    pip install -r \$APP_DIR/requirements.txt || {
      echo "Error: Failed to install dependencies"
      exit 1
    }
  else
    echo "Warning: \$APP_DIR/requirements.txt not found, skipping dependency installation"
  fi

  # Configure pm2 to run on boot
  echo "Configuring pm2 to run on boot..."
  export PM2_HOME=/home/\$EC2_USER/.pm2
  sudo -E env PATH=\$PATH:/usr/bin:/usr/local/bin pm2 startup systemd -u \$EC2_USER --hp /home/\$EC2_USER || {
    echo "Error: Failed to configure pm2 startup"
    echo "Attempting manual pm2 startup setup..."
    sudo systemctl stop pm2-\$EC2_USER || true
    sudo systemctl disable pm2-\$EC2_USER || true
    sudo rm -f /etc/systemd/system/pm2-\$EC2_USER.service
    sudo -E env PATH=\$PATH:/usr/bin:/usr/local/bin pm2 startup systemd -u \$EC2_USER --hp /home/\$EC2_USER || {
      echo "Error: Manual pm2 startup setup failed"
      exit 1
    }
  }

  # Debug: Verify pm2 startup service
  echo "Checking pm2 startup service..."
  sudo systemctl status pm2-\$EC2_USER || {
    echo "Warning: pm2 startup service not running"
  }

  # Stop and delete any existing PM2 process
  echo "Stopping and deleting existing PM2 process (if any)..."
  pm2 delete app || true

  # Start the application with PM2 using virtual environment's Python
  echo "Starting \$APP_DIR/main.py with PM2..."
  pm2 start \$APP_DIR/main.py --name app --interpreter \$VENV_DIR/bin/python || {
    echo "Error: Failed to start \$APP_DIR/main.py with PM2"
    exit 1
  }

  # Save PM2 process list
  echo "Saving PM2 process list..."
  pm2 save || {
    echo "Error: Failed to save PM2 process list"
    exit 1
  }

  # Debug: Check PM2 status
  echo "Checking PM2 status..."
  pm2 list

  # Debug: Verify the application is running
  echo "Checking if Flask server is running..."
  sleep 2
  curl -s http://localhost:5000 || {
    echo "Warning: Failed to reach Flask server at http://localhost:5000"
  }

  # Deactivate virtual environment
  deactivate
EOF

echo "Deployment completed successfully!"