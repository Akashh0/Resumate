from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('Resumate.urls')),
    path('', lambda request: HttpResponse("Welcome to Resumate Backend 🚀")),
]
