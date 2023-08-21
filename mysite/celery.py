import os

from celery import Celery
from dotenv import load_dotenv

load_dotenv()

app = Celery("mysite", broker_url=os.getenv("CHANNEL_LAYERS_HOST_WITH_PASSWORD"))
app.autodiscover_tasks()
