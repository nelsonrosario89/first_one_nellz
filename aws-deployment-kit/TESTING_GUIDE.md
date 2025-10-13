# Testing Guide - AWS Deployment Kit

This guide shows you how to test the deployment kit without purchasing a domain name.

---

## 🎯 Quick Test Deployment (No Domain Required)

Perfect for:
- Testing the deployment process
- Learning AWS infrastructure
- Development and staging environments
- Proof of concept projects

**Time:** 15-20 minutes  
**Cost:** Free tier eligible (~$0 for testing)  
**Result:** Fully functional website on CloudFront URL

---

## 📋 Prerequisites

1. AWS account (free to create)
2. AWS CLI configured with credentials
3. Node.js installed (for building your site)
4. A React/Vite project to deploy (or use our test site)

---

## 🚀 Step-by-Step Test Deployment

### Step 1: Set Up Environment (2 minutes)

```bash
cd aws-deployment-kit
chmod +x scripts/bootstrap.sh
./scripts/bootstrap.sh
```

This installs AWS CLI, Node.js, and verifies your setup.

### Step 2: Validate Template (Optional, 1 minute)

```bash
./scripts/validate-stack.sh cloudformation/website-infrastructure-no-domain.yaml
```

This checks that the CloudFormation template is valid.

### Step 3: Deploy Infrastructure (10-15 minutes)

```bash
# Create the stack
aws cloudformation create-stack \
  --stack-name test-website \
  --template-body file://cloudformation/website-infrastructure-no-domain.yaml \
  --parameters ParameterKey=ProjectName,ParameterValue=test-website \
  --region us-east-1

# Wait for completion (this takes 10-15 minutes)
aws cloudformation wait stack-create-complete \
  --stack-name test-website \
  --region us-east-1
```

**What gets created:**
- S3 bucket for your website files
- CloudFront distribution (global CDN)
- Origin Access Control (security)
- S3 bucket policy (permissions)

**What does NOT get created:**
- Route 53 hosted zone (no DNS needed)
- ACM SSL certificate (uses CloudFront default)

### Step 4: Get Stack Outputs (1 minute)

```bash
aws cloudformation describe-stacks \
  --stack-name test-website \
  --region us-east-1 \
  --query 'Stacks[0].Outputs' \
  --output table
```

You'll see:
- **WebsiteBucketName**: S3 bucket name (e.g., `test-website-123456789`)
- **CloudFrontDistributionId**: Distribution ID (e.g., `E1234ABCDEFGH`)
- **CloudFrontURL**: Your website URL (e.g., `https://d123abc.cloudfront.net`)

**Save these values!** You'll need them for deployment.

### Step 5: Create Test Website (Optional, 2 minutes)

If you don't have a website ready, create a simple test:

```bash
mkdir -p test-site/dist
cd test-site/dist

cat > index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Deployment</title>
    <style>
        body {
            font-family: system-ui, -apple-system, sans-serif;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .container {
            background: white;
            padding: 3rem;
            border-radius: 1rem;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            text-align: center;
        }
        h1 { color: #333; margin: 0 0 1rem; }
        p { color: #666; }
        .success { 
            background: #10b981; 
            color: white; 
            padding: 1rem 2rem; 
            border-radius: 0.5rem; 
            margin: 1rem 0;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Deployment Successful!</h1>
        <div class="success">✓ AWS Infrastructure Working</div>
        <p>Your CloudFormation stack deployed correctly!</p>
        <p><small>Replace this with your actual website.</small></p>
    </div>
</body>
</html>
EOF

cd ../..
```

### Step 6: Deploy Your Website (2 minutes)

```bash
# From your project directory (or test-site directory)
../aws-deployment-kit/scripts/deploy.sh <bucket-name> <distribution-id>

# Example:
../aws-deployment-kit/scripts/deploy.sh test-website-123456789 E1234ABCDEFGH

# With AWS profile:
../aws-deployment-kit/scripts/deploy.sh test-website-123456789 E1234ABCDEFGH my-profile
```

The script will:
1. Upload files to S3
2. Invalidate CloudFront cache
3. Show success message

### Step 7: Visit Your Website! 🎉

Open the CloudFront URL from Step 4 in your browser:
```
https://d123abc.cloudfront.net
```

Your website should load with HTTPS!

---

## 🔄 Making Updates

To update your website:

```bash
# Make changes to your code
# ...

# Build (if using React/Vite)
npm run build

# Deploy
../aws-deployment-kit/scripts/deploy.sh <bucket-name> <distribution-id>
```

Changes will be live in 1-2 minutes after cache invalidation.

---

## 🧹 Cleaning Up

When you're done testing, delete everything to avoid charges:

