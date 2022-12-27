from django.contrib.auth import get_user_model
import tempfile
import shutil
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from users.utils import get_d_m_y

from users.models import Post, Tag, Like, Image
from io import BytesIO
from PIL import Image as Im
from django.core.files.base import File

MEDIA_ROOT = tempfile.mkdtemp()

User = get_user_model()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestViews(TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)  # delete the temp dir
        super().tearDownClass()

    @staticmethod
    def get_image_file(name='test.png', ext='png', size=(50, 50), color=(256, 0, 0)):
        file_obj = BytesIO()
        image = Im.new("RGB", size=size, color=color)
        image.save(file_obj, ext)
        file_obj.seek(0)
        return File(file_obj, name=name)

    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='test_username_1', first_name='test_first_name_1',
                                              last_name='test_last_name_1', about='test_about_1', email_verify=True,
                                              password='test_password')
        self.post1 = Post.objects.create(title='title_test_1', text='text_test_1', user=self.user1)
        self.client.login(username='test_username_1', password='test_password')

    def test_PostFeed(self):
        response = self.client.get(reverse('home'))
        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'text/html; charset=utf-8'
        self.assertTemplateUsed(response, 'users/index.html')

    def test_ShowPost(self):
        response = self.client.get(reverse('post', args=[1]))
        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'text/html; charset=utf-8'
        self.assertTemplateUsed(response, 'users/post.html')

    def test_AboutSite(self):
        response = self.client.get(reverse('about'))
        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'text/html; charset=utf-8'
        self.assertTemplateUsed(response, 'users/about.html')

    def test_Profile_get(self):
        response = self.client.get(reverse('user'))
        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'text/html; charset=utf-8'
        self.assertTemplateUsed(response, 'users/user.html')

    def test_ChangeProfile_get(self):
        response = self.client.get(reverse('change_profile'))
        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'text/html; charset=utf-8'
        self.assertTemplateUsed(response, 'users/change_profile.html')

    def test_ChangeProfile_post(self):
        self.image = self.get_image_file(name='test3.png')
        response = self.client.post(reverse('change_profile'), {
            'username': 'test_username',
            'first_name': 'test_first_name',
            'last_name': 'test_last_name',
            'avatar': self.image,
            'about': 'test_about',
        })
        test_user = User.objects.get(pk=1)
        assert response.status_code == 302
        self.assertEqual(test_user.username, 'test_username')
        self.assertEqual(test_user.first_name, 'test_first_name')
        self.assertEqual(test_user.last_name, 'test_last_name')
        self.assertEqual(test_user.avatar, 'photos/users/test3.png')
        self.assertEqual(test_user.about, 'test_about')

    def test_ChangeProfile_post_no_data(self):
        response = self.client.post(reverse('change_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/change_profile.html')

    def test_AddPage_get(self):
        response = self.client.get(reverse('add_page'))
        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'text/html; charset=utf-8'
        self.assertTemplateUsed(response, 'users/addpage.html')

    def test_AddPage_post(self):
        self.image = self.get_image_file(name='test3.png')
        response = self.client.post(reverse('add_page'), {
            'title': 'test_title',
            'text': 'test_text',
            'image': self.image,
            'tag_title': 'test_tag_1'
        })

        post = Post.objects.get(pk=2)
        image = Image.objects.get(post=2)
        tag = Tag.objects.get(pk=1)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(post.title, 'test_title')
        self.assertEqual(post.text, 'test_text')
        self.assertEqual(len(post.tags.all()), 1)
        self.assertEqual(tag.tag_title, '#test_tag_1')
        self.assertEqual(image.image, f'photos/posts/{get_d_m_y("y")}/{get_d_m_y("m")}/{get_d_m_y("d")}/test3.png')
        self.assertEqual(image.resized_image,
                         f'photos/posts/resized/{get_d_m_y("y")}/{get_d_m_y("m")}/{get_d_m_y("d")}/test3.png')

    def test_AddPage_post_no_data(self):
        response = self.client.get(reverse('add_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/addpage.html')

    def test_ContactFormView_get(self):
        response = self.client.get(reverse('contact'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/contact.html')

    def test_ContactFormView_post(self):
        response = self.client.post(reverse('contact'), {
            'name': 'test_name',
            'email': 'rollbar1990@gmail.com',
            'content': 'test_content',
            'captcha_0': 'test',
            'captcha_1': "PASSED"
        })
        self.assertEqual(response.status_code, 302)
        assert response.headers['Content-Type'] == 'text/html; charset=utf-8'

    def test_LoginUser_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_LoginUser_post(self):
        response = self.client.post(reverse('login'), {
            'username': 'test_username_1',
            'password': 'test_password'
        })
        self.assertEqual(response.status_code, 302)

    def test_RegisterUser_get(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')

    def test_RegisterUser_post(self):
        response = self.client.post(reverse('register'), {
            'username': 'test_username',
            'email': 'test@email.com',
            'password1': 'register_test_password_007',
            'password2': 'register_test_password_007',
        })
        self.assertEqual(response.status_code, 302)

    def test_ConfirmEmailView(self):
        response = self.client.get(reverse('confirm_email'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/confirm_email.html')

    def test_InvalidVerifyView(self):
        response = self.client.get(reverse('invalid_verify'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/invalid_verify.html')

    def test_EmailVerify(self):
        response = self.client.get(reverse('verify_email', args=[1, 2]))
        self.assertEqual(response.status_code, 302)

    def test_AddLikeView_post(self):
        response = self.client.post(reverse('add'), data=dict(post_id=1, user_id=1, url_form='home'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(Like.objects.all()), 1)

    def test_RemoveLikeView_post(self):
        Like.objects.create(
            post=Post.objects.get(pk=1),
            liked_by=User.objects.get(pk=1)
        )
        response = self.client.post(reverse('remove'), data=dict(likes_id=1, like=True, url_form='home'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(Like.objects.all()), 0)
