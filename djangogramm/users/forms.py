from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django.forms import widgets

from .models import Post, Image, Tag
from .utils import send_email_verify, tag_creator
from django.utils.translation import gettext_lazy as _
from captcha.fields import CaptchaField, CaptchaTextInput

User = get_user_model()


class AddPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['id', 'title', 'text']

    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) > 50:
            raise ValidationError('Длинна превышает 50 символов')
        return title


class TagForm(forms.Form):
    tag_title = forms.CharField(max_length=250, label='Tags')

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super(TagForm, self).__init__(*args, **kwargs)

    def clean_tag_title(self):
        tag_title = tag_creator(self.cleaned_data['tag_title'])
        var = '@\"\'()[]{}:;.|`%*/?><+='
        counter = 0
        for element in var:
            for string in tag_title:
                if element in string:
                    raise ValidationError(
                        'В тегах не должно быть пробелов либо символов кроме дефиса и запятых')
        for string in tag_title:
            for _ in string:
                counter += 1
                if counter >= 120:
                    raise ValidationError(
                        'Слишком много тегов для одного поста')
        return tag_title

    def save_for(self, post):
        for tag in self.cleaned_data['tag_title']:
            to_save = Tag(tag_title=tag)
            to_save.save()
            post.tags.add(to_save)


class ImageForm(forms.Form):
    image = forms.ImageField(widget=widgets.FileInput(attrs={'multiple': 'multiple'}))

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super(ImageForm, self).__init__(*args, **kwargs)

    def clean_image(self):
        # Остаются только картинки
        image = [i for i in self.request.FILES.getlist('image') if 'image' in i.content_type]
        # Если среди загруженных файлов картинок нет, то исключение
        if len(image) == 0:
            raise forms.ValidationError(u'Not found uploaded photos.')
        return image

    def save_for(self, post, user):
        for image in self.cleaned_data['image']:
            to_save = Image(image=image, resized_image=image, post_id=post, user_id=user)
            to_save.save()


class ChangeProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'avatar', 'about']

    def save_with_slug(self, commit=True):
        """Override the save method to add an automatic slug."""
        if self.errors:
            raise ValueError(
                "The %s could not be %s because the data didn't validate." % (
                    self.instance._meta.object_name,
                    'created' if self.instance._state.adding else 'changed',
                )
            )
        if commit:
            self.instance.slug = self.cleaned_data['username'].lower()
            self.instance.save()
            self._save_m2m()
        else:
            self.save_m2m = self._save_m2m
        return self.instance


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email']

    def save_with_slag(self, commit=True):
        """Override the save method to add an automatic slug."""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])

        if commit:
            user.slug = self.cleaned_data['username'].lower()
            user.save()
        return user


class LoginForm(AuthenticationForm):

    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username is not None and password:
            self.user_cache = authenticate(
                self.request,
                username=username,
                password=password
            )
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)
            if not self.user_cache.email_verify:
                send_email_verify(self.request, self.user_cache)
                raise ValidationError(
                    'Email is not verify? Check your email!',
                    code="invalid_login",
                )
        return self.cleaned_data

    class Meta:
        # model = User
        fields = ['username', 'email']


class ContactForm(forms.Form):
    name = forms.CharField(
        label="Имя",
        max_length=255,
        widget=forms.TextInput(
            attrs={'placeholder': 'Введите ваше имя'}
        )
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.TextInput(
            attrs={'placeholder': 'Введите Email'}
        )
    )
    content = forms.CharField(
        label="Введите текст",
        widget=forms.Textarea(attrs={'cols': 39, 'rows': 5, 'placeholder': 'Сообщение'}))

    captcha = CaptchaField(widget=CaptchaTextInput(attrs={'class': 'form-control'}), label="Капча")
