from django.contrib.auth.views import LogoutView
from django.urls import path, include
from django.views.generic import TemplateView

from .views import *

urlpatterns = [
    # path('', include('django.contrib.auth.urls')),
    path('', PostsFeed.as_view(), name='home'),
    path('user/', Profile.as_view(), name='user'),
    path('change_profile/', ChangeProfile.as_view(), name='change_profile'),
    path('post/<int:post_id>/', ShowPost.as_view(), name='post'),
    path('about/', AboutSite.as_view(), name='about'),
    path('add_page/', AddPage.as_view(), name='add_page'),
    path('contact/', ContactFormView.as_view(), name='contact'),
    path('register/', RegisterUser.as_view(), name='register'),
    path('login/', LoginUser.as_view(), name='login'),
    path('verify_email/<uidb64>/<token>/', EmailVerify.as_view(), name='verify_email'),
    path('confirm_email/', ConfirmEmailView.as_view(template_name='registration/confirm_email.html'), name='confirm_email'),
    path('invalid_verify/', InvalidVerifyView.as_view(template_name='registration/invalid_verify.html'), name='invalid_verify'),
    path("logout/", LogoutView.as_view(), name="logout"),
    path('likes/add/', AddLikeView.as_view(), name='add'),
    path('likes/remove/', RemoveLikeView.as_view(), name='remove'),
    # path('tags/', tags_list, name='tags_list_url'),
]

urlpatterns += [
    path('captcha/', include('captcha.urls')),
]
