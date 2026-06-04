# Cloudflare Setup & Configuration Guide

## Cloudflare Services Used

1. **DNS Management** - Domain nameservers
2. **CDN** - Global content delivery
3. **Web Application Firewall (WAF)** - Security
4. **DDoS Protection** - Free tier included
5. **R2 Storage** - Media file hosting
6. **SSL/TLS** - HTTPS certificates
7. **Page Rules** - Caching and performance
8. **Workers** - Serverless functions (optional)

## Step 1: Add Domain to Cloudflare

### 1.1 Transfer Domain or Add Nameservers

**Option A: Transfer domain to Cloudflare** (recommended)
1. Go to https://dash.cloudflare.com
2. Click "Add a site"
3. Enter your domain: `techsphere.dev`
4. Select Free plan
5. Follow domain transfer instructions

**Option B: Keep domain registrar, update nameservers**
1. Log into your domain registrar
2. Update nameservers to Cloudflare's:
   - `doug.ns.cloudflare.com`
   - `jessica.ns.cloudflare.com`
3. Wait 24 hours for propagation

### 1.2 Verify Domain Ownership

1. Go to Cloudflare dashboard
2. Select your domain
3. Add CNAME or TXT record for verification
4. Wait for verification to complete

## Step 2: Configure DNS Records

### 2.1 Set Up A Records for Main Site

Create DNS records in Cloudflare dashboard:

| Type | Name | Content | TTL | Proxied |
|------|------|---------|-----|---------|
| A | @ | 216.239.38.21 | Auto | Proxied ☁️ |
| CNAME | www | techsphere.dev | Auto | Proxied ☁️ |

Replace `216.239.38.21` with Railway's IP or domain.

### 2.2 Set Up CNAME Records for Services

| Type | Name | Content | TTL | Proxied |
|------|------|---------|-----|---------|
| CNAME | api | techsphere.dev | Auto | Proxied ☁️ |
| CNAME | cdn | techsphere.dev | Auto | Proxied ☁️ |
| CNAME | admin | techsphere.dev | Auto | Proxied ☁️ |

### 2.3 Set Up Media Subdomain for R2

```
Type: CNAME
Name: media
Content: techsphere-media.techsphere.r2.cloudflarestorage.com
TTL: Auto
Proxied: Proxied ☁️
```

This makes media files load through Cloudflare's CDN.

### 2.4 Email Records (if using email)

```
Type: MX
Name: @
Content: mail.protonmail.ch
Priority: 10
TTL: Auto
Proxied: DNS only

Type: TXT
Name: @
Content: v=spf1 include:protonmail.com ~all
TTL: Auto
```

## Step 3: SSL/TLS Configuration

### 3.1 Set SSL Mode

1. Go to SSL/TLS tab in Cloudflare
2. Select "Full (strict)" mode
3. This requires Railway to have valid SSL certificate (included)

### 3.2 Enable Automatic HTTPS Rewrites

1. SSL/TLS > Edge Certificates
2. Enable "Always use HTTPS"
3. Enable "Automatic HTTPS Rewrites"

### 3.3 Add Custom SSL Certificate (Optional)

For advanced setups:
1. SSL/TLS > Custom Certificates
2. Upload your certificate and private key
3. Or let Cloudflare manage it

### 3.4 Enable Minimum TLS Version

1. SSL/TLS > Edge Certificates
2. Set "Minimum TLS Version" to TLS 1.2
3. This ensures only modern clients can connect

## Step 4: Web Application Firewall (WAF)

### 4.1 Enable Managed Rulesets

1. Go to Security > WAF
2. Enable these rulesets:
   - Cloudflare Managed Ruleset
   - OWASP Managed Ruleset
   - Cloudflare Free Managed Ruleset

### 4.2 Create Custom WAF Rules

**Rate Limiting Rule:**
```
Field: Request Rate
Operator: greater than
Value: 100 (requests per 10 seconds)
Action: Challenge (CAPTCHA)
```

**Bot Management (Free tier):**
```
Field: Bot Score
Operator: less than
Value: 30
Action: Challenge
```

### 4.3 Configure WAF Sensitivity

1. Security > WAF
2. Set sensitivity level to "Medium" or "High"
3. Low = fewer false positives but less protection
4. High = more protection but more legitimate traffic blocked

## Step 5: Performance Optimization

