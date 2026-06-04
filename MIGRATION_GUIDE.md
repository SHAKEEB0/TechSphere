# Complete Migration Guide: From Render to Railway

## Overview

This guide provides step-by-step instructions to migrate TechSphere from Render to a modern, cost-effective stack using:
- **Railway** for application hosting
- **Neon PostgreSQL** for database
- **Cloudflare R2** for media storage
- **Cloudflare** for CDN and security
- **GitHub Actions** for CI/CD

## Phase 1: Pre-Migration Preparation (1-2 days)

### 1.1 Sign Up for Required Services

#### Railway
1. Visit https://railway.app
2. Sign up with GitHub account
3. Link your GitHub repository
4. Create a new project

#### Neon PostgreSQL
1. Visit https://neon.tech
2. Sign up with GitHub or email
3. Create a new project (region: us-east-1 recommended for US)
4. Note the connection string (Connection pooling enabled by default)

#### Cloudflare R2
1. Visit https://dash.cloudflare.com
2. Sign up (if not already have account)
3. Navigate to R2 storage
4. Create a new bucket: `techsphere-media`
5. Create API token with R2 permissions

#### Sentry (Optional but recommended)
1. Visit https://sentry.io
2. Create an account
3. Create a new Django project
4. Copy the DSN

### 1.2 Gather Current Data

#### Export Current Database from Render

```bash
# Get Render database connection info from Render dashboard

# Option 1: Using pg_dump
pg_dump -h [render-db-host] \
        -U [username] \
        -d [database] \
        --no-acl \
        --no-owner \
        > techsphere-backup.sql

# Option 2: Using Render dashboard
# Render Dashboard > Databases > [Your DB] > Connect > Download backup
```

#### Export Media Files from Render

```bash
# If using Render's file storage
rsync -av [render-app]:/opt/render/project/src/media/ ./media-backup/

# If using S3/R2 bucket
aws s3 sync s3://render-bucket/media/ ./media-backup/ --profile default
```

### 1.3 Prepare Environment Configuration

1. Copy `.env.example` to `.env` in your local repository
2. Fill in all required values (see Environment Variables section below)
3. Never commit `.env` to version control

## Phase 2: Database Migration (1 day)

### 2.1 Create Neon PostgreSQL Database

```bash
# Get connection info from Neon dashboard
# Connection string format:
# postgresql://user:password@host/database

# Test connection locally
psql "postgresql://user:password@host/database" -c "SELECT version();"
```

### 2.2 Import Data to Neon

#### Option A: Direct Import (Recommended for smaller databases)

```bash
# Connect to Neon and import SQL dump
psql "postgresql://user:password@host/database" < techsphere-backup.sql

# Verify import
psql "postgresql://user:password@host/database" -c "\dt"
```

#### Option B: Django Dump & Load (Recommended for larger databases)

```bash
# On local machine with access to Render database
export DATABASE_URL=postgresql://render-user:password@render-host/database

# Dump using Django
python manage.py dumpdata --natural-foreign --indent 2 > techsphere-fixture.json

# Import to Neon
export DATABASE_URL=postgresql://neon-user:password@neon-host/database
python manage.py migrate --noinput
python manage.py loaddata techsphere-fixture.json
```

### 2.3 Verify Data Integrity

```bash
# Check table counts
python manage.py shell
>>> from django.db import connection
>>> from apps.blog.models import Post, Category
>>> print(f"Posts: {Post.objects.count()}")
>>> print(f"Categories: {Category.objects.count()}")
>>> print(f"All tables: {len([name for name in connection.introspection.table_names()])}")

# Check specific data
Post.objects.all()[:5]
```

## Phase 3: Media Migration to Cloudflare R2 (1 day)

### 3.1 Set Up AWS CLI for R2

```bash
# Install AWS CLI if not already installed
pip install awscli

# Configure AWS CLI for R2
aws configure --profile r2

# When prompted:
# AWS Access Key ID: [R2 API Token Access Key]
# AWS Secret Access Key: [R2 API Token Secret Key]
# Default region name: auto
# Default output format: json
```

### 3.2 Upload Media to R2

