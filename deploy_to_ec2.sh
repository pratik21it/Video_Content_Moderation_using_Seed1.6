#!/bin/bash

# Deployment script for Video Content Moderation App on EC2
# Run this script on your EC2 instance after connecting via SSH

echo "Starting deployment of Video Content Moderation App..."

# Update system packages
echo "Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Install required system dependencies
echo "Installing system dependencies..."
sudo apt install python3-pip python3-dev git tmux -y

# Clone the repository
echo "Cloning the repository..."
git clone https://github.com/pratik21it/Video_Content_Moderation_using_Seed1.6.git
cd Video_Content_Moderation_using_Seed1.6

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

# Create systemd service file
echo "Setting up systemd service..."
cat > streamlit.service << EOL
[Unit]
Description=Streamlit Content Moderation App
After=network.target

[Service]
User=\$(whoami)
WorkingDirectory=\$(pwd)
ExecStart=\$(which streamlit) run app.py --server.port=8501 --server.address=0.0.0.0
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOL

# Move service file to systemd directory
echo "Installing systemd service..."
sudo mv streamlit.service /etc/systemd/system/

# Enable and start the service
echo "Starting the service..."
sudo systemctl daemon-reload
sudo systemctl enable streamlit
sudo systemctl start streamlit

# Check service status
echo "Service status:"
sudo systemctl status streamlit

# Get public IP address
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)

echo ""
echo "Deployment completed!"
echo "You can access your app at: http://$PUBLIC_IP:8501"
echo ""
echo "To check logs: sudo journalctl -u streamlit"
echo "To restart the service: sudo systemctl restart streamlit"