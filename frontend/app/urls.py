from django.urls import path
from .views import index, process_request_view, signup
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', index, name='index'),
    path('process/', process_request_view, name='process_request_view'),
    path('login/',
         auth_views.LoginView.as_view(template_name='registration/login.html'),
         name='login'),
    path('logout/',
         auth_views.LogoutView.as_view(next_page='/'),
         name='logout'),
    path('signup/', signup, name='signup'),  # Add this line
]
