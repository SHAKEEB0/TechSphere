# TechSphere

TechSphere is a production-ready technology media platform built for blogging, learning, and monetization. It is designed for organic SEO growth, ad revenue, affiliate marketing, premium membership, and scalable infrastructure.

## Key Features

- Django 5 backend with Django REST Framework
- PostgreSQL database and Redis caching
- Celery task queue ready
- Bootstrap 5 + HTMX + Alpine.js frontend
- CKEditor 5 rich text editor integration
- Full-text search with PostgreSQL search vectors
- Custom user profiles, social login placeholders, and secure auth
- Post management with drafts, scheduled publishing, tags, categories, and featured images
- Nested comments, likes, bookmarks, and reading history
- Newsletter subscription pipeline and analytics models
- SEO-optimized URLs, meta tags, sitemap, robots.txt, and structured page templates
- Dockerized development and GitHub Actions CI workflow

## Project Structure

- `techsphere/` - Django project settings and URL configuration
- `apps/accounts/` - authentication, profile, and account management
- `apps/blog/` - categories, posts, comments, likes, bookmarks, SEO models
- `apps/newsletter/` - newsletter subscriber management
- `apps/analytics/` - traffic and search analytics models
- `apps/ads/` - advertisement and affiliate campaign models
- `templates/` - Django templates for frontend pages
- `static/` - styles and frontend assets
- `Dockerfile` and `docker-compose.yml` - local and production container setup
- `.github/workflows/ci.yml` - CI pipeline for tests and migrations

## Local Setup

1. Copy the environment template:

   ```bash
   cp .env.example .env
   ```

2. Start the development environment:

   ```bash
   docker compose up --build
   ```

3. Apply migrations and create a superuser:

   ```bash
   docker compose exec web python manage.py migrate
   docker compose exec web python manage.py createsuperuser
   ```

4. Open the app at `http://localhost:8000`.

## Deployment

TechSphere includes production-ready deployment files:

- `Dockerfile`
- `docker-compose.yml`
- `nginx.conf`
- `gunicorn.conf.py`
- `render.yaml`

For low-cost deployment, use GitHub Student Developer Pack services such as GitHub Actions, free-tier DigitalOcean/App Platform, Render, or student cloud credits on AWS/Azure/GCP.

## Render Deployment (Recommended)

Render is the easiest hosting path for this Django app because it supports Docker, managed Postgres, and Redis.

1. Connect your GitHub repository to Render.
2. Use the included `render.yaml` or create a Web Service with Docker.
3. Configure production environment variables in Render.
4. Run migrations and collect static files.

See `deploy/render.md` for full Render deployment instructions.

## GitHub Student Pack Optimization

- Use GitHub repos and Actions for CI/CD.
- Host static and media assets with CDN-friendly storage.
- Use GitHub Codespaces for instant development environment.
- Start free with Docker Compose locally, then scale with managed Postgres and Redis tiers.

## Phase Scaling Plan

### Phase 1: 0 - 10,000 visitors/month

- Infrastructure: Docker Compose local + small cloud instance
- Database: single PostgreSQL instance
- Caching: Redis local / managed free tier
- CDN: free CDN for static assets
- Cost: near free using student credits and free tiers

### Phase 2: 10,000 - 100,000 visitors/month

- Infrastructure: managed container service or low-cost VPS
- Database: managed PostgreSQL with automated backups
- Caching: Redis managed instance
- CDN: Cloudflare or GitHub Pages for static files
- Cost: modest, student credits can cover initial load

### Phase 3: 100,000 - 1,000,000+ visitors/month

- Infrastructure: scalable Kubernetes or PaaS
- Database: PostgreSQL replica set, connection pooling
- Caching: Redis cluster + CDN edge caching
- CDN: global CDN for JS, CSS, images, sitemap
- Cost: optimize with reserved instances and caching

## Environment Variables

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `REDIS_URL`

## Contributing

See `CONTRIBUTING.md` for contribution guidelines.

## License

This project is open source and may be licensed under a student-friendly open source license.
