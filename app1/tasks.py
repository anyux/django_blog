import time

from celery import shared_task
from user_api.models import User



@shared_task
def add(x, y):
    return x + y


@shared_task
def mul(x, y):
    return x * y


@shared_task
def xsum(numbers):
    return sum(numbers)


@shared_task(bind=True)
def count_user(self):
    time.sleep(50)
    qr= User.objects.all()
    print(qr)
    data = list(qr.values())
    task_id = self.request.id
    for obj in data:
        obj['task_id'] = task_id
    return data


@shared_task
def rename_widget(widget_id, name):
    w = User.objects.get(id=widget_id)
    w.name = name
    w.save()