from logging import getLogger
from celery import Celery
from celery import Task

from app.core.config import settings
from app.core.db import engine
from sqlmodel import Session

logger = getLogger(__name__)


class CustomTask(Task):
    _db: Session = None
        


app = Celery(__name__, task_cls="app.worker.celery.CustomTask")
app.conf.broker_url = settings.CELERY_BROKER_URL

app.autodiscover_tasks(packages=["app.worker"], related_name="tasks")
