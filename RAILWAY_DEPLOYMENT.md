# Railway Deployment Guide

## Prerequisites

- GitHub account with TechSphere repository
- Railway account (https://railway.app)
- PostgreSQL database (Neon recommended)
- Redis instance (Railway provides one)
- Cloudflare R2 bucket (for media storage)
- Domain name with Cloudflare DNS

## Step 1: Create Railway Project

### 1.1 Connect GitHub Repository

1. Log into https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Authorize GitHub integration
5. Select your TechSphere repository
6. Choose a name: `TechSphere` or similar
7. Click "Deploy"

Railway will auto-detect the Dockerfile and start building.

### 1.2 Wait for Initial Build

- Railway will build the Docker image
- Initial build takes 5-15 minutes
- You can watch logs in real-time
- Don't worry if it fails initially (missing env vars expected)

## Step 2: Configure Environment Variables

### 2.1 Add Environment Variables in Railway

1. Go to your Railway project
2. Select the web service
3. Click "Variables"
4. Add all variables from `.env.example`:

```bash
# Core Django Settings
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=<generate-with-management-command>
DJANGO_ALLOWED_HOSTS=techsphere.dev www.techsphere.dev

# Database (get from Neon dashboard)
DATABASE_URL=postgresql://user:password@host/database

# Redis (Railway auto-creates this)
# REDIS_URL is automatically set by Railway

# Cloudflare R2
USE_R2=True
R2_ACCESS_KEY_ID=<your-r2-access-key>
R2_SECRET_ACCESS_KEY=<your-r2-secret>
R2_BUCKET_NAME=techsphere-media
R2_ENDPOINT_URL=https://<account-id>.r2.cloudflarestorage.com
R2_CUSTOM_DOMAIN=https://media.techsphere.dev

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=<your-email@gmail.com>
EMAIL_HOST_PASSWORD=<app-password>
DEFAULT_FROM_EMAIL=noreply@techsphere.dev

# Google Services
GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX
GOOGLE_ADSENSE_CLIENT_ID=ca-pub-xxxxxxxxx

# Sentry (Error Tracking)
SENTRY_ENABLED=True
SENTRY_DSN=https://examplekey@sentry.io/123456
SENTRY_TRACE_RATE=0.1

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000

# Site Configuration
SITE_URL=https://techsphere.dev
SITE_NAME=TechSphere
ENVIRONMENT=production
```

### 2.2 Using Railway CLI (Alternative)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Add environment variables
railway variables add \
  DJANGO_DEBUG=False \
  DJANGO_SECRET_KEY=your-key \
  DATABASE_URL=postgresql://...
```

## Step 3: Connect PostgreSQL Database

### Option A: Use Railway's Built-in PostgreSQL

1. In Railway project, click "+ Add Service"
2. Select "PostgreSQL"
3. This creates a database with auto-generated credentials
4. Railway automatically sets DATABASE_URL variable

### Option B: Use Neon PostgreSQL (Recommended)

1. Create account on https://neon.tech
2. Create a project (select region: us-east-1)
3. Copy connection string: `postgresql://user:password@host/database`
4. In Railway, set `DATABASE_URL` to this connection string

## Step 4: Add Redis Service

1. In Railway project, click "+ Add Service"
2. Select "Redis"
3. Railway automatically sets REDIS_URL environment variable
4. This is used for Celery tasks and caching

## Step 5: Configure Domain & SSL

### 5.1 Add Custom Domain in Railway

1. Go to Railway project > web service settings
2. Find "Domains" section
3. Click "Add Custom Domain"
4. Enter: `techsphere.dev`
5. Click "Add"

Railway will generate:
- A CNAME record you need to add to Cloudflare

### 5.2 Update Cloudflare DNS

1. Log into Cloudflare dashboard
2. Go to your domain's DNS settings
3. Create CNAME record:
   ```
   Name: techsphere.dev
   Type: CNAME
   Target: <railway-domain>.up.railway.app
   ```
4. For www subdomain:
   ```
   Name: www
   Type: CNAME
   Target: techsphere.dev
   ```

### 5.3 SSL Certificate

- Railway automatically provides SSL via Cloudflare
- Certificate is provisioned automatically
- Wait 10-15 minutes for full propagation

## Step 6: Deploy Application

### 6.1 Initial Deployment

1. Go to Railway project > Deployments
2. Click on the initial build (may have failed)
3. Click "Redeploy" 
4. Railway will:
   - Build Docker image
   - Run migrations
   - Collect static files
   - Start Gunicorn server

This takes 5-10 minutes.

### 6.2 Check Logs

1. Click the running deployment
2. Click "Logs" tab
3. Watch for any errors during startup
4. Look for "Successfully started" or "ready to accept connections"

### 6.3 Verify Deployment

```bash
# From terminal
curl https://techsphere.dev/
# Should return HTML of homepage

# Check health endpoint
curl https://techsphere.dev/health/
# Should return 200 OK
```

## Step 7: Run Migrations

### 7.1 One-Time Setup

If migrations didn't run automatically:

```bash
# Using Railway CLI
railway run python manage.py migrate --noinput

# Or via web dashboard:
# 1. Go to project > web service
# 2. Click "Shell" or similar
# 3. Run: python manage.py migrate --noinput
```

### 7.2 Create Superuser

```bash
railway run python manage.py createsuperuser

# Follow prompts:
# Username: admin
# Email: your-email@example.com
# Password: (strong password)
```

### 7.3 Collect Static Files

```bash
railway run python manage.py collectstatic --noinput
```

## Step 8: Configure Celery (Background Tasks)

### 8.1 Add Celery Worker Service

1. In Railway project, click "+ Add Service"
2. Select "GitHub Repo"
3. Select your TechSphere repo
4. Configure as separate service:
   - Name: `celery-worker`
   - Dockerfile path: `Dockerfile`
   - Command: `celery -A techsphere worker -l info`

### 8.2 Add Celery Beat (Scheduled Tasks)

1. Click "+ Add Service"
2. Select "GitHub Repo"
3. Select TechSphere
4. Configure:
   - Name: `celery-beat`
   - Dockerfile path: `Dockerfile`
   - Command: `celery -A techsphere beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler`

### 8.3 Configure Environment for Celery

Ensure these environment variables are set for all services:
```
CELERY_BROKER_URL=<REDIS_URL>
CELERY_RESULT_BACKEND=redis://...
```

## Step 9: Set Up Monitoring

### 9.1 Enable Sentry

1. Create Sentry account: https://sentry.io
2. Create Django project
3. Copy DSN
4. Set `SENTRY_DSN` in Railway environment variables
5. Set `SENTRY_ENABLED=True`

Sentry will now capture all errors automatically.

### 9.2 Railway Monitoring

Railway provides built-in monitoring:

1. Go to project > web service
2. Click "Metrics" tab
3. Monitor:
   - CPU usage
   - Memory usage
   - Network I/O
   - Error rate

## Step 10: Set Up Auto-Deployment with GitHub Actions

### 10.1 Create GitHub Secret

1. Go to GitHub repository
2. Settings > Secrets and variables > Actions
3. New repository secret:
   - Name: `RAILWAY_TOKEN`
   - Value: Get from Railway dashboard (Account > API Tokens)

### 10.2 GitHub Actions Workflow

The `.github/workflows/ci-cd.yml` file automatically:
- Runs tests on push
- Builds Docker image
- Deploys to Railway on main branch

### 10.3 Test Auto-Deployment

1. Make a small change to code
2. Push to main branch
3. Go to GitHub > Actions
4. Watch workflow run
5. Check Railway > Deployments for new deployment

## Step 11: Performance Optimization

### 11.1 Enable Caching

Railway automatically provides Redis. Cache is configured in settings.

To verify caching is working:

```bash
railway run python manage.py shell
>>> from django.core.cache import cache
>>> cache.set('test', 'value', 60)
>>> cache.get('test')
'value'
```

### 11.2 Scale Resources

For higher traffic:

1. Go to Railway project > web service > Settings
2. Under "Resources", adjust:
   - CPU: 0.5 to 2 (more = faster)
   - Memory: 1GB to 4GB
3. Cost scales with resources

### 11.3 Enable Auto-Scaling

1. In web service settings
2. Look for "Auto-scaling" section
3. Set minimum and maximum instances
4. Railway automatically scales based on CPU/Memory

## Step 12: Backup and Disaster Recovery

### 12.1 PostgreSQL Backups

If using Neon PostgreSQL:
- Neon handles automated backups
- 7-day retention by default
- Point-in-time recovery available
- Accessible via Neon dashboard

### 12.2 Media Backups

Cloudflare R2:
- No automatic backups (but R2 is reliable)
- Manual backup:
```bash
aws s3 sync s3://techsphere-media/ ./backup/ --profile r2
```

### 12.3 Database Backup Script

Create a scheduled backup:

```bash
# In GitHub Actions, add new workflow for daily backups:
# .github/workflows/backup.yml

name: Daily Database Backup
on:
  schedule:
    - cron: '0 2 * * *'  # 2 AM UTC daily

jobs:
  backup:
    runs-on: ubuntu-latest
    steps:
      - name: Run Database Backup
        run: |
          pg_dump "DATABASE_URL" > backup-$(date +%Y%m%d).sql
      
      - name: Upload to Storage
        run: |
          aws s3 cp backup-*.sql s3://backup-bucket/
```

## Troubleshooting

### Issue: Build Fails

```
Error: "Failed to build Docker image"

Solution:
1. Check Docker build logs
2. Verify Dockerfile is valid
3. Check requirements.txt for syntax errors
4. Test locally: docker build -t test .
```

### Issue: Database Connection Error

```
Error: "could not connect to server"

Solution:
1. Verify DATABASE_URL is correct
2. Check PostgreSQL is running
3. Verify IP whitelist (if applicable)
4. Test connection: railway run python manage.py shell
```

### Issue: Static Files Not Loading

```
Error: 404 on /static/...

Solution:
1. Run collectstatic: railway run python manage.py collectstatic
2. Verify STATIC_URL in settings
3. Check whitenoise is installed
4. Clear Cloudflare cache
```

### Issue: High Memory Usage

```
Solution:
1. Check for memory leaks in code
2. Reduce worker count
3. Clear cache: railway run python manage.py shell
4. Monitor with Railway metrics
```

## Production Checklist

Before going live, verify:

- [ ] Database connection is working
- [ ] Redis connection is working
- [ ] Static files are being served
- [ ] Media files loading from R2
- [ ] Emails sending successfully
- [ ] Error tracking (Sentry) is working
- [ ] SSL certificate is valid
- [ ] Domain DNS pointing to Railway
- [ ] Migrations have run
- [ ] Superuser created
- [ ] Caching is working
- [ ] Background tasks (Celery) working
- [ ] Monitoring is enabled
- [ ] Logs are being captured
- [ ] Backups are working

## Security Checklist

- [ ] DJANGO_DEBUG=False
- [ ] DJANGO_SECRET_KEY is strong (32+ chars, random)
- [ ] SECURE_SSL_REDIRECT=True
- [ ] SESSION_COOKIE_SECURE=True
- [ ] CSRF_COOKIE_SECURE=True
- [ ] ALLOWED_HOSTS properly configured
- [ ] Email credentials secured
- [ ] R2 credentials secured (never in code)
- [ ] Cloudflare WAF enabled
- [ ] Cloudflare rate limiting configured
- [ ] Sentry error tracking enabled
- [ ] Database credentials encrypted
- [ ] API keys not in version control

## Next Steps

1. Configure Cloudflare R2 for media storage
2. Set up custom domain with SSL
3. Configure email delivery
4. Set up error tracking with Sentry
5. Configure monitoring and alerts
6. Create backup procedures
7. Test disaster recovery
8. Configure CI/CD with GitHub Actions
9. Create runbooks for common issues
10. Set up status page for incidents

## Support

- Railway Documentation: https://docs.railway.app
- Railway Community: https://community.railway.app
- Django Documentation: https://docs.djangoproject.com
- PostgreSQL Documentation: https://www.postgresql.org/docs
