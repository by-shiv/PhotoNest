from django.urls import path
from .views import (
    gallery_home, upload_image, favorites, archives, 
    trash, recently_added, albums_list, album_detail,
    toggle_favorite, toggle_archive, move_to_trash,
    restore_from_trash, delete_permanently, live_search_api, album_create, album_edit, update_album_images,
    user_images_api, create_album_with_images, remove_from_album, profile_view, profile_edit
)
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', gallery_home, name='gallery_home'),
    path('upload/', upload_image, name='upload_image'),
    path('favorites/', favorites, name='favorites'),
    path('archives/', archives, name='archives'),
    path('trash/', trash, name='trash'),
    path('recently-added/', recently_added, name='recently_added'),
    path('albums/', albums_list, name='albums_list'),
    path('api/search/', live_search_api, name='live_search_api'),
    path('albums/create/', album_create, name='album_create'),
    path('api/user_images/', user_images_api, name='user_images_api'),
    path('albums/<int:album_id>/remove_image/<int:image_id>/', remove_from_album, name='remove_from_album'),
    path('albums/<int:album_id>/update_images/', update_album_images, name='update_album_images'),
    path('api/create_album_with_images/', create_album_with_images, name='create_album_with_images'),
    path('albums/<int:album_id>/edit/', album_edit, name='album_edit'),
    path('albums/<int:album_id>/', album_detail, name='album_detail'),
    path('image/<int:image_id>/favorite/', toggle_favorite, name='toggle_favorite'),
    path('image/<int:image_id>/archive/', toggle_archive, name='toggle_archive'),
    path('image/<int:image_id>/trash/', move_to_trash, name='move_to_trash'),
    path('image/<int:image_id>/restore/', restore_from_trash, name='restore_from_trash'),
    path('image/<int:image_id>/delete/', delete_permanently, name='delete_permanently'),
    path('profile/', profile_view, name='profile'),
    path('profile/edit/', profile_edit, name='profile_edit'),
]
