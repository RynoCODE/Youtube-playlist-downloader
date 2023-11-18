from django.urls import path
from .views import home, download_files

urlpatterns = [
    path('', home, name='home'),
    path('download/', download_files, name='download_files'),
]
