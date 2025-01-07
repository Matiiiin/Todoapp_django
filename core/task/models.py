from django.db import models


class TaskStatus(models.TextChoices):
    NEW = "NEW", "new"
    DONE = "DONE", "done"


# Create your models here.
class Task(models.Model):
    author = models.ForeignKey(
        "accounts.Profile", on_delete=models.CASCADE, related_name="tasks"
    )
    title = models.CharField(max_length=255)
    status = models.CharField(
        choices=TaskStatus.choices, default=TaskStatus.NEW, max_length=255
    )

    def __str__(self):
        return f"{self.author}  {self.title}"
