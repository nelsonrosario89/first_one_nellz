# Contact Form Setup Guide

**Optional Feature:** Add a working contact form to your portfolio website

**Time Required:** 10-15 minutes  
**Prerequisite:** Verified email in SES (see PREREQUISITES.md Step 6)

---

## 🎯 What You'll Get

A fully functional contact form that:
- ✅ Sends submissions to your email via AWS SES
- ✅ Runs on AWS Lambda (serverless, pay-per-use)
- ✅ Includes spam protection
- ✅ Works with your custom domain
- ✅ Costs ~$0.10/month (or free with Lambda free tier)

---

## 📋 Prerequisites

Before setting up the contact form:

- [ ] **Email verified in SES** - See PREREQUISITES.md Step 6
- [ ] **Website deployed** - Complete main deployment first
- [ ] **AWS CLI configured** - With proper credentials

---

## 🚀 Quick Setup (3 Steps)

### Step 1: Verify Your Email (If Not Done)

**Already verified?** Skip to Step 2.

```bash
# Quick verification
aws ses verify-email-identity \
  --email-address your-email@example.com \
  --region us-east-1

# Check your email and click the verification link
```

Or use the AWS Console (easier):
1. Go to SES Console (us-east-1 region)
2. Click "Verified identities" → "Create identity"
3. Enter your email
4. Check email and click verification link

### Step 2: Deploy Contact Form API

Use the provided script:

```bash
cd aws-deployment-kit

# Run the setup script
./scripts/deploy-contact-api.sh

# Follow the prompts:
# - Stack name (e.g., my-website-contact-api)
# - Your verified email address
# - AWS profile (if using named profile)
```

This deploys:
- Lambda function for handling form submissions
- API Gateway endpoint for receiving submissions
- IAM roles and permissions
- SES integration

**Time:** ~5 minutes

### Step 3: Add Form to Your Website

The script will output an API endpoint URL. Add this to your website:

```html
<!-- Add this form to your HTML -->
<form id="contactForm" action="YOUR_API_ENDPOINT" method="POST">
  <input type="text" name="name" placeholder="Your Name" required>
  <input type="email" name="email" placeholder="Your Email" required>
  <textarea name="message" placeholder="Your Message" required></textarea>
  <button type="submit">Send Message</button>
</form>

<script>
document.getElementById('contactForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const formData = new FormData(e.target);
  const data = Object.fromEntries(formData);
  
  try {
    const response = await fetch('YOUR_API_ENDPOINT', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    
    if (response.ok) {
      alert('Message sent successfully!');
      e.target.reset();
    } else {
      alert('Failed to send message. Please try again.');
    }
  } catch (error) {
    alert('Error sending message. Please try again.');
  }
});
</script>
```

Replace `YOUR_API_ENDPOINT` with the URL from Step 2.

---

## 🔧 Manual Setup (Alternative)

If you prefer to deploy manually:

### Step 1: Create IAM User for SES (Optional)

```bash
./scripts/setup-ses-iam-user.sh
```

This creates an IAM user with SES permissions and generates SMTP credentials.

### Step 2: Deploy CloudFormation Stack

```bash
aws cloudformation create-stack \
  --stack-name my-contact-api \
  --template-body file://cloudformation/contact-form-api.yaml \
  --parameters \
    ParameterKey=VerifiedEmail,ParameterValue=your-email@example.com \
    ParameterKey=ProjectName,ParameterValue=my-website \
  --capabilities CAPABILITY_IAM \
  --region us-east-1
```

### Step 3: Get API Endpoint

```bash
aws cloudformation describe-stacks \
  --stack-name my-contact-api \
  --region us-east-1 \
  --query 'Stacks[0].Outputs[?OutputKey==`ContactFormApiUrl`].OutputValue' \
  --output text
```

---

## 📧 Testing Your Contact Form

### Test in Sandbox Mode

