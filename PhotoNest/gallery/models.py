from django.db import models
from users.models import CustomUser
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


class ImageUpload(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='gallery/')
    title = models.CharField(max_length=255, blank=True)
    tags = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    audio_note = models.FileField(upload_to='audio/', blank=True, null=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    favorite = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)
    trashed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.title or 'Image'} - {self.user.username}"

class Album(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    images = models.ManyToManyField(ImageUpload, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s profile"



@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        from .models import UserProfile
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()