```bash
# Create the bucket (if not exists)
aws --profile r2 s3api create-bucket \
    --bucket techsphere-media \
    --region auto \
    --endpoint-url https://[account-id].r2.cloudflarestorage.com

# Upload media files
aws --profile r2 s3 sync ./media-backup/ s3://techsphere-media/ \
    --endpoint-url https://[account-id].r2.cloudflarestorage.com \
    --acl private \
    --storage-class STANDARD

# Verify upload
aws --profile r2 s3 ls s3://techsphere-media/ \
    --endpoint-url https://[account-id].r2.cloudflarestorage.com \
    --recursive
```

### 3.3 Update Django Media URLs

```bash
# For each media file, update the database URL from local path to R2 URL

python manage.py shell

>>> from django.db import connection
>>> cursor = connection.cursor()
>>> 
>>> # Update all media URLs in Post model
>>> UPDATE posts set featured_image = CONCAT('https://media.techsphere.dev/', featured_image) 
>>> WHERE featured_image NOT LIKE 'https://%'

# Or use Django ORM:
>>> from apps.blog.models import Post
>>> for post in Post.objects.filter(featured_image__startswith='uploads/'):
>>>     new_url = f"https://media.techsphere.dev/{post.featured_image}"
>>>     post.featured_image = new_url
>>>     post.save()
```

## Phase 4: Infrastructure Setup (1 day)

### 4.1 Configure Cloudflare DNS

1. Log into Cloudflare dashboard
2. Add your domain (or use existing)
3. Update nameservers at your domain registrar to Cloudflare nameservers
4. Wait for DNS propagation (up to 24 hours)
5. In Cloudflare Dashboard:
   - Create A record pointing to Railway's domain
   - Create CNAME for media.techsphere.dev pointing to R2 bucket
   - Set SSL/TLS to "Flexible" initially, then "Full" after Railway is set up

### 4.2 Configure Railway

1. Open Railway dashboard for your project
2. Add environment variables:

```bash
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=[generate new one]
DJANGO_ALLOWED_HOSTS=techsphere.dev www.techsphere.dev railway.app
DATABASE_URL=[from Neon]
REDIS_URL=[Railway Redis URL - will be set automatically]
USE_R2=True
R2_ACCESS_KEY_ID=[from R2]
R2_SECRET_ACCESS_KEY=[from R2]
R2_BUCKET_NAME=techsphere-media
R2_ENDPOINT_URL=https://[account-id].r2.cloudflarestorage.com
R2_CUSTOM_DOMAIN=https://media.techsphere.dev
GOOGLE_ANALYTICS_ID=[your GA4 ID]
GOOGLE_ADSENSE_CLIENT_ID=[your Adsense ID]
SENTRY_DSN=[from Sentry]
SENTRY_ENABLED=True
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
EMAIL_HOST=[gmail or your provider]
EMAIL_PORT=587
EMAIL_HOST_USER=[your email]
EMAIL_HOST_PASSWORD=[app password]
DEFAULT_FROM_EMAIL=noreply@techsphere.dev
```

3. Connect GitHub repository to Railway
4. Configure build and deployment settings

### 4.3 Configure Cloudflare WAF

1. In Cloudflare Dashboard > Security > WAF
2. Enable all protection levels
3. Create custom rules:
   - Rate limiting: 1000 requests/10 minutes
   - DDoS protection: enabled
   - Bot management: Definitely automated

### 4.4 Set Up R2 CORS Headers

```bash
# Create CORS configuration
cat > cors.json << EOF
{
  "CORSRules": [
    {
      "AllowedOrigins": ["https://techsphere.dev", "https://www.techsphere.dev"],
      "AllowedMethods": ["GET", "HEAD"],
      "AllowedHeaders": ["*"],
      "MaxAgeSeconds": 3000
    }
  ]
}
EOF

# Apply to bucket
aws --profile r2 s3api put-bucket-cors \
    --bucket techsphere-media \
    --cors-configuration file://cors.json \
    --endpoint-url https://[account-id].r2.cloudflarestorage.com
```

## Phase 5: Deployment Preparation (1 day)

### 5.1 Update Django Settings

1. Create `techsphere/settings_production.py` (already created)
2. Ensure all environment variables are properly read
3. Test settings with `python manage.py check --deploy`

### 5.2 Set Up GitHub Actions

1. Create GitHub repository secrets:

```bash
RAILWAY_TOKEN=[from Railway dashboard]
SENTRY_DSN=[from Sentry]
```

