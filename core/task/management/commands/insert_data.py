import random

from django.core.management.base import BaseCommand
from accounts.models import User , Profile
from task.models import Task , TaskStatus
from faker import Faker
class Command(BaseCommand):
    help = "Create dummy data for application"
    def __init__(self):
        super().__init__()
        self.faker = Faker()
    def handle(self, *args, **options):
        user = User.objects.create_user(
            email=self.faker.email(),
            password='123'
        )
        profile = Profile.objects.get(user=user)
        for _ in range(5):
            Task.objects.get_or_create(
                author=profile,
                title=self.faker.text(max_nb_chars=20),
                status=random.choice(list(TaskStatus))
            )
        self.stdout.write(
            self.style.SUCCESS('Successfully created the data'))