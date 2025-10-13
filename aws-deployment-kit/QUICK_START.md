# Quick Start Guide - 5 Minutes

**Too busy to read the full guide?** Here's the absolute minimum to get started.

---

## 🎯 Choose Your Path

### Path A: Testing Without a Domain (Fastest)
Use this if you just want to test the deployment without buying a domain.
- **Time:** 15-20 minutes
- **Cost:** Free tier eligible
- **Result:** Website on CloudFront URL (e.g., `https://d123abc.cloudfront.net`)

### Path B: Production With Custom Domain
Use this for a real website with your own domain.
- **Time:** 45-60 minutes (DNS propagation)
- **Cost:** ~$0.50-1/month + domain
- **Result:** Website on your domain (e.g., `https://yourdomain.com`)

---

## ⚡ Path A: Quick Test (No Domain)

### 1. Bootstrap (2 minutes)
```bash
cd aws-deployment-kit
chmod +x scripts/bootstrap.sh
./scripts/bootstrap.sh
```
Follow prompts to configure AWS credentials.

### 2. Deploy Infrastructure (10-15 minutes, mostly waiting)
```bash
# Validate template first (optional)
./scripts/validate-stack.sh cloudformation/website-infrastructure-no-domain.yaml

# Deploy with AWS CLI
aws cloudformation create-stack \
  --stack-name test-website \
  --template-body file://cloudformation/website-infrastructure-no-domain.yaml \
  --parameters ParameterKey=ProjectName,ParameterValue=test-website \
  --region us-east-1

# Wait for completion
aws cloudformation wait stack-create-complete \
  --stack-name test-website \
  --region us-east-1
```

### 3. Get Stack Outputs
```bash
aws cloudformation describe-stacks \
  --stack-name test-website \
  --region us-east-1 \
  --query 'Stacks[0].Outputs'
```
Save the `WebsiteBucketName`, `CloudFrontDistributionId`, and `CloudFrontURL`.

### 4. Deploy Your Website (2 minutes)
```bash
# In your React/Vite project
npm run build

# Deploy (use values from step 3)
../aws-deployment-kit/scripts/deploy.sh <bucket-name> <distribution-id>
```

### 5. Visit Your Site! 🎉
Go to the CloudFront URL from step 3 (e.g., `https://d123abc.cloudfront.net`)

---

## ⚡ Path B: Production Setup (With Domain)

### 1. Bootstrap (2 minutes)
```bash
cd aws-deployment-kit
chmod +x scripts/bootstrap.sh
./scripts/bootstrap.sh
```
Follow prompts to configure AWS credentials.

### 2. Deploy Infrastructure (30-40 minutes, mostly waiting)
1. Go to [AWS CloudFormation Console](https://console.aws.amazon.com/cloudformation)
2. Click **Create stack** → **With new resources**
3. Upload `cloudformation/website-infrastructure.yaml`
4. Fill in:
   - **Stack name**: `my-website`
   - **DomainName**: `yourdomain.com`
   - **ProjectName**: `my-website`
   - **CreateHostedZone**: `Yes`
5. Click **Next** → **Next** → Check the IAM acknowledgment → **Submit**
6. ☕ Wait 30-40 minutes

### 3. Update Nameservers (5 minutes)
1. Go to CloudFormation → Your stack → **Outputs** tab
2. Copy the 4 nameservers from **HostedZoneNameServers**
3. Go to your domain registrar (GoDaddy, Namecheap, etc.)
4. Update nameservers to the AWS ones
5. Wait 10-60 minutes for DNS propagation

### 4. Deploy Your Website (2 minutes)
```bash
# In your React/Vite project
npm run build

# Deploy (get values from CloudFormation Outputs tab)
../aws-deployment-kit/scripts/deploy.sh <bucket-name> <distribution-id>

# Or with a specific AWS profile
../aws-deployment-kit/scripts/deploy.sh <bucket-name> <distribution-id> my-profile
```

### 5. Visit Your Site! 🎉
Go to `https://yourdomain.com`

---

## 📋 What You Need

- AWS account
- Domain name (or use CloudFront URL)
- React/Vite project
- 30-60 minutes total time

---

## 🆘 If Something Goes Wrong

Read the full **[GUIDE.md](GUIDE.md)** - it has detailed troubleshooting for every step.

Common issues:
- **Certificate stuck?** Wait 30 minutes, check nameservers
- **Access Denied?** Wait 10 minutes after deployment
- **Changes not showing?** Clear cache, hard refresh browser

---

## 💡 Pro Tips

1. **Use `us-east-1` region** for CloudFormation (required for certificates)
2. **Save your bucket name and distribution ID** from Outputs tab
3. **Create `.env` file** with these values for easier deployments
4. **Set up GitHub Actions** for automatic deployments (see README.md)

---

**Need more details?** Read the complete [GUIDE.md](GUIDE.md) for step-by-step instructions with screenshots and explanations.
