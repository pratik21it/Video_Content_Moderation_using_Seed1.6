# Setting Up a Free Domain Name for Your AWS EC2 Instance

This guide will help you set up a free domain name for your AWS EC2 instance instead of using the IP address directly.

## Prerequisites

- An AWS account with an EC2 instance running your Streamlit app
- Basic understanding of DNS (Domain Name System)

## Step 1: Allocate an Elastic IP Address

Since EC2 instances get a new public IP address each time they restart, you should allocate an Elastic IP address to ensure your domain always points to your instance.

1. Go to the AWS Management Console
2. Navigate to EC2 > Network & Security > Elastic IP
3. Click "Allocate Elastic IP address"
4. Select "Amazon's pool of IPv4 addresses" and click "Allocate"
5. Select the newly created Elastic IP and click "Actions" > "Associate Elastic IP address"
6. Choose your EC2 instance from the dropdown and click "Associate"

> **Note:** AWS Free Tier includes one free Elastic IP address as long as it's associated with a running instance. You'll be charged if you keep an Elastic IP that's not associated with a running instance.

## Step 2: Get a Free Domain Name from Freenom

Freenom offers free domain names with extensions like .tk, .ml, .ga, .cf, and .gq.

1. Go to [Freenom](https://www.freenom.com)
2. Create an account or log in if you already have one
3. Go to Services > Register a New Domain
4. Search for your desired domain name and check its availability
5. Select a free domain extension (.tk, .ml, .ga, .cf, or .gq)
6. Choose a period (up to 12 months for free)
7. Complete the checkout process

## Step 3: Configure DNS Settings

### Option 1: Using Freenom's DNS Service (Simpler)

1. In your Freenom account, go to Services > My Domains
2. Find your domain and click "Manage Domain"
3. Go to "Manage Freenom DNS"
4. Add two "A" records:
   - Name: leave blank (for root domain)
   - Type: A
   - TTL: 3600 (or lower)
   - Target: Your Elastic IP address
   
   And:
   - Name: www
   - Type: A
   - TTL: 3600 (or lower)
   - Target: Your Elastic IP address
5. Click "Save Changes"

### Option 2: Using AWS Route 53 (More Advanced)

1. Go to AWS Management Console > Route 53
2. Create a hosted zone with your domain name
3. Create two "A" records pointing to your Elastic IP address:
   - One for the root domain (leave name blank)
   - One for www subdomain
4. Note the four AWS nameservers assigned to your hosted zone
5. In your Freenom account, go to Services > My Domains
6. Find your domain and click "Manage Domain"
7. Go to "Management Tools" > "Nameservers"
8. Select "Use custom nameservers"
9. Enter the four AWS nameservers
10. Click "Change Nameservers"

## Step 4: Configure Your EC2 Instance

Make sure your EC2 security group allows inbound traffic on ports 80 (HTTP) and 443 (HTTPS).

1. Go to EC2 > Network & Security > Security Groups
2. Select the security group associated with your instance
3. Add inbound rules for HTTP (port 80) and HTTPS (port 443) if not already present

## Step 5: Update Your Streamlit App Configuration

If your Streamlit app is configured to use a specific host or port, update it to work with your domain name.

In your Streamlit app, you might want to run it with:

```bash
streamlit run app.py --server.port 80 --server.address 0.0.0.0
```

## Step 6: Test Your Domain

After DNS propagation (which can take 10 minutes to 48 hours), you should be able to access your Streamlit app using your domain name.

## Alternative Free Domain Options

1. **No-IP**: Offers free dynamic DNS services with domains like example.ddns.net
   - Visit [No-IP](https://www.noip.com) to sign up
   - Create a free hostname
   - Point it to your Elastic IP

2. **Afraid.org (FreeDNS)**: Another free DNS service
   - Visit [Afraid.org](https://freedns.afraid.org)
   - Register and select a free subdomain
   - Point it to your Elastic IP

## Maintaining Your Free Domain

- Freenom domains need to be renewed every 12 months to keep them free
- Set a reminder to renew your domain before it expires
- No-IP free domains require confirmation every 30 days

## Troubleshooting

- **Domain not working**: DNS changes can take time to propagate. Wait at least 30 minutes before troubleshooting.
- **Security issues**: Free domains may be more vulnerable to security threats. Consider implementing additional security measures.
- **EC2 instance restarted**: If you didn't set up an Elastic IP and your instance restarted, you'll need to update your DNS records with the new IP address.

## Conclusion

You now have a free domain name pointing to your AWS EC2 instance! This makes your application more professional and easier to access than using an IP address directly.