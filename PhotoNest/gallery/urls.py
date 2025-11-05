from django.urls import path
from .views import gallery_home, upload_image

urlpatterns = [
    path('', gallery_home, name='gallery_home'),
    path('upload/', upload_image, name='upload_image')
]
