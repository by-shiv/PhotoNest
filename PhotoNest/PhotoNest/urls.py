from django.contrib import admin
from django.urls import path, include
from users.views import auth_view 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('users/', include('users.urls')),
    path('gallery/', include('gallery.urls')),
    path('', auth_view, name='root_auth'), 
]


from django.conf import settings
from django.conf.urls.static import static
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)