1. **Submit a test message** through your contact form
2. **Check your email** - You should receive the submission
3. **Verify details** - Name, email, message all included

### Common Issues

**Not receiving emails?**
- Check spam folder
- Verify email is confirmed in SES
- Check Lambda logs in CloudWatch
- Ensure region is us-east-1

**Getting CORS errors?**
- API Gateway CORS is configured in the template
- Check browser console for specific error
- Verify API endpoint URL is correct

**Form submission fails?**
- Check API endpoint URL
- Verify Lambda function deployed
- Check CloudWatch logs for errors

---

## 💰 Cost

### Contact Form Costs
- **Lambda:** FREE (1M requests/month free tier)
- **API Gateway:** FREE (1M requests/month free tier)
- **SES:** $0.10 per 1,000 emails
- **Typical usage:** ~$0.10/month or FREE

**Example:** 100 form submissions/month = FREE

---

## 🔒 Security Features

The contact form includes:
- ✅ CORS protection
- ✅ Rate limiting (via API Gateway)
- ✅ Input validation
- ✅ Spam protection
- ✅ Secure Lambda execution
- ✅ IAM role-based permissions

---

## 🎨 Customization

### Customize Email Template

Edit `lambda/contact-form-handler.js`:

```javascript
// Customize the email subject
const subject = `New Contact Form Submission from ${name}`;

// Customize the email body
const body = `
Name: ${name}
Email: ${email}
Message: ${message}
`;
```

### Add Fields

Add more form fields:
- Company name
- Phone number
- Subject/Topic
- Budget range
- Project timeline

Update both the HTML form and Lambda function.

### Style the Form

Add CSS styling to match your website design. The form structure is flexible and can be styled however you like.

---

## 📊 Monitoring

### View Form Submissions

**CloudWatch Logs:**
```bash
aws logs tail /aws/lambda/contact-form-handler \
  --follow \
  --region us-east-1
```

**API Gateway Metrics:**
- Go to API Gateway Console
- Click your API
- View "Dashboard" for metrics

### Set Up Alerts

Create CloudWatch alarms for:
- Failed Lambda executions
- High error rates
- Unusual traffic patterns

---

## 🆘 Troubleshooting

### Email Not Verified
```bash
# Check verification status
aws ses get-identity-verification-attributes \
  --identities your-email@example.com \
  --region us-east-1
```

Should show "Success" status.

### Lambda Errors
```bash
# View recent logs
aws logs tail /aws/lambda/contact-form-handler \
  --since 1h \
  --region us-east-1
```

### API Gateway Issues
- Check API endpoint URL is correct
- Verify CORS settings
- Test with curl:
  ```bash
  curl -X POST YOUR_API_ENDPOINT \
    -H "Content-Type: application/json" \
    -d '{"name":"Test","email":"test@example.com","message":"Test message"}'
  ```

---

## 🎯 Next Steps

After setting up the contact form:

1. **Test thoroughly** - Submit multiple test messages
2. **Add to portfolio** - Integrate form into your design
3. **Monitor usage** - Check CloudWatch metrics
4. **Request production access** - If you need to send to unverified emails
5. **Add analytics** - Track form submissions

---

## 💡 Pro Tips

1. **Use domain email** - `contact@yourdomain.com` looks professional
2. **Test in sandbox** - Verify everything works before production
3. **Monitor costs** - Set up billing alerts
4. **Add honeypot** - Extra spam protection
5. **Response time** - Add auto-reply email
6. **Backup submissions** - Store in DynamoDB or S3
7. **Analytics** - Track conversion rates

---

## ✅ Success Checklist

- [ ] Email verified in SES
- [ ] Contact API deployed
- [ ] API endpoint obtained
- [ ] Form added to website
- [ ] Test submission successful
- [ ] Received test email
- [ ] Form styled to match site
- [ ] Production ready

---

**Questions?** See the FAQ.md or ask in the community!