2. Ensure `.github/workflows/ci-cd.yml` is in place

### 5.3 Test Locally with Production Config

```bash
# Create local test environment
cp .env.example .env.local

# Edit .env.local with test values
# Run with production settings
DJANGO_SETTINGS_MODULE=techsphere.settings_production \
DJANGO_DEBUG=False \
python manage.py check --deploy

# Run migrations test
DJANGO_SETTINGS_MODULE=techsphere.settings_production \
python manage.py migrate --plan

# Run static files collection test
DJANGO_SETTINGS_MODULE=techsphere.settings_production \
python manage.py collectstatic --noinput --dry-run
```

### 5.4 Build Docker Image Locally

```bash
# Build image
docker build -t techsphere:latest .

# Test image
docker run --rm -it \
    -e DATABASE_URL=postgresql://... \
    -e DJANGO_SECRET_KEY=test \
    -e DJANGO_DEBUG=False \
    techsphere:latest \
    python manage.py check
```

## Phase 6: Cutover (4-8 hours)

### 6.1 Final Verification

```bash
# Before starting cutover:

# 1. Verify Railway deployment is ready
# Check Railway dashboard - should show green status

# 2. Run smoke tests
curl https://techsphere.dev/health/

# 3. Verify database connection
python manage.py shell < scripts/db_check.py

# 4. Check media access
curl https://media.techsphere.dev/[sample-file-path]

# 5. Verify SSL certificate
curl -vI https://techsphere.dev
```

### 6.2 DNS Cutover

1. Keep Render running (as backup)
2. Update Cloudflare A record to point to Railway domain
3. Test DNS resolution:

```bash
nslookup techsphere.dev
# Should show Railway IP

# Test with curl
curl -H "Host: techsphere.dev" https://railway-url
```

4. Monitor error logs for next 1 hour

### 6.3 Update DNS/SSL Records

```bash
# Update in DNS provider or Cloudflare:
# A record: techsphere.dev → Railway IP
# CNAME: www → techsphere.dev
# CNAME: media → R2 bucket
# TXT: For SSL verification (if needed)
```

### 6.4 Monitoring During Cutover

```bash
# Watch Railway logs
railway logs -f

# Watch error tracking (Sentry)
# Visit https://sentry.io/issues

# Monitor uptime and latency
# Use https://uptimerobot.com (free tier)

# Check Google Analytics
# Watch real-time user access
```

## Phase 7: Post-Cutover (2-4 hours)

### 7.1 Verification Tests

```bash
# 1. Test all website features
# - Homepage loads
# - Blog posts display
# - Images load from R2
# - Search functionality works
# - Comment submission works
# - Newsletter signup works

# 2. Database queries
python manage.py shell
>>> from apps.blog.models import Post
>>> Post.objects.count()
>>> from apps.newsletter.models import NewsletterSubscriber
>>> NewsletterSubscriber.objects.count()

# 3. Background tasks (Celery)
python manage.py celery inspect active

# 4. Email delivery test
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])

# 5. Cache functionality
python manage.py shell
>>> from django.core.cache import cache
>>> cache.set('test', 'value', 60)
>>> cache.get('test')
```

### 7.2 Monitor for Issues

```
# Key metrics to watch for first 24 hours:
- Error rate (should be < 0.1%)
- Response time (should be < 500ms)
- Database connection pool (should be healthy)
- Cache hit rate (should be > 50%)
- Memory usage (should be stable)
```

### 7.3 Keep Render as Backup

```bash
# Keep Render running for 24-48 hours
# Continue monitoring Railway for any issues
# If critical issues arise:
#   1. Keep Railway running
#   2. Switch DNS back to Render (A record)
#   3. Investigate and fix issues
#   4. Switch DNS back to Railway

# After 48 hours of stable operation:
# 1. Verify no requests hitting Render
# 2. Scale down Render resources to minimum
# 3. Create backup from Render (as archive)
# 4. Keep Render for 1 week as disaster recovery
# 5. Finally decommission Render
```

## Phase 8: Cleanup (1 day after verification)

### 8.1 Remove Render Resources

```bash
# From Render Dashboard:
1. Delete web service
2. Delete database
3. Cancel Render subscription
4. Export final backup (if needed)
```

### 8.2 Optimize Railway Configuration

