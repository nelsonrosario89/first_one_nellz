# Prerequisites - Complete This BEFORE the Demo

**⏱️ Time Required:** 30-45 minutes  
**💰 Cost:** ~$12-15 for domain (one-time annual fee)

---

## ⚠️ IMPORTANT: Do This Before Attending the Demo

To follow along with the live demo and deploy your own site, you need to complete these prerequisites **in advance**. The demo moves quickly, so having these done beforehand is essential.

---

## ✅ Checklist Overview

Complete these steps in order:

- [ ] **Step 1:** Create AWS Account (10 min)
- [ ] **Step 2:** Set Up AWS CLI with Credentials (10 min)
- [ ] **Step 3:** Bootstrap Your Machine (5 min)
- [ ] **Step 4:** Register Domain in Route 53 (5 min)
- [ ] **Step 5:** Request SSL Certificate in ACM (10 min)
- [ ] **Step 6:** Verify Email in SES (5 min) - For contact form

**Total Time:** ~45 minutes  
**Do this at least 24 hours before the demo** (DNS, certificates, and email verification take time to propagate)

---

## 📋 Step 1: Create AWS Account (10 minutes)

### What You Need
- Email address
- Credit card (for verification - won't be charged during free tier)
- Phone number

### Instructions

1. **Go to AWS:**
   - Visit: https://aws.amazon.com
   - Click "Create an AWS Account"

2. **Fill Out Information:**
   - Root user email address
   - AWS account name (e.g., "My Personal Account")
   - Choose password

3. **Contact Information:**
   - Account type: Personal
   - Full name, phone, address

4. **Payment Information:**
   - Add credit card (required for verification)
   - You won't be charged during free tier
   - Set up billing alerts (recommended)

5. **Identity Verification:**
   - Verify phone number via SMS or call

6. **Select Support Plan:**
   - Choose "Basic Support - Free"

7. **Complete Setup:**
   - Wait for confirmation email
   - Sign in to AWS Console

### ✅ Verification
- [ ] Can log into AWS Console at https://console.aws.amazon.com
- [ ] See AWS Management Console dashboard

---

## 🔐 Step 2: Set Up AWS CLI with Credentials (10 minutes)

### Create IAM User (Recommended - Don't Use Root Account)

1. **Open IAM Console:**
   - Go to: https://console.aws.amazon.com/iam
   - Click "Users" in left sidebar
   - Click "Create user"

2. **User Details:**
   - User name: `deployment-user` (or your preferred name)
   - Click "Next"

3. **Set Permissions:**
   - Select "Attach policies directly"
   - Search and select these policies:
     - `AdministratorAccess` (for full deployment access)
     - OR for minimal access: `AmazonS3FullAccess`, `CloudFrontFullAccess`, `AWSCertificateManagerFullAccess`, `Route53FullAccess`, `CloudFormationFullAccess`
   - Click "Next"

4. **Review and Create:**
   - Review settings
   - Click "Create user"

5. **Create Access Keys:**
   - Click on the user you just created
   - Click "Security credentials" tab
   - Scroll to "Access keys"
   - Click "Create access key"
   - Choose "Command Line Interface (CLI)"
   - Check the confirmation box
   - Click "Next"
   - Add description tag (optional): "Deployment CLI"
   - Click "Create access key"

6. **Save Your Credentials:**
   - **IMPORTANT:** Copy both:
     - Access key ID
     - Secret access key
   - Click "Download .csv file" (backup)
   - Store these securely - you won't see them again!

### Install and Configure AWS CLI

**We'll do this together in the demo using the bootstrap script**, but if you want to do it now:

1. **Run Bootstrap Script:**
   ```bash
   cd aws-deployment-kit
   chmod +x scripts/bootstrap.sh
   ./scripts/bootstrap.sh
   ```

2. **When Prompted for AWS Configuration:**
   - AWS Access Key ID: [paste your access key]
   - AWS Secret Access Key: [paste your secret key]
   - Default region: `us-east-1` (IMPORTANT: Use us-east-1)
   - Default output format: `json`

3. **Create Named Profile (Optional but Recommended):**
   ```bash
   aws configure --profile deployment
   ```
   - Enter same credentials
   - This creates a separate profile for deployments

### ✅ Verification
```bash
aws sts get-caller-identity
```
Should show your account information.

---

## 💻 Step 3: Bootstrap Your Machine (5 minutes)

### What Gets Installed
- AWS CLI (if not already installed)
- Node.js (if not already installed)
- Deployment scripts

### Instructions

1. **Navigate to the Kit:**
   ```bash
   cd aws-deployment-kit
   ```

2. **Make Bootstrap Script Executable:**
   ```bash
   chmod +x scripts/bootstrap.sh
   ```

3. **Run Bootstrap:**
   ```bash
   ./scripts/bootstrap.sh
   ```

4. **Follow Prompts:**
   - Install AWS CLI? (if needed)
   - Install Node.js? (if needed)
   - Configure AWS credentials? (if not done in Step 2)

### ✅ Verification
```bash
# Check AWS CLI
aws --version

# Check Node.js
node --version

# Check npm
npm --version

# Verify AWS credentials
aws sts get-caller-identity
```

All commands should work without errors.

---

## 🌐 Step 4: Register Domain in Route 53 (5 minutes)

### Why Do This First?
- Domain registration takes 10-60 minutes to complete
- You need the domain for the SSL certificate
- Doing this early ensures it's ready for the demo

### Instructions

1. **Open Route 53 Console:**
   - Go to: https://console.aws.amazon.com/route53
   - Click "Registered domains" in left sidebar
   - Click "Register domain"

2. **Search for Domain:**
   - Enter your desired domain name
   - Click "Check"
   - Choose an available domain (.com, .net, .io, etc.)
   - Typical cost: $12-15/year

3. **Add to Cart:**
   - Click "Add to cart"
   - Click "Continue"

4. **Contact Information:**
   - Fill out registrant contact details
   - Enable/disable privacy protection (recommended: enable)
   - Click "Continue"

5. **Review and Complete:**
   - Review all details
   - Accept terms and conditions
   - Click "Complete order"

6. **Wait for Confirmation:**
   - Check email for verification (if required)
   - Click verification link
   - Domain registration takes 10-60 minutes

### ✅ Verification
- [ ] Domain shows in Route 53 "Registered domains"
- [ ] Status shows "Successful" or "In progress"
- [ ] Email verification completed (if required)

### 💡 Domain Suggestions
- Use your name: `yourname.com`
- Professional: `yourname.dev` or `yourname.io`
- Brand: `yourbrand.com`
- Keep it short and memorable

---

## 🔒 Step 5: Request SSL Certificate in ACM (10 minutes)

### Why Do This First?
- Certificate validation takes 5-30 minutes
- Must be done in `us-east-1` region for CloudFront
- Needs domain from Step 4 to be registered

### ⚠️ IMPORTANT: Region Must Be us-east-1

CloudFront requires certificates to be in `us-east-1` region!

### Instructions

1. **Switch to us-east-1 Region:**
   - In AWS Console, top-right corner
   - Click region dropdown
   - Select "US East (N. Virginia) us-east-1"
   - **Verify you're in us-east-1 before proceeding!**

2. **Open ACM Console:**
   - Go to: https://console.aws.amazon.com/acm
   - Verify region shows "N. Virginia" (us-east-1)
   - Click "Request certificate"

3. **Request Public Certificate:**
   - Select "Request a public certificate"
   - Click "Next"

4. **Domain Names:**
   - Add your domain name: `yourdomain.com`
   - Click "Add another name to this certificate"
   - Add www subdomain: `www.yourdomain.com`
   - Click "Next"

5. **Validation Method:**
   - Select "DNS validation - recommended"
   - Click "Next"

6. **Key Algorithm:**
   - Leave as default (RSA 2048)
   - Click "Next"

7. **Tags (Optional):**
   - Add tags if desired (e.g., Name: My Website Certificate)
   - Click "Next"

8. **Review and Request:**
   - Review all details
   - Click "Request"

9. **Create DNS Records (IMPORTANT!):**
   - You'll see "Pending validation" status
   - Click "View certificate"
   - Under "Domains" section, you'll see CNAME records
   - Click "Create records in Route 53" button
   - Click "Create records"
   - Wait for confirmation

10. **Wait for Validation:**
    - Status will change from "Pending validation" to "Issued"
    - This takes 5-30 minutes
    - Refresh the page periodically
    - ☕ Take a break!

### ✅ Verification
- [x] Certificate status shows "Issued" (not "Pending validation")
- [x] Both domain names listed (yourdomain.com and www.yourdomain.com)
- [x] Region is us-east-1
- [x] DNS validation records created in Route 53

### 🔍 Troubleshooting

**Certificate Stuck on "Pending validation"?**
- Wait 30 minutes (it can be slow)
- Check Route 53 has the validation CNAME records
- Verify domain registration is complete
- Make sure you clicked "Create records in Route 53"

**Can't find "Create records in Route 53" button?**
- Your domain must be registered in Route 53
- You must be viewing the certificate details page
- Refresh the page and look under "Domains" section

---

## 📧 Step 6: Verify Email in SES (5 minutes)

### Why Do This?
If you want to use the contact form feature (optional but recommended), you need to verify your email address in Amazon SES (Simple Email Service). This allows your website to send you contact form submissions.

### ⚠️ IMPORTANT: Region Must Be us-east-1

Use the same region as your certificate!

### Instructions

1. **Switch to us-east-1 Region:**
   - In AWS Console, top-right corner
   - Click region dropdown
   - Select "US East (N. Virginia) us-east-1"
   - **Verify you're in us-east-1!**

2. **Open SES Console:**
   - Go to: https://console.aws.amazon.com/ses
   - Verify region shows "N. Virginia" (us-east-1)

3. **Navigate to Verified Identities:**
   - In left sidebar, click "Verified identities"
   - Click "Create identity"

4. **Create Email Identity:**
   - Identity type: Select "Email address"
   - Email address: Enter your email (e.g., `you@yourdomain.com` or `you@gmail.com`)
   - Click "Create identity"

5. **Check Your Email:**
   - AWS will send a verification email immediately
   - Subject: "Amazon Web Services - Email Address Verification Request"
   - Click the verification link in the email
   - **Must click within 24 hours!**

6. **Confirm Verification:**
   - Return to SES Console
   - Refresh the page
   - Your email should show "Verified" status

7. **Request Production Access (Optional):**
   - By default, SES is in "Sandbox mode" (can only send to verified emails)
   - For production contact forms, request production access:
     - Click "Account dashboard" in left sidebar
     - Click "Request production access"
     - Fill out the form (takes 24 hours for approval)
   - **For testing/demo:** Sandbox mode is fine!

### ✅ Verification
- [ ] Email shows "Verified" status in SES Console
- [ ] Region is us-east-1
- [ ] Verification email received and clicked

### 💡 Pro Tips

**Use Your Domain Email:**
- If your domain is `yourdomain.com`
- Verify `contact@yourdomain.com` or `hello@yourdomain.com`
- Looks more professional than Gmail

**Verify Multiple Emails:**
- Verify your personal email for testing
- Verify your domain email for production
- Both can be used

**Sandbox vs Production:**
- **Sandbox:** Can only send to verified emails (good for testing)
- **Production:** Can send to anyone (requires approval)
- **For demo:** Sandbox is sufficient!

### 🔍 Troubleshooting

**Didn't receive verification email?**
- Check spam folder
- Wait 5 minutes and check again
- Try a different email address
- Make sure email address is typed correctly

**Verification link expired?**
- Delete the identity in SES Console
- Create a new identity
- Click the link within 24 hours

**Need to send to unverified emails?**
- Request production access (takes 24 hours)
- Or verify recipient emails in sandbox mode

---

## 📋 Pre-Demo Checklist

Complete this checklist **at least 24 hours before the demo:**

### Account Setup
- [ ] AWS account created and verified
- [ ] Can log into AWS Console
- [ ] IAM user created (not using root account)
- [ ] Access keys created and saved securely

### Local Machine Setup
- [ ] AWS CLI installed
- [ ] AWS CLI configured with credentials
- [ ] Node.js installed
- [ ] Bootstrap script run successfully
- [ ] Can run `aws sts get-caller-identity` successfully

### Domain Setup
- [ ] Domain registered in Route 53
- [ ] Domain status is "Successful"
- [ ] Email verification completed (if required)
- [ ] Domain shows in Route 53 "Registered domains"

### SSL Certificate Setup
- [ ] Certificate requested in ACM
- [ ] Region is us-east-1 (verified!)
- [ ] DNS validation records created in Route 53
- [ ] Certificate status is "Issued" (not "Pending")
- [ ] Both domain and www subdomain included

### Email Setup (For Contact Form)
- [ ] Email verified in SES
- [ ] Region is us-east-1
- [ ] Verification email clicked
- [ ] Email shows "Verified" status
- [ ] (Optional) Production access requested if needed

### Ready for Demo
- [ ] All above items checked
- [ ] Have domain name written down
- [ ] Have verified email address written down
- [ ] Have certificate ARN ready (optional - we'll find it in demo)
- [ ] AWS CLI profile name noted (if using named profile)

---

## 💰 Cost Breakdown

### One-Time Costs
- **Domain Registration:** $12-15/year (varies by TLD)

### Monthly Costs (After Free Tier)
- **Route 53 Hosted Zone:** $0.50/month
- **S3 Storage:** ~$0.10/month (small site)
- **CloudFront:** ~$0.50-2/month (normal traffic)
- **ACM Certificate:** FREE forever
- **Total:** ~$1-3/month

### Free Tier (First 12 Months)
- S3: 5 GB storage, 20K requests FREE
- CloudFront: 1 TB transfer, 10M requests FREE
- Route 53: $0.50/month (not free)
- **Total first year:** ~$0.50-1/month + domain

---

## 🆘 Getting Help

### Before the Demo
If you get stuck on prerequisites:

1. **Check Documentation:**
   - AWS has great docs for each service
   - Search for specific error messages

2. **Common Issues:**
   - **AWS CLI not working:** Run bootstrap script again
   - **Certificate pending:** Wait 30 minutes, check DNS records
   - **Domain not registered:** Check email for verification link
   - **Wrong region:** Switch to us-east-1 for certificate

3. **Ask for Help:**
   - Post in Patreon community
   - Ask in Slack channel
   - Include error messages and screenshots

### During the Demo
- Ask questions in chat
- We'll troubleshoot together
- Don't worry if something doesn't work - we'll fix it!

---

## 🎯 What Happens in the Demo

Once you have prerequisites complete, in the demo we'll:

1. **Review Setup** (5 min)
   - Verify everyone's prerequisites
   - Quick troubleshooting

2. **Deploy Infrastructure** (10 min)
   - Use CloudFormation template
   - Connect domain and certificate
   - Create S3 and CloudFront

3. **Build Portfolio** (10 min)
   - Fill out questionnaire
   - Generate website
   - Customize if desired

4. **Deploy Website** (5 min)
   - Upload files to S3
   - Invalidate cache
   - Site goes live!

5. **Q&A** (10 min)
   - Answer questions
   - Troubleshoot issues
   - Next steps

---

## 💡 Pro Tips

1. **Do This Early:** Complete prerequisites 24-48 hours before demo
2. **Use us-east-1:** Always use us-east-1 region for certificates
3. **Save Credentials:** Keep access keys in a secure password manager
4. **Enable MFA:** Add multi-factor authentication to your AWS account
5. **Set Billing Alerts:** Create alerts at $5, $10, $20 to avoid surprises
6. **Test AWS CLI:** Run `aws sts get-caller-identity` to verify setup
7. **Check Certificate:** Make sure it shows "Issued" before demo
8. **Have Domain Ready:** Write down your domain name for the demo

---

## 📞 Support Resources

### AWS Documentation
- **IAM:** https://docs.aws.amazon.com/iam/
- **Route 53:** https://docs.aws.amazon.com/route53/
- **ACM:** https://docs.aws.amazon.com/acm/
- **CLI:** https://docs.aws.amazon.com/cli/

### Video Tutorials
- AWS Account Setup: Search YouTube for "AWS account setup"
- AWS CLI Configuration: Search "AWS CLI setup tutorial"
- Route 53 Domain: Search "Route 53 register domain"
- ACM Certificate: Search "AWS ACM certificate tutorial"

### Community
- Patreon community discussions
- GRC Engineering Book Club Slack
- AWS Forums: https://forums.aws.amazon.com

---

## ✅ You're Ready!

Once you've completed all steps in the checklist, you're ready for the demo!

**See you at the demo!** 🚀

---

## 🔖 Quick Reference

**AWS Console:** https://console.aws.amazon.com  
**Route 53:** https://console.aws.amazon.com/route53  
**ACM:** https://console.aws.amazon.com/acm  
**IAM:** https://console.aws.amazon.com/iam  

**Region for Certificate:** us-east-1 (N. Virginia)  
**Recommended Profile Name:** deployment  
**Domain Cost:** $12-15/year  
**Monthly Cost:** $1-3/month after free tier  

---

**Questions?** Ask in Patreon community or Slack before the demo!
