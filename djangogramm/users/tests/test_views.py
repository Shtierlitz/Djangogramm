import time

from django.contrib.auth import get_user_model
import tempfile
import shutil

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.urls import reverse

from users.forms import ImageForm
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
    def get_image_file(name='test.png', file_format='png'):
        file = BytesIO()
        image = Im.new('RGBA', size=(50, 50), color=(155, 0, 0))
        image.save(file, file_format)
        file.seek(0)
        return SimpleUploadedFile(name, file.getvalue(), content_type=f'image/{file_format}')

    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='test_username_1', first_name='test_first_name_1',
                                              last_name='test_last_name_1', slug='test_slug', about='test_about_1', email_verify=True,
                                              password='test_password')
        self.user2 = User.objects.create_user(username='test_username_2', first_name='test_first_name_2',
                                              last_name='test_last_name_', slug='test_slug_2', about='test_about_2',
                                              email_verify=True,
                                              password='test_password_2')
        self.post1 = Post.objects.create(title='title_test_1', text='text_test_1', user=self.user1)
        self.client.login(username='test_username_1', password='test_password')

    def test_PostFeed(self):
        response = self.client.get(reverse('home'))
        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'text/html; charset=utf-8'
        self.assertTemplateUsed(response, 'users/index.html')

    def test_ShowPost_get(self):
        response = self.client.get(reverse('post', args=[1]))
        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'text/html; charset=utf-8'
        self.assertTemplateUsed(response, 'users/post.html')

    def test_ShowPost_post(self):
        self.post2 = Post.objects.create(title='title_test_2', text='text_test_2', user=self.user1)
        assert len(Post.objects.all()) == 2
        response = self.client.post(reverse('post', args=[2]), {'delete': 1})
        self.assertEqual(response.status_code, 302)
        assert len(Post.objects.all()) == 1


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
            'username': 'Test_username',
            'first_name': 'test_first_name',
            'last_name': 'test_last_name',
            'avatar': self.image,
            'about': 'test_about',
        })
        test_user = User.objects.get(pk=1)
        assert response.status_code == 302
        self.assertEqual(test_user.username, 'Test_username')
        self.assertEqual(test_user.first_name, 'test_first_name')
        self.assertEqual(test_user.last_name, 'test_last_name')
        self.assertEqual(test_user.avatar, 'photos/users/test3.png')
        self.assertEqual(test_user.about, 'test_about')
        self.assertEqual(test_user.slug, 'test_username')

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
        self.image = [self.get_image_file(name=f'test{i}.png') for i in range(1, 4)]
        response = self.client.post(reverse('add_page'), {
            'title': 'test_title',
            'text': 'test_text',
            'image': self.image,
            'tag_title': 'test_tag_1'
        })

        post = Post.objects.get(pk=2)
        image = Image.objects.last()
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
        response = self.client.post(reverse('add-ajax'), data=dict(post_id=1, user_id=1, url_form='home'), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(Like.objects.all()), 1)

    def test_RemoveLikeView_post(self):
        Like.objects.create(
            post=Post.objects.get(pk=1),
            liked_by=User.objects.get(pk=1)
        )
        response = self.client.post(reverse('remove-ajax'), data=dict(post_id=1, likes_id=1, user_id=1, like=True, url_form='home'), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(Like.objects.all()), 0)

    def test_Followers(self):
        response = self.client.get(reverse('followers', args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/followers.html')

    def test_Follows(self):
        response = self.client.get(reverse('follows', args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/follows.html')

    def test_ForeignProfile_get(self):
        slug = User.objects.get(pk=1).slug
        response = self.client.get(reverse('foreign_profile', args=[slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/foreign_profile.html')

    def test_ForeignProfile_post_subscribe(self):
        test_user_2 = User.objects.get(pk=2)
        response = self.client.post(reverse('foreign_profile', args=[test_user_2.slug]), {
            'subscribe': 1
        })
        self.assertEqual(response.status_code, 302)
        assert len(test_user_2.follows.all()) == 1

    def test_ForeignProfile_post_unsubscribe(self):
        test_user = User.objects.get(pk=1)
        test_user_2 = User.objects.get(pk=2)
        test_user_2.follows.add(test_user)
        response = self.client.post(reverse('foreign_profile', args=[test_user_2.slug]), {
            'unsubscribe': 1
        })
        self.assertEqual(response.status_code, 302)
        assert len(test_user_2.follows.all()) == 0


