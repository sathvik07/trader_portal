# core/tasks.py
from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_watchlist_email(user_email, company_name):
    print(f"[CELERY TASK] Sending email to {user_email} for company {company_name}")
    send_mail(
        subject='Company Added to Watchlist',
        message=f'You added {company_name} to your watchlist.',
        from_email='no-reply@tradersportal.com',
        recipient_list=[user_email],
    )
