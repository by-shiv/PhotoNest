from django.contrib import admin
from .models import ImageUpload, Album, UserProfile

class ImageUploadAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'favorite', 'archived', 'trashed', 'upload_date', 'ai_tags')
    search_fields = ('title', 'user__username', 'tags', 'ai_tags')
    list_filter = ('favorite', 'archived', 'trashed', 'upload_date')

class AlbumAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user', 'created_date')
    search_fields = ('name', 'user__username')

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'profile_pic')

admin.site.register(ImageUpload, ImageUploadAdmin)
admin.site.register(Album, AlbumAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
