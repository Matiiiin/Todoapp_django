from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import User, Profile

"""
save a profile for the created user
"""


@receiver(post_save, sender=User)
def create_profile_for_user(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(
            user=instance,
        )