### 5.1 Caching Rules

**Cache Everything:**
```
URL: /
Cache Level: Cache Everything
Browser Cache TTL: 30 minutes
```

**Cache Static Assets:**
```
URL: /static/*
Cache Level: Cache Everything
Browser Cache TTL: 1 year
```

**Cache Media:**
```
URL: /media/*
Cache Level: Cache Everything
Browser Cache TTL: 30 days
```

**Don't Cache API:**
```
URL: /api/*
Cache Level: Bypass
```

### 5.2 Enable Automatic Compression

1. Speed > Optimization
2. Enable all compression options:
   - Gzip compression
   - Brotli compression
   - Minify JavaScript
   - Minify CSS
   - Minify HTML

### 5.3 Enable Caching for File Extensions

1. Speed > Caching > Cache Rules
2. Ensure these are cached:
   ```
   .jpg, .jpeg, .png, .gif, .ico, .svg
   .css, .js, .woff, .woff2, .ttf
   .pdf, .zip, .rar, .zip
   ```

## Step 6: DDoS & Security

### 6.1 DDoS Protection Level

1. Go to Security > DDoS
2. Set DDoS Sensitivity to "High"
3. This is automatic in Cloudflare free tier

### 6.2 Security Headers

1. Security > Security Headers
2. Enable:
   - HSTS (HTTP Strict Transport Security)
   - X-Frame-Options: DENY
   - X-Content-Type-Options: nosniff
   - X-XSS-Protection: 1; mode=block

### 6.3 Bot Management

1. Security > Bot Management
2. Set Super Bot Fight Mode to "Definitely Automated"
3. This blocks obvious bots

### 6.4 IP Reputation

1. Security > Security Settings
2. Enable "IP Reputation Database"
3. Set "Challenge (Captcha)" for "High" reputation threats

## Step 7: Cloudflare R2 Configuration

### 7.1 Create R2 Bucket

1. Cloudflare Dashboard > R2 Storage
2. Click "Create bucket"
3. Name: `techsphere-media`
4. Click "Create bucket"

### 7.2 Configure CORS

Create file `cors.json`:
```json
{
  "CORSRules": [
    {
      "AllowedOrigins": [
        "https://techsphere.dev",
        "https://www.techsphere.dev"
      ],
      "AllowedMethods": ["GET", "HEAD", "PUT", "POST", "DELETE"],
      "AllowedHeaders": ["*"],
      "ExposeHeaders": ["ETag"],
      "MaxAgeSeconds": 3000
    }
  ]
}
```

Apply with AWS CLI:
```bash
aws --profile r2 s3api put-bucket-cors \
  --bucket techsphere-media \
  --cors-configuration file://cors.json \
  --endpoint-url https://[account-id].r2.cloudflarestorage.com
```

### 7.3 Set Up Custom Domain for R2

1. R2 > techsphere-media bucket
2. Settings > Custom Domain
3. Enter: `media.techsphere.dev`
4. Cloudflare automatically creates CNAME

