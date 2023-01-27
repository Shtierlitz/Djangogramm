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
    path('foreign_profile/<slug:user_slug>/', ForeignProfile.as_view(), name='foreign_profile'),
    path('user/<int:user_id>/followers/', Followers.as_view(), name='followers'),
    path('user/<int:user_id>/follows/', Follows.as_view(), name='follows'),
    # path('likes/add/', AddLikeView.as_view(), name='add'),
    # path('likes/remove/', RemoveLikeView.as_view(), name='remove'),

    path('ajax/add/', ajax_add_like, name='add-ajax'),
    path('ajax/remove/', ajax_remove_like, name='remove-ajax'),
    path('api/like-info/<int:post_id>/', api_like_info, name='api-like-info'),

    path('ajax/follow-add/', ajax_add_follower, name='ajax-add-follower'),
    path('ajax/follow-remove/', ajax_remove_follower, name='ajax-remove-follower'),
    path('api/follow-info/<int:user_id>/<int:foreign_user_id>/', api_follow_info, name='api-follow-info'),
]

urlpatterns += [
    path('captcha/', include('captcha.urls')),
]