```bash
# Fine-tune resources based on actual usage
# Adjust worker count
# Optimize database connection pooling
# Review cost and adjust scaling policies
```

### 8.3 Archive Render Configuration

```bash
# Keep for future reference:
- render.yaml (for historical reference)
- Render database structure
- Any custom configurations
```

### 8.4 Update Documentation

```bash
# Update all documentation to reflect new setup:
- README.md
- DEPLOYMENT.md
- Architecture docs
- Team playbooks
```

## Rollback Procedure (If Needed)

### If Critical Issues Occur

```bash
# Option 1: Quick DNS Fallback to Render (5 minutes)
1. Log into Cloudflare
2. Edit A record for techsphere.dev
3. Point back to Render IP address
4. Save (propagates in < 1 minute)
5. Verify Render is serving traffic

# Option 2: Investigate Issue on Railway
1. Check Railway logs
2. Check database connectivity
3. Check environment variables
4. Review error tracking (Sentry)
5. Fix issue
6. Restart Railway service

# Option 3: Database Rollback
1. Restore from Neon backup (within 30 days)
2. Verify data integrity
3. Restart Rails application
```

## Environment Variables Reference

See `.env.example` for complete list of all environment variables needed.

Key variables for Railway deployment:
```
DATABASE_URL
REDIS_URL
DJANGO_SECRET_KEY
DJANGO_DEBUG
DJANGO_ALLOWED_HOSTS
USE_R2
R2_ACCESS_KEY_ID
R2_SECRET_ACCESS_KEY
R2_BUCKET_NAME
R2_ENDPOINT_URL
R2_CUSTOM_DOMAIN
GOOGLE_ANALYTICS_ID
SENTRY_DSN
EMAIL_HOST_USER
EMAIL_HOST_PASSWORD
```

## Support & Troubleshooting

### Common Issues and Solutions

#### 1. Database Connection Fails
```
Error: "could not connect to database server"

Solution:
- Verify DATABASE_URL is correct
- Check Neon connection limits
- Ensure Railway has access to Neon (IP whitelist)
- Test locally with psql
```

#### 2. Media Files Not Loading from R2
```
Error: 404 on media files

Solution:
- Verify R2 credentials
- Check R2_CUSTOM_DOMAIN is set correctly
- Verify Cloudflare CNAME record points to R2
- Test S3 access directly with AWS CLI
```

#### 3. Static Files Not Loading
```
Error: CSS/JS files return 404

Solution:
- Verify collectstatic ran
- Check STATIC_URL and STATIC_ROOT
- Verify Cloudflare cache is not stale
- Check whitenoise configuration
```

#### 4. Email Not Sending
```
Error: SMTPAuthenticationError

Solution:
- Verify EMAIL_HOST_USER and PASSWORD
- For Gmail: ensure App Password used (not regular password)
- Enable "Less secure apps" if needed
- Check email firewall rules
```

### Monitoring Tools

- **Railway Dashboard**: https://railway.app - App logs, metrics, deployments
- **Sentry**: https://sentry.io - Error tracking and performance
- **Neon Dashboard**: https://neon.tech - Database monitoring
- **Cloudflare Dashboard**: https://dash.cloudflare.com - CDN and WAF stats
- **Google Analytics**: https://analytics.google.com - User behavior
- **Uptime Robot**: https://uptimerobot.com - Uptime monitoring

## Cost Breakdown

### Monthly Costs Estimate (100K-500K monthly users)
```
Railway: $5-30
Neon PostgreSQL: $0-10
Cloudflare R2: $2-5
Cloudflare CDN/WAF: $0 (free tier)
Sentry: $0-29
GitHub Actions: $0-20
---
Total: ~$25-35/month
```

## Conclusion

You've successfully migrated from Render to a modern, scalable, cost-effective stack. Key benefits:

✓ 10x reduction in hosting costs
✓ Better performance with Cloudflare CDN
✓ Automatic scaling on Railway
✓ Advanced security with Cloudflare WAF
✓ Flexible media storage with R2
✓ Better error tracking with Sentry

For questions or issues, refer to the service documentation:
- Railway: https://docs.railway.app
- Neon: https://neon.tech/docs
- Cloudflare: https://developers.cloudflare.com
- Django: https://docs.djangoproject.com
