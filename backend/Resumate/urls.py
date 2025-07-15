from django.urls import path
from .views import RegisterView, UserView, LoginView, UploadResumeView

from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('user/', UserView.as_view(), name='user'), path('login/', LoginView.as_view(), name='login'),
    path('upload-resume/', UploadResumeView.as_view()), 
]
