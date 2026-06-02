# Deployment Guide

## GitHub Actions

The project includes `.github/workflows/ci.yml` for continuous integration.

## Docker deployment

1. Build the container:

   ```bash
   docker build -t techsphere .
   ```

2. Run with Docker Compose:

   ```bash
   docker compose up -d
   ```

3. The app will be available at `http://localhost:8000`.

## Production suggestions

- Use a managed PostgreSQL database.
- Use Redis for caching and Celery.
- Configure HTTPS with a reverse proxy such as Nginx or cloud load balancer.
- Use a CDN for static assets.
- Set `DJANGO_DEBUG=False` in production.

## Student-friendly hosting

- Use GitHub Student Pack credits for DigitalOcean, Render, or cloud provider discounts.
- Start with free-tier managed services for PostgreSQL, Redis, and CDN.
