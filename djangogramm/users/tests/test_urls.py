from django.test import TestCase, SimpleTestCase
from django.urls import reverse, resolve
from users.views import PostsFeed, Profile, ChangeProfile, ShowPost, AboutSite, AddPage, ContactFormView, RegisterUser, \
    LoginUser, EmailVerify, ConfirmEmailView, InvalidVerifyView, AddLikeView, RemoveLikeView, ForeignProfile, Followers, \
    Follows
from django.contrib.auth.views import LogoutView


# Create your tests here.


class TestUrls(SimpleTestCase):

    def test_PostFeed(self):
        url = reverse('home')
        assert resolve(url).func.view_class == PostsFeed

    def test_Profile(self):
        url = reverse('user')
        assert resolve(url).func.view_class == Profile

    def test_ChangeProfile(self):
        url = reverse('change_profile')
        assert resolve(url).func.view_class == ChangeProfile

    def test_ShowPost(self):
        url = reverse('post', args=[1])
        assert resolve(url).func.view_class == ShowPost

    def test_AboutSite(self):
        url = reverse('about')
        assert resolve(url).func.view_class == AboutSite

    def test_AddPage(self):
        url = reverse('add_page')
        assert resolve(url).func.view_class == AddPage

    def test_ContactFormView(self):
        url = reverse('contact')
        assert resolve(url).func.view_class == ContactFormView

    def test_RegisterUser(self):
        url = reverse('register')
        assert resolve(url).func.view_class == RegisterUser

    def test_LoginUser(self):
        url = reverse('login')
        assert resolve(url).func.view_class == LoginUser

    def test_EmailVerify(self):
        url = reverse('verify_email', args=[1, 2])
        assert resolve(url).func.view_class == EmailVerify

    def test_ConfirmEmailView(self):
        url = reverse('confirm_email')
        assert resolve(url).func.view_class == ConfirmEmailView

    def test_InvalidVerifyView(self):
        url = reverse('invalid_verify')
        assert resolve(url).func.view_class == InvalidVerifyView

    def test_LogoutView(self):
        url = reverse('logout')
        assert resolve(url).func.view_class == LogoutView

    def test_AddLikeView(self):
        url = reverse('add')
        assert resolve(url).func.view_class == AddLikeView

    def test_RemoveLikeView(self):
        url = reverse('remove')
        assert resolve(url).func.view_class == RemoveLikeView

    def test_ForeignProfile(self):
        url = reverse('foreign_profile', args=['slug'])
        assert resolve(url).func.view_class == ForeignProfile

    def test_Followers(self):
        url = reverse('followers', args=[1])
        assert resolve(url).func.view_class == Followers

    def test_Follows(self):
        url = reverse('follows', args=[1])
        assert resolve(url).func.view_class == Follows