### 7.4 Configure R2 Bucket Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::techsphere-media/*"
    }
  ]
}
```

This allows public read access to media files.

## Step 8: Monitoring & Analytics

### 8.1 Enable Cloudflare Analytics

1. Dashboard > Overview
2. View real-time analytics:
   - Requests (total and by status code)
   - Bandwidth usage
   - Cache performance
   - Threats blocked

### 8.2 Set Up Web Analytics

1. Analytics > Web Analytics
2. Embed Cloudflare Web Analytics snippet (optional)
3. View privacy-friendly analytics (no cookies)

### 8.3 Create Custom Dashboards

1. Analytics > Dashboards
2. Create custom dashboard with:
   - Cache hit ratio
   - Response time
   - Error rate (4xx/5xx)
   - Bandwidth by country
   - Top pages

## Step 9: Page Rules (Advanced)

### 9.1 Cache Rules

**Example 1: Cache API responses**
```
URL: techsphere.dev/api/*
Page Rule: Cache Level = Cache Everything
```

**Example 2: Bypass cache for admin**
```
URL: techsphere.dev/admin/*
Page Rule: Cache Level = Bypass
```

**Example 3: Long-lived asset caching**
```
URL: techsphere.dev/static/*
Page Rule: Browser Cache TTL = 1 year
Page Rule: Cache Level = Cache Everything
```

### 9.2 Security Rules

**Block specific countries** (if needed):
```
URL: techsphere.dev/*
Page Rule: Security Level = Under Attack (if needed)
```

## Step 10: Monitoring & Alerts

### 10.1 Email Alerts

1. Notifications > Notification Settings
2. Enable alerts for:
   - High rate of errors
   - DDoS attack
   - Certificate renewal
   - Billing notifications

### 10.2 Webhook Alerts

1. Notifications > Notification Settings
2. Set up webhook to Sentry or Slack
3. Send alerts to: `https://your-webhook.endpoint`

## Step 11: Workers (Optional - Advanced)

### 11.1 Simple Worker for Analytics

Create `analytics.js` worker:

```javascript
export default {
  async fetch(request) {
    // Log request info
    console.log({
      method: request.method,
      url: request.url,
      country: request.headers.get('cf-ipcountry'),
      timestamp: new Date().toISOString()
    });
    
    // Pass through to origin
    return fetch(request);
  }
}
```

Deploy in Cloudflare dashboard.

## Cloudflare Settings Summary

### Recommended Free Tier Configuration

```
DNS Mode: Nameserver (or CNAME)
SSL/TLS Mode: Full (strict)
Caching: Aggressive
Compression: Gzip + Brotli
DDoS Protection: High
Bot Management: Definitely Automated
WAF: Managed Rules enabled
Rate Limiting: 100 req/10s
Minimum TLS: 1.2
HSTS: Enabled (1 year)
Auto HTTPS Rewrites: Enabled
```

## Cost Analysis

**Free Tier Includes:**
- Unlimited requests
- Global CDN
- DDoS protection
- WAF
- 10M requests/day
- All the above features

**Optional Premium:**
- Advanced WAF Rules: $200/month
- Advanced Bot Management: $200/month+
- Rate Limiting: $20/month+

**R2 Storage Pricing:**
- Storage: $0.015/GB/month
- Requests: $0.36 per million reads
- No egress charges (unlike S3)

## Troubleshooting

### Issue: High Latency

**Solution:**
1. Check cache hit ratio (Analytics tab)
2. Enable compression if disabled
3. Move origin closer to Cloudflare datacenter
4. Clear cache and rebuild

### Issue: Blank Pages

**Solution:**
1. Verify SSL certificate is valid
2. Check origin is responding
3. Disable WAF rules temporarily to test
4. Check browser console for CORS errors

### Issue: Media Files Not Loading

**Solution:**
1. Verify R2 bucket CORS configured
2. Check R2 custom domain CNAME
3. Verify bucket policy allows public read
4. Test direct R2 URL access

### Issue: API Rate Limiting

**Solution:**
1. Adjust rate limiting rules
2. Use Cloudflare Transforms to add headers
3. Set up bypass for authenticated users
4. Implement queue for legitimate high-volume traffic

## Best Practices

1. **Keep cache fresh**: Purge cache after deployments
2. **Monitor WAF**: Review blocked requests weekly
3. **Update SSL**: Auto-renewal enabled (recommended)
4. **Security headers**: Set proper headers in Django
5. **Rate limiting**: Balance protection vs. user experience
6. **Backup DNS**: Keep secondary DNS provider as backup
7. **Monitor costs**: R2 egress can add up
8. **Regular backups**: Export DNS records regularly

## Security Checklist

- [ ] SSL/TLS mode set to "Full (strict)"
- [ ] HTTPS redirect enabled
- [ ] HSTS header enabled
- [ ] WAF managed rules enabled
- [ ] Rate limiting configured
- [ ] DDoS protection set to High
- [ ] Bot management enabled
- [ ] Security headers enabled
- [ ] X-Frame-Options set
- [ ] Email alerts configured
- [ ] IP reputation enabled
- [ ] Minimum TLS version 1.2

## Next Steps

1. Configure DNS records
2. Set up SSL/TLS
3. Enable WAF and security rules
4. Configure R2 for media
5. Enable caching rules
6. Set up monitoring
7. Test security headers
8. Create monitoring dashboard
9. Set up email alerts
10. Document your configuration

## Resources

- Cloudflare Dashboard: https://dash.cloudflare.com
- Documentation: https://developers.cloudflare.com
- Community: https://community.cloudflare.com
- Status Page: https://www.cloudflarestatus.com
