# Trader Portal Backend

This is a Django backend for the Trader Portal, deployed on an AWS EC2 Ubuntu instance using Gunicorn, Supervisor, and Nginx.

---

## Tech Stack

- **Backend**: Django (with Django REST Framework)
- **Deployment**: Gunicorn + Nginx + Supervisor
- **Environment Management**: `python-decouple` or `django-environ`
- **Hosting**: AWS EC2 (Ubuntu)

---



## Health Check:
curl http://127.0.0.1:8000/api/register
curl http://13.60.241.112/api/register  

---

## User Registration:
curl -X POST http://13.60.241.112/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
        "username": "testuser",
        "password": "StrongPassword123",
        "email": "test@example.com"
      }'