```bash
# Empty the S3 bucket first
aws s3 rm s3://<bucket-name> --recursive

# Delete the CloudFormation stack
aws cloudformation delete-stack \
  --stack-name test-website \
  --region us-east-1

# Wait for deletion to complete
aws cloudformation wait stack-delete-complete \
  --stack-name test-website \
  --region us-east-1
```

**Cost after deletion:** $0

---

## 🆚 Test vs Production

### Test Deployment (No Domain)
- ✅ Uses CloudFront URL
- ✅ Free HTTPS (CloudFront default certificate)
- ✅ Faster setup (10-15 min)
- ✅ No domain costs
- ❌ URL is not memorable (e.g., `d123abc.cloudfront.net`)
- ❌ No custom branding

### Production Deployment (With Domain)
- ✅ Custom domain (e.g., `yourdomain.com`)
- ✅ Professional appearance
- ✅ Custom SSL certificate
- ✅ Route 53 DNS management
- ❌ Requires domain purchase ($10-15/year)
- ❌ Longer setup (30-40 min for DNS/certificate)
- ❌ Additional costs (~$0.50/month for Route 53)

---

## 🔍 Troubleshooting

### Stack Creation Failed
```bash
# Check stack events for errors
aws cloudformation describe-stack-events \
  --stack-name test-website \
  --region us-east-1 \
  --max-items 10
```

Common issues:
- **Region not us-east-1**: CloudFront works best with us-east-1
- **IAM permissions**: Ensure your AWS user has CloudFormation permissions
- **Resource limits**: Check AWS service quotas

### Website Shows "Access Denied"
- Wait 2-3 minutes after deployment
- Check that files were uploaded to S3
- Verify CloudFront distribution is deployed

### Changes Not Showing
- Wait 1-2 minutes for cache invalidation
- Hard refresh browser (Cmd+Shift+R or Ctrl+Shift+R)
- Check invalidation status:
  ```bash
  aws cloudfront list-invalidations \
    --distribution-id <distribution-id>
  ```

### Deployment Script Fails
- Verify AWS credentials: `aws sts get-caller-identity`
- Check bucket name and distribution ID are correct
- Ensure `dist/` folder exists with built files

---

## 📊 What You're Testing

This test deployment validates:

1. **CloudFormation Template**
   - ✅ Syntax is correct
   - ✅ Resources create successfully
   - ✅ Outputs are properly configured

2. **S3 Configuration**
   - ✅ Bucket creates with correct settings
   - ✅ Versioning enabled
   - ✅ Public access blocked (secure)
   - ✅ Bucket policy allows CloudFront access

3. **CloudFront Configuration**
   - ✅ Distribution deploys successfully
   - ✅ Origin Access Control works
   - ✅ HTTPS enabled
   - ✅ Caching configured
   - ✅ Error pages for SPA routing

4. **Deployment Process**
   - ✅ Files upload to S3
   - ✅ Cache invalidation works
   - ✅ Website accessible via HTTPS
   - ✅ Updates deploy correctly

---

## 🎓 Next Steps

After successful testing:

1. **Move to Production**
   - Buy a domain name
   - Use `website-infrastructure.yaml` template
   - Follow the full GUIDE.md

2. **Customize**
   - Modify CloudFormation parameters
   - Adjust caching policies
   - Add custom error pages

3. **Automate**
   - Set up CI/CD with GitHub Actions
   - Create deployment pipelines
   - Add automated testing

4. **Monitor**
   - Enable CloudFront logging
   - Set up CloudWatch alarms
   - Track costs with AWS Budgets

---

## 💡 Pro Tips

1. **Use AWS Profiles**: Separate test and production credentials
   ```bash
   aws configure --profile test
   ./scripts/deploy.sh <bucket> <dist-id> test
   ```

2. **Version Your Deployments**: Enable S3 versioning (already done!)
   ```bash
   aws s3api list-object-versions --bucket <bucket-name>
   ```

3. **Test Locally First**: Use `npx serve dist` before deploying

4. **Monitor Costs**: Set up billing alerts in AWS Console

5. **Keep Stack Names Consistent**: Use descriptive names like `project-env`
   - `myapp-test`
   - `myapp-staging`
   - `myapp-production`

---

## ✅ Success Checklist

- [ ] Bootstrap script completed successfully
- [ ] CloudFormation stack created (CREATE_COMPLETE)
- [ ] Stack outputs retrieved
- [ ] Website files uploaded to S3
- [ ] CloudFront cache invalidated
- [ ] Website accessible via HTTPS
- [ ] Updates deploy successfully
- [ ] Cleanup completed (if testing only)

---

**Ready for production?** See [GUIDE.md](GUIDE.md) for the full deployment with custom domain!
