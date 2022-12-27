import shutil
import tempfile
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import InMemoryUploadedFile

from users.forms import AddPostForm, ImageForm, TagForm, ChangeProfileForm, RegisterForm, LoginForm, ContactForm
from django.test import SimpleTestCase, override_settings, TestCase
from io import BytesIO
from PIL import Image as Im
from django.core.files.base import File


MEDIA_ROOT = tempfile.mkdtemp()
User = get_user_model()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestForms(TestCase):
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

    def test_AddPostForm_valid_data(self):
        form = AddPostForm(data={
            'title': "test_form_1",
            'text': 'test_text_1'
        })
        self.assertTrue(form.is_valid())

    def test_AddPostForm_no_data(self):
        form = AddPostForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 1)

    def test_AddPostForm_clean_title(self):
        form = AddPostForm(data={
            'title': "x" * 60,
            'text': 'test_text_1'
        })
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 1)

    def test_TagForm_valid_data(self):
        form = TagForm(data={
            'tag_title': "test_tag"
        })
        self.assertTrue(form.is_valid())

    def test_TagForm_no_data(self):
        form = TagForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 1)

    def test_TagForm_clean_tag_title(self):
        form = TagForm(data={
            'tag_title': "false_tag=\'\"+*/@$%"
        })
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 1)

    def test_ChangeProfileForm_valid(self):
        form = ChangeProfileForm(
            data={
                'username': 'Test_username',
                'first_name': 'test_first_name',
                'last_name': 'test_second_name',
                'avatar': 'test.png',   # not required
                'about': 'test_about'   # not required
            },
            files={
                InMemoryUploadedFile: self.get_image_file('test.png')
            })
        self.assertTrue(form.is_valid())

    def test_ChangeProfileForm_no_data(self):
        form = ChangeProfileForm(
            data={})
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 3)

    def test_ChangeProfileForm_clean_fields(self):
        form = ChangeProfileForm(
            data={
                'username': 'u'*151,
                'first_name': 't'*21,
                'last_name': 't'*21,
                'avatar': 'test.png',  # not required
                'about': 'test_about'  # not required
            })
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 3)

    def test_RegisterForm_is_valid(self):
        form = RegisterForm(data={
            'username': 'test_username_1',
            'email': "test_email@mail.com",
            'password1': 'test_password',
            'password2': 'test_password'
        })
        self.assertTrue(form.is_valid())

    def test_RegisterForm_no_data(self):
        form = RegisterForm(
            data={})
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 4)

    def test_RegisterForm_clean_fields(self):
        form = RegisterForm(data={
            'username': 'u'*151,
            'email': "test_email",
            'password1': '1234_test_true',
            'password2': '1234_test_false'
        })
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 3)

    def test_LoginForm_is_valid(self):
        self.user1 = User.objects.create_user(username='test_username_1', first_name='test_first_name_1',
                                              last_name='test_last_name_1', about='test_about_1', email_verify=True,
                                              password='test_password')
        form = LoginForm(data={
            'username': 'test_username_1',
            'password': 'test_password'
        })
        self.assertTrue(form.is_valid())

    def test_LoginForm_no_data(self):
        form = LoginForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 2)

    def test_LoginForm_clean_passwords(self):
        form = LoginForm(data={
            'password': '1234'  # to short
        })
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 1)

    def test_ContactForm_is_valid(self):
        form = ContactForm(data={
            'name':  'test_name',
            'email': "test_email@mail.com",
            'content': 'test_content',
            'captcha_0': 'test',
            'captcha_1': "PASSED"
        })
        self.assertTrue(form.is_valid())

    def test_ContactForm_no_data(self):
        form = ContactForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 4)

    def test_ContactForm_clean_fields(self):
        form = ContactForm(data={
            'name': 't'*300,
            'email': "test_email",
            'content': 'test_content',
            'captcha_0': '0',
            'captcha_1': "0"
        })
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 3)


    # def test_ImageForm(self):
    #     self.image = self.get_image_file('test.png')
    #
    #     form = ImageForm(data={'image': 'test.png'}, files={
    #         InMemoryUploadedFile: self.image
    #     })
    #     print(form.clean_image())
    #     print(form.is_valid())
    #     self.assertTrue(form.is_valid())
    #
    #     '''image = [i for i in self.request.FILES.getlist('image') if 'image' in i.content_type]
    #     AttributeError: 'HttpResponse' object has no attribute 'FILES'''''

