# AWS Deployment Guide for Video Content Moderation App

This guide will walk you through deploying the Video Content Moderation App on an AWS EC2 instance using the Free Tier.

## Prerequisites

- AWS account (Free Tier eligible)
- Basic knowledge of AWS services
- SSH client (Terminal on macOS/Linux or PuTTY on Windows)

## Step 1: Create an EC2 Instance

1. Log in to your AWS Management Console
2. Navigate to EC2 Dashboard
3. Click "Launch Instance"
4. Choose an Amazon Machine Image (AMI)
   - Select "Ubuntu Server 22.04 LTS" (Free Tier eligible)
5. Choose an Instance Type
   - Select "t2.micro" (Free Tier eligible)
6. Configure Instance Details
   - Keep default settings for a basic setup
7. Add Storage
   - The default 8GB is sufficient for this application
8. Add Tags (Optional)
   - You can add tags to help identify your instance
9. Configure Security Group
   - Create a new security group
   - Add rules to allow SSH (port 22) and Streamlit (port 8501)
   - Set source to "Anywhere" (0.0.0.0/0) for public access
10. Review and Launch
11. Create a new key pair, download it, and keep it secure
12. Launch the instance

## Step 2: Connect to Your EC2 Instance

1. From the EC2 Dashboard, select your running instance
2. Click "Connect"
3. Follow the instructions to connect via SSH
   - For macOS/Linux: `ssh -i /path/to/your-key.pem ubuntu@your-instance-public-dns`
   - Make sure to change permissions: `chmod 400 /path/to/your-key.pem`

## Step 3: Set Up the Environment

1. Update the package lists:
   ```
   sudo apt update
   sudo apt upgrade -y
   ```

2. Install Python, pip, and OpenCV dependencies:
   ```
   sudo apt install python3-pip python3-dev -y
   sudo apt install libgl1-mesa-glx libsm6 libxext6 libxrender-dev -y
   ```

3. Install Git:
   ```
   sudo apt install git -y
   ```

4. Clone the repository:
   ```
   git clone https://github.com/pratik21it/Video_Content_Moderation_using_Seed1.6.git
   cd Video_Content_Moderation_using_Seed1.6
   ```

5. Install required packages:
   ```
   pip3 install -r requirements.txt
   ```

## Step 4: Run the Streamlit App

1. Test the app locally on the EC2 instance:
   ```
   streamlit run app.py
   ```

2. To make the app accessible from the internet, run:
   ```
   streamlit run app.py --server.port=8501 --server.address=0.0.0.0
   ```

3. Access your app using your EC2 instance's public DNS or IP:
   ```
   http://your-instance-public-dns:8501
   ```
   or
   ```
   http://your-instance-public-ip:8501
   ```

## Step 5: Keep the App Running (Optional)

1. Install tmux to keep the app running after you disconnect:
   ```
   sudo apt install tmux -y
   ```

2. Create a new tmux session:
   ```
   tmux new -s streamlit
   ```

3. Run your Streamlit app:
   ```
   cd Video_Content_Moderation_using_Seed1.6
   streamlit run app.py --server.port=8501 --server.address=0.0.0.0
   ```

4. Detach from the tmux session (the app will continue running):
   - Press `Ctrl+B` and then `D`

5. To reattach to the session later:
   ```
   tmux attach -t streamlit
   ```

## Step 6: Set Up as a System Service (Recommended)

1. Create a systemd service file:
   ```
   sudo nano /etc/systemd/system/streamlit.service
   ```

2. Add the following content (adjust paths as needed):
   ```
   [Unit]
   Description=Streamlit Content Moderation App
   After=network.target

   [Service]
   User=ubuntu
   WorkingDirectory=/home/ubuntu/Video_Content_Moderation_using_Seed1.6
   ExecStart=/home/ubuntu/.local/bin/streamlit run app.py --server.port=8501 --server.address=0.0.0.0
   Restart=always
   RestartSec=5

   [Install]
   WantedBy=multi-user.target
   ```

3. Enable and start the service:
   ```
   sudo systemctl daemon-reload
   sudo systemctl enable streamlit
   sudo systemctl start streamlit
   ```

4. Check the status:
   ```
   sudo systemctl status streamlit
   ```

## Security Considerations

- The current setup exposes your app to the public internet
- Consider setting up HTTPS using a reverse proxy like Nginx
- Restrict access to specific IP addresses in your security group
- Set up authentication for your Streamlit app

## Cost Management

- AWS Free Tier includes 750 hours of t2.micro instances per month for 12 months
- Monitor your usage to avoid unexpected charges
- Set up billing alerts in AWS to be notified of any charges

## Troubleshooting

- If you can't access your app, check that:
  - The security group allows traffic on port 8501
  - The app is running with the correct server address (0.0.0.0)
  - The EC2 instance is running
- If you encounter OpenCV errors like `ImportError: libGL.so.1: cannot open shared object file: No such file or directory`:
  - Make sure you've installed the OpenCV dependencies:
    ```
    sudo apt install libgl1-mesa-glx libsm6 libxext6 libxrender-dev -y
    ```
  - Reinstall opencv-python:
    ```
    pip3 install --upgrade opencv-python
    ```
- Check application logs:
  ```
  sudo journalctl -u streamlit
  ```