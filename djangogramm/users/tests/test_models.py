import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import TestCase, Client, override_settings
from io import BytesIO
from PIL import Image as Im
from django.core.files.base import File

from users.models import Post, Like, Tag, Image
from users.utils import get_d_m_y

MEDIA_ROOT = tempfile.mkdtemp()
User = get_user_model()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestModels(TestCase):
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
        self.user1 = User.objects.create_user(username='test_username_1', first_name='test_first_name_1',
                                              last_name='test_last_name_1', slug='test_slug_1', about='test_about_1', email_verify=True,
                                              password='test_password')
        self.user2 = User.objects.create_user(username='test_username_2', first_name='test_first_name_2',
                                              last_name='test_last_name_2', slug='test_slug_2', about='test_about_2', email_verify=True,
                                              password='test_password_2')
        self.post1 = Post.objects.create(title='title_test_1', text='text_test_1', user=self.user1)
        self.like1 = Like.objects.create(post=self.post1, liked_by=self.user1, like=True)
        self.client.login(username='test_username_1', password='test_password')
        self.tag1 = Tag.objects.create(tag_title="test_tag_1")
        self.tag2 = Tag.objects.create(tag_title="test_tag_2")
        self.post1.tags.add(self.tag1)
        self.post1.tags.add(self.tag2)
        self.user1.follows.add(self.user2)

    def test_User(self):
        self.test_user = User.objects.get(pk=1)
        self.image = self.get_image_file(name='test2.png')
        self.test_user.avatar = self.image
        self.assertEqual(self.test_user.username, 'test_username_1')
        self.assertEqual(self.test_user.first_name, 'test_first_name_1')
        self.assertEqual(self.test_user.last_name, 'test_last_name_1')
        self.assertEqual(self.test_user.slug, 'test_slug_1')
        self.assertEqual(self.test_user.about, 'test_about_1')
        self.assertEqual(self.test_user.avatar, 'test2.png')
        self.assertEqual(self.test_user.email_verify, True)
        self.assertEqual(self.test_user.follows.all()[0], self.user2)
        self.assertEqual(self.test_user.get_absolute_url(), '/foreign_profile/test_slug_1/')

    def test_Post(self):
        self.test_user = User.objects.get(pk=1)
        self.test_post = Post.objects.get(pk=1)
        self.assertEqual(self.test_post.title, 'title_test_1')
        self.assertEqual(self.test_post.text, 'text_test_1')
        self.assertEqual(self.test_post.user.id, self.test_user.pk)
        self.assertEqual(self.test_post.is_published, True)
        self.assertEqual(self.test_post.get_absolute_url(), '/post/1/')

    def test_Like(self):
        self.test_like = Like.objects.get(pk=1)
        self.assertEqual(self.test_like.post.pk, self.post1.pk)
        self.assertEqual(self.test_like.liked_by.pk, self.user1.pk)

    def test_Tag(self):
        self.test_tag = Tag.objects.get(pk=1)
        self.assertEqual(self.tag1.tag_title, 'test_tag_1')
        self.assertEqual(len(self.test_tag.posts.all()), 1)
        self.assertEqual(len(self.post1.tags.all()), 2)

    def test_Image(self):
        self.image = self.get_image_file(name='test2.png')
        self.test_image_1 = Image.objects.create(image=self.image, resized_image=self.image, post=self.post1, user=self.user1)
        self.assertEqual(self.test_image_1.image,
                         f'photos/posts/{get_d_m_y("y")}/{get_d_m_y("m")}/{get_d_m_y("d")}/test2.png')
        self.assertEqual(self.test_image_1.resized_image,
                         f'photos/posts/resized/{get_d_m_y("y")}/{get_d_m_y("m")}/{get_d_m_y("d")}/test2.png')
        self.assertEqual(self.test_image_1.post.pk, 1)
        self.assertEqual(self.test_image_1.user.pk, 1)
