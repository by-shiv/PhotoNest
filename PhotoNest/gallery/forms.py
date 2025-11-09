from django import forms
from .models import ImageUpload, Album

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = ImageUpload
        fields = ['image', 'title', 'tags', 'description', 'audio_note']

class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ['name', 'description']
