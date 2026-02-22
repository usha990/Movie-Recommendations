from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
import random

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True, null=True)

    def _str_(self):
        return self.user.username

    def generate_otp(self):
        self.otp = str(random.randint(100000, 999999))
        self.save()
        return self.otp

# Signal must not be indented inside the class
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)