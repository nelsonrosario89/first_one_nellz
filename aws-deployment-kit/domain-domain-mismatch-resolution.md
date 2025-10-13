# Custom Domain Configuration Summary

## Background
- **Issue:** The CloudFront distribution `DIST_ID_EXAMPLE` served the site from the default URL `https://example123.cloudfront.net`. When we tried adding the custom domain `example-portfolio.com`, CloudFront rejected the change because no matching Alternate Domain Names (CNAMEs) were configured, and the distribution had no SSL certificate covering that hostname.
- **Goal:** Point `example-portfolio.com` (and `www`) to the existing portfolio without breaking HTTPS, using the previously issued ACM certificate.

## Root Cause
- The distribution was still using the default CloudFront certificate, which only covers the `*.cloudfront.net` domain.
- Alternate Domain Names (CNAMEs) for `example-portfolio.com` and `www.example-portfolio.com` were missing.
- Route 53 lacked alias records mapping the custom domain to the CloudFront distribution.

## Resolution Steps
- **Verify domain registration email** in Route 53 to ensure the registrar record stays active.
- **Confirm ACM certificate** `arn:aws:acm:us-east-1:123456789012:certificate/EXAMPLE-CERT-ID` issued in `us-east-1` covers both the apex and `www` hostnames.
- **Update CloudFront distribution**:
  - Open distribution `DIST_ID_EXAMPLE` → *Edit*.
  - Add Alternate Domain Names: `example-portfolio.com` and `www.example-portfolio.com`.
  - Select the custom ACM certificate above under *Custom SSL certificate* and save. CloudFront redeployed with HTTPS enabled for the new hostnames.
- **Create Route 53 alias records** in the hosted zone `example-portfolio.com`:
  - `A` (alias) pointing the apex to distribution `DIST_ID_EXAMPLE`.
  - `A` (alias) with name `www` pointing to the same distribution.
  - Optional `AAAA` alias records were also added for IPv6 coverage.
- **Validate deployment:** After propagation (~15 minutes), the site resolved at `https://example-portfolio.com` with a valid padlock, and the resume download continued to work.

## Outcome
The portfolio now loads securely on the custom domain, and both the apex and `www` hostnames share the same CloudFront distribution and ACM certificate.
