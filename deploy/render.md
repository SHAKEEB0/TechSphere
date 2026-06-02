# Render Deployment Guide

This guide helps deploy TechSphere to Render using the existing Docker setup.

## 1. Create a Render account

- Go to `https://render.com`
- Sign up with GitHub and authorize the repository
- Use GitHub Student Developer Pack credits if available

## 2. Add the TechSphere service

- In Render, click **New → Web Service**
- Select your GitHub repository and branch `main`
- Choose **Docker** as the environment
- Set the build command to use the repository `Dockerfile`
- Set the start command:

  ```bash
  gunicorn techsphere.wsgi:application --bind 0.0.0.0:8000 --workers 3
  ```

## 3. Add database and cache

- Create a managed PostgreSQL instance on Render
- Create a managed Redis instance on Render

## 4. Configure environment variables

In Render service settings, add these env vars:

- `DJANGO_SECRET_KEY` = a secure random string
- `DJANGO_DEBUG` = `False`
- `DJANGO_ALLOWED_HOSTS` = your-render-url.onrender.com
- `DATABASE_URL` = (value from Render Postgres service or auto-injected by the managed database connection)
- `REDIS_URL` = `redis://:<password>@<host>:<port>`

## 5. Run migrations and collect static files

Use Render shell or a deploy hook:

```bash
python manage.py migrate --noinput
python manage.py collectstatic --noinput
```

## 6. Verify deployment

- Visit the Render service URL
- Confirm the homepage loads
- Log into the Django admin if needed

## Notes

- Do not commit secret values to GitHub
- Keep `DEBUG=False` in production
- Use the Render dashboard to review logs and environment settings
