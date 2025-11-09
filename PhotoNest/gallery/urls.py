from django.urls import path
from .views import (
    gallery_home, upload_image, favorites, archives, 
    trash, recently_added, albums_list, album_detail,
    toggle_favorite, toggle_archive, move_to_trash,
    restore_from_trash, delete_permanently
)

urlpatterns = [
    path('', gallery_home, name='gallery_home'),
    path('upload/', upload_image, name='upload_image'),
    path('favorites/', favorites, name='favorites'),
    path('archives/', archives, name='archives'),
    path('trash/', trash, name='trash'),
    path('recently-added/', recently_added, name='recently_added'),
    path('albums/', albums_list, name='albums_list'),
    path('albums/<int:album_id>/', album_detail, name='album_detail'),
    path('image/<int:image_id>/favorite/', toggle_favorite, name='toggle_favorite'),
    path('image/<int:image_id>/archive/', toggle_archive, name='toggle_archive'),
    path('image/<int:image_id>/trash/', move_to_trash, name='move_to_trash'),
    path('image/<int:image_id>/restore/', restore_from_trash, name='restore_from_trash'),
    path('image/<int:image_id>/delete/', delete_permanently, name='delete_permanently'),
]
