from django.urls import path
from .views import auth_view, CustomLogoutView

urlpatterns = [
    path('auth/', auth_view, name='auth'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
]

