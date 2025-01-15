import sys
import time
from celery import shared_task
#
# # task.py
@shared_task
def delete_done_tasks():
    from task.models import Task
    Task.objects.filter(status='DONE').delete()
