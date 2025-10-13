# Portfolio Builder Guide

**Welcome to the AWS Deployment Kit Portfolio Builder!** 🎉

This guide will walk you through creating and deploying a professional portfolio website to AWS - even if you've never done this before.

---

## 🎯 What You'll Get

By the end of this guide, you'll have:
- ✅ A professional portfolio website showcasing your skills and projects
- ✅ Hosted on AWS with global CDN (CloudFront)
- ✅ Secure HTTPS connection
- ✅ Live on the internet in ~20 minutes
- ✅ Costs less than $1/month (or free with AWS free tier)

---

## 📋 Prerequisites

Before starting, make sure you have:
- [ ] AWS account (free to create at [aws.amazon.com](https://aws.amazon.com))
- [ ] AWS CLI installed and configured
- [ ] This deployment kit downloaded
- [ ] 20-30 minutes of time

**Don't have AWS CLI set up?** Run this first:
```bash
cd aws-deployment-kit
./scripts/bootstrap.sh
```

---

## 🚀 Quick Start (3 Steps)

### Step 1: Fill Out Your Information (10 min)

Open and complete the questionnaire:
```bash
open PORTFOLIO_QUESTIONNAIRE.md
```

**What to include:**
- Your name and professional title
- Social media links (LinkedIn, GitHub, etc.)
- Professional summary (2-3 paragraphs about you)
- Key skills and certifications
- 2-5 projects you want to showcase
- Optional: Talks, podcasts, blog posts

**Pro Tip:** You don't need to fill out everything - just the basics will create a great site!

---

### Step 2: Tell Me You're Ready (1 min)

Once you've filled out the questionnaire, just say:

**"I'm ready to build my portfolio!"**

I'll then:
1. Read your questionnaire
2. Create a beautiful, professional portfolio website
3. Set up the project structure
4. Make it ready to deploy

This takes about 2 minutes.

---

### Step 3: Deploy to AWS (15 min)

I'll guide you through deploying to AWS:

1. **Create AWS infrastructure** (~12 min, mostly waiting)
   - S3 bucket for your files
   - CloudFront CDN for fast global delivery
   - Security configurations

2. **Deploy your website** (~2 min)
   - Upload your portfolio
   - Invalidate cache
   - Get your live URL

3. **You're live!** 🎉
   - Share your CloudFront URL
   - (Optional) Add custom domain later

---

## 📁 What Gets Created

Your portfolio will include:

### Pages
- **Home/About** - Your professional summary and photo
- **Skills** - Technical skills organized by category
- **Projects** - Showcase your best work with descriptions
- **Experience** - Certifications and achievements
- **Contact** - Links to reach you

### Features
- ✅ Responsive design (looks great on mobile)
- ✅ Professional styling
- ✅ Fast loading (optimized)
- ✅ SEO friendly
- ✅ Resume download button (if you provide PDF)
- ✅ Social media links
- ✅ Project showcases with GitHub links

---

## 🎨 Customization Options

### Design Themes

Choose from:
- **Professional Blue** (default) - Clean, corporate look
- **Dark Mode** - Modern tech aesthetic
- **Minimal** - Simple black and white
- **Custom** - Specify your own colors

Just mention your preference in the questionnaire!

---

## 💰 Cost Breakdown

### First 12 Months (AWS Free Tier)
- S3 Storage: **FREE** (5 GB included)
- CloudFront: **FREE** (1 TB transfer included)
- **Total: $0/month** ✨

### After Free Tier
- Small portfolio: **~$0.10-0.50/month**
- With custom domain: **~$1-2/month**

**Much cheaper than traditional hosting!**

---

## 🔄 Making Updates

Want to update your portfolio later?

1. **Edit your files** - Make changes locally
2. **Redeploy** - Run one command:
   ```bash
   ./scripts/deploy.sh <bucket-name> <distribution-id>
   ```
3. **Live in 1-2 minutes** - That's it!

You can update as often as you want!

---

## 🆚 CloudFront URL vs Custom Domain

### Starting with CloudFront URL (Recommended)

**Pros:**
- ✅ Free - no domain purchase needed
- ✅ Fast setup - live in 15 minutes
- ✅ Perfect for testing and learning
- ✅ Can add custom domain later

**Cons:**
- ❌ URL is not memorable (e.g., `d123abc.cloudfront.net`)
- ❌ Less professional looking

**Best for:** Testing, learning, temporary sites

---

### Upgrading to Custom Domain (Optional)

**Pros:**
- ✅ Professional URL (e.g., `yourname.com`)
- ✅ Better for sharing and branding
- ✅ Looks more professional

**Cons:**
- ❌ Costs $10-15/year for domain
- ❌ Takes 30-40 minutes to set up (DNS propagation)
- ❌ Additional $0.50/month for Route 53

**Best for:** Professional portfolios, long-term sites

**You can start with CloudFront and upgrade later!**

---

## 📖 Step-by-Step Walkthrough

### Phase 1: Preparation (10 min)

1. **Open the questionnaire:**
   ```bash
   open PORTFOLIO_QUESTIONNAIRE.md
   ```

2. **Fill out your information:**
   - Start with the basics (name, title, summary)
   - Add your social links
   - List your key skills
   - Describe 2-3 projects
   - Add certifications if you have them

3. **Optional - Add your resume:**
   - Save your resume as `resume.pdf`
   - Place it in the project directory
   - I'll add a download button automatically

4. **Save the file** when done

---

### Phase 2: Build Your Site (2 min)

1. **Tell me you're ready:**
   - Just say: "I'm ready to build!"
   - Or: "Let's create my portfolio!"

2. **I'll create your site:**
   - Generate HTML/CSS based on your info
   - Create professional layout
   - Optimize for performance
   - Set up project structure

3. **Review (optional):**
   - I'll show you what was created
   - You can request changes
   - Or proceed to deployment

---

### Phase 3: Deploy to AWS (15 min)

1. **Create infrastructure:**
   ```bash
   aws cloudformation create-stack \
     --stack-name my-portfolio \
     --template-body file://cloudformation/website-infrastructure-no-domain.yaml \
     --parameters ParameterKey=ProjectName,ParameterValue=my-portfolio \
     --region us-east-1 \
     --profile build
   ```
   
   ⏳ **Wait ~12 minutes** (CloudFront takes time to deploy globally)

2. **Get your deployment info:**
   ```bash
   aws cloudformation describe-stacks \
     --stack-name my-portfolio \
     --region us-east-1 \
     --profile build \
     --query 'Stacks[0].Outputs'
   ```
   
   📝 **Save these values:**
   - Bucket name
   - Distribution ID
   - CloudFront URL (your website address!)

3. **Deploy your site:**
   ```bash
   ./scripts/deploy.sh <bucket-name> <distribution-id> build
   ```
   
   ⏳ **Wait ~1-2 minutes** for cache invalidation

4. **Visit your site!** 🎉
   - Open the CloudFront URL in your browser
   - Your portfolio is live!

---

## 🎓 What You're Learning

By completing this process, you'll learn:
- ✅ How to deploy websites to AWS
- ✅ CloudFormation (Infrastructure as Code)
- ✅ S3 for static website hosting
- ✅ CloudFront CDN for global delivery
- ✅ AWS CLI basics
- ✅ Cache invalidation
- ✅ HTTPS and security best practices

**These are valuable professional skills!**

---

## 🆘 Troubleshooting

### "I don't have AWS CLI configured"
Run the bootstrap script:
```bash
cd aws-deployment-kit
./scripts/bootstrap.sh
```

### "Stack creation failed"
Check the error:
```bash
aws cloudformation describe-stack-events \
  --stack-name my-portfolio \
  --region us-east-1 \
  --max-items 10
```

Common fixes:
- Make sure you're using `us-east-1` region
- Check your AWS credentials are valid
- Ensure you have proper IAM permissions

### "Website shows Access Denied"
- Wait 2-3 minutes after deployment
- Hard refresh your browser (Cmd+Shift+R or Ctrl+Shift+R)
- Check that files uploaded to S3

### "Changes aren't showing"
- Wait 1-2 minutes for cache invalidation
- Hard refresh browser
- Check invalidation status

### Need more help?
See [TESTING_GUIDE.md](TESTING_GUIDE.md) for detailed troubleshooting.

---

## 💡 Pro Tips

1. **Start simple** - You can always add more later
2. **Use good photos** - Professional headshot makes a difference
3. **Show, don't tell** - Projects with links are more impressive
4. **Keep it updated** - Redeploy when you have new projects
5. **Test on mobile** - Most visitors will view on phones
6. **Get feedback** - Share with friends before going public
7. **Add analytics** - Consider Google Analytics later

---

## 🎯 Success Checklist

Before you start:
- [ ] AWS account created
- [ ] AWS CLI configured with profile
- [ ] Questionnaire downloaded
- [ ] 20-30 minutes available

After completion:
- [ ] Questionnaire filled out
- [ ] Portfolio site created
- [ ] AWS infrastructure deployed
- [ ] Website uploaded and live
- [ ] CloudFront URL working
- [ ] Shared with someone! 🎉

---

## 🚀 Ready to Start?

**Here's what to do right now:**

1. Open the questionnaire:
   ```bash
   open PORTFOLIO_QUESTIONNAIRE.md
   ```

2. Fill it out (take your time!)

3. Come back and say: **"I'm ready to build!"**

That's it! I'll handle the rest. 

---

## 📚 Additional Resources

- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Detailed deployment guide
- **[QUICK_START.md](QUICK_START.md)** - 5-minute reference
- **[GUIDE.md](GUIDE.md)** - Complete tutorial
- **[FAQ.md](FAQ.md)** - Common questions

---

## 🌟 Example Portfolios

Here's what others have built:

**GRC Engineer Portfolio:**
- Professional summary highlighting compliance expertise
- Projects: SOC 2 automation, AWS security architecture
- Certifications: AWS Security Specialty, CISSP
- Blog posts and conference talks
- Resume download button

**Cloud Security Engineer:**
- Dark mode design
- Focus on AWS and security tools
- GitHub projects with live demos
- Podcast appearances
- Contact form integration

**Your portfolio will be unique to you!**

---

## 🎉 Let's Build!

Ready to create your professional portfolio?

**Step 1:** Open `PORTFOLIO_QUESTIONNAIRE.md`  
**Step 2:** Fill it out  
**Step 3:** Say "I'm ready!"  

Let's make something awesome! 🚀
