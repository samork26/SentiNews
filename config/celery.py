import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

app.conf.beat_schedule = {
    "fetch-news-every-6-hours": {
        "task": "app.automation.tasks.fetch_and_store_news",
        "schedule": crontab(minute=0, hour="*/6"),  # Every 6 hours
    },
    "delete-old-news-daily": {
        "task": "app.automation.tasks.delete_old_articles",
        "schedule": crontab(minute=0, hour=0),  # Runs daily at midnight
    },
}
