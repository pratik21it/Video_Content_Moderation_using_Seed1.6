#!/bin/bash

# Script to help set up Elastic IP for EC2 instance
# This script provides guidance and commands for setting up a free domain

echo "========================================================="
echo "Free Domain Setup Helper for AWS EC2"
echo "========================================================="
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "AWS CLI is not installed. Please install it first:"
    echo "pip install awscli"
    echo "Then configure it with: aws configure"
    exit 1
fi

# Check if AWS CLI is configured
aws sts get-caller-identity &> /dev/null
if [ $? -ne 0 ]; then
    echo "AWS CLI is not configured. Please run: aws configure"
    exit 1
fi

echo "Step 1: Getting your current EC2 instance ID"
echo "----------------------------------------"
INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
if [ -z "$INSTANCE_ID" ]; then
    echo "Error: Could not retrieve instance ID. Are you running this on an EC2 instance?"
    echo "If not on EC2, please enter your instance ID manually:"
    read -p "Instance ID: " INSTANCE_ID
else
    echo "Your instance ID: $INSTANCE_ID"
fi

echo ""
echo "Step 2: Allocating a new Elastic IP"
echo "----------------------------------------"
echo "This will allocate a new Elastic IP address to your AWS account."
echo "Note: AWS Free Tier includes one Elastic IP as long as it's associated with a running instance."
read -p "Proceed with allocation? (y/n): " PROCEED

if [ "$PROCEED" != "y" ]; then
    echo "Allocation cancelled."
    exit 0
fi

echo "Allocating Elastic IP..."
ALLOCATION_ID=$(aws ec2 allocate-address --domain vpc --query 'AllocationId' --output text)
ELASTIC_IP=$(aws ec2 describe-addresses --allocation-ids $ALLOCATION_ID --query 'Addresses[0].PublicIp' --output text)

echo "Allocated Elastic IP: $ELASTIC_IP"
echo "Allocation ID: $ALLOCATION_ID"

echo ""
echo "Step 3: Associating Elastic IP with your instance"
echo "----------------------------------------"
echo "This will associate the Elastic IP with your EC2 instance."
read -p "Proceed with association? (y/n): " PROCEED

if [ "$PROCEED" != "y" ]; then
    echo "Association cancelled."
    echo "Warning: You will be charged for an unassociated Elastic IP."
    echo "To release it, run: aws ec2 release-address --allocation-id $ALLOCATION_ID"
    exit 0
fi

echo "Associating Elastic IP with instance $INSTANCE_ID..."
aws ec2 associate-address --instance-id $INSTANCE_ID --allocation-id $ALLOCATION_ID

echo ""
echo "Step 4: Setting up a free domain name"
echo "----------------------------------------"
echo "Now that you have an Elastic IP ($ELASTIC_IP), you can set up a free domain name."
echo "Follow these steps:"
echo ""
echo "1. Go to Freenom.com and register for a free domain (.tk, .ml, .ga, .cf, or .gq)"
echo "2. After registration, go to 'Services > My Domains > Manage Domain > Manage Freenom DNS'"
echo "3. Add two 'A' records:"
echo "   - Leave the 'Name' field empty for the root domain, set 'Target' to $ELASTIC_IP"
echo "   - Add another with 'Name' as 'www', set 'Target' to $ELASTIC_IP"
echo "4. Save changes and wait for DNS propagation (can take 10-30 minutes)"
echo ""
echo "Alternatively, you can use No-IP.com or Afraid.org for free dynamic DNS services."
echo ""
echo "========================================================="
echo "Setup complete! Your Elastic IP is: $ELASTIC_IP"
echo "Use this IP when configuring your free domain DNS settings."
echo "========================================================="