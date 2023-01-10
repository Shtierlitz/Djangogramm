from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
from django.urls import reverse
from django.utils import timezone

from django.conf import settings
from django_resized import ResizedImageField


class User(AbstractUser):
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    avatar = models.ImageField(upload_to="photos/users", blank=True)
    about = models.TextField(blank=True, default="About user")
    slug = models.SlugField(max_length=50, unique=True, db_index=True, null=True, verbose_name='URL')
    follows = models.ManyToManyField('self', symmetrical=False)

    email_verify = models.BooleanField(default=False)

    def __str__(self):
        return self.username

    class Meta:
        ordering = ("id",)

    def get_absolute_url(self):
        return reverse('foreign_profile', kwargs={'user_slug': self.slug})


class Post(models.Model):
    title = models.CharField(max_length=50)
    text = models.TextField(blank=True)
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)
    tags = models.ManyToManyField("Tag", blank=True, related_name='posts', verbose_name="Тэги")

    user = models.ForeignKey("User", on_delete=models.CASCADE, null=True, verbose_name="Пользователь")

    class Meta:
        ordering = ('-time_create', 'id')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post', kwargs={'post_id': self.pk})


class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    liked_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name="Поставил лайк")
    like = models.BooleanField('like', default=False)
    created = models.DateTimeField('Дата и время', default=timezone.now)

    def __str__(self):
        return f"{self.liked_by}: {self.post} {self.like}"


class Tag(models.Model):
    tag_title = models.CharField(max_length=250, verbose_name='Tags')

    def __str__(self):
        return self.tag_title


class Image(models.Model):
    image = models.ImageField(upload_to="photos/posts/%Y/%m/%d")
    resized_image = ResizedImageField(
        size=[1000, 750],
        upload_to='photos/posts/resized/%Y/%m/%d',
        quality=50,
        force_format='PNG',
        null=True
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)




