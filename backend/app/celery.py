from celery import Celery
import os

# Load env variables (if needed, though main.py already does this, celery workers run separately)
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

app = Celery('axion')
app.conf.broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
app.conf.result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')
app.conf.task_serializer = 'json'
app.conf.result_serializer = 'json'
app.conf.beat_schedule = {
    'daily-analytics-aggregation': {
        'task': 'app.tasks.analytics.aggregate_daily_analytics',
        'schedule': 86400.0,
        'args': (),
    },
}
app.autodiscover_tasks(['app.tasks'])
