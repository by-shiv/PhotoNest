from django.db import models
from users.models import CustomUser

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
