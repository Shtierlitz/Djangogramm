from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.http import HttpResponseServerError, HttpResponseNotFound, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from django.urls import reverse_lazy
from django.utils.http import urlsafe_base64_decode
from django.views import View
from django.views.generic import ListView, DetailView, FormView
from django.contrib.auth import login
from django.db.models import Count
from django.contrib.sites.models import Site

from users.forms import *
from .utils import *


User = get_user_model()


class PostsFeed(DataMixin, View):
    template_name = 'users/index.html'

    def get(self, request):
        search_query = request.GET.get('search', '')
        if search_query:
            posts = []
            # filter by post title
            for _ in Post.objects.all():
                if _.title == search_query:
                    posts.append(_)
            # filter by tag title
            for i in Post.objects.filter(tags__tag_title=search_query):
                posts.append(i)
            # filter by username
            for _ in Post.objects.all():
                if _.user.username == search_query:
                    posts.append(_)

            if len(posts) == 0:
                posts = Post.objects.filter(is_published=True)
        else:
            posts = Post.objects.filter(is_published=True)
        context = self.get_user_context()
        context['posts'] = posts
        context['search'] = True

        return render(request, self.template_name, context=context)


class ShowPost(DataMixin, View):
    model = Post
    template_name = 'users/post.html'

    def get(self, request, post_id):
        context = self.get_user_context()
        context_mixin = self.get_user_context(title=Post.objects.get(pk=post_id))
        context['post'] = Post.objects.get(pk=post_id)
        # context = dict(list(context.items()) + list(context_mixin.items()))
        context.update(context_mixin)
        return render(request, self.template_name, context=context)

    def post(self, request, post_id):
        context = self.get_user_context()
        context['post'] = Post.objects.get(pk=post_id)
        obj_post = Post.objects.get(pk=post_id)
        obj_image = Image.objects.filter(post=post_id)
        context_mixin = self.get_user_context(title=obj_post.title)
        # context = dict(list(context.items()) + list(context_mixin.items()))
        context.update(context_mixin)

        if request.POST.get('delete'):
            obj_post.delete()
            for i in obj_image:
                i.delete()
            return redirect('home')

        return render(request, self.template_name, context=context)


class AboutSite(DataMixin, View):
    def get(self, request):
        context = self.get_user_context()
        context['title'] = 'О сайте'
        return render(request, 'users/about.html', context=context)


class Profile(LoginRequiredMixin, DataMixin, ListView):
    model = User
    template_name = 'users/user.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = get_object_or_404(User, pk=self.request.user.pk)
        context_mixin = self.get_user_context(title=f"Ваш профиль: {context['user']}")
        context_mixin['followers'] = context['user'].follows.all().count()
        context_mixin['follows'] = len(get_folowers(context['user']))
        context_mixin['user_images'] = Image.objects.filter(user=self.request.user.pk).order_by('-id')
        context_mixin['user_images_count'] = len(context_mixin['user_images'])
        context.update(context_mixin)
        return context


class ChangeProfile(LoginRequiredMixin, DataMixin, View):
    post_form = ChangeProfileForm
    template_name = 'users/change_profile.html'

    def get(self, request):
        user = request.user
        initiial_data = {
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'about': user.about,
        }
        context = self.get_user_context()
        context['form'] = self.post_form(initial=initiial_data)
        context['title'] = 'Редктирование профиля'
        context['image'] = user.avatar

        return render(request, self.template_name, context=context)

    def post(self, request):
        settings_exists = get_object_or_404(User, pk=request.user.pk)
        settings_form = self.post_form(request.POST, request.FILES, instance=settings_exists)
        user = request.user
        context = self.get_user_context()
        context['form'] = settings_form
        context['title'] = 'Редктирование профиля'
        context['image'] = user.avatar
        if settings_form.is_valid():
            settings_form.save_with_slug()
            return redirect('user')
        else:
            settings_form = self.post_form(request.POST, request.FILES)
            context['form'] = settings_form
        return render(request, self.template_name, context=context)


class AddPage(LoginRequiredMixin, DataMixin, View):
    model = Post
    template_name = 'users/addpage.html'
    post_form = AddPostForm
    image_form = ImageForm
    tag_form = TagForm

    def get(self, request):
        context = self.get_user_context()
        context['title'] = 'Добавление поста'
        context['form'] = self.post_form
        context['image'] = self.image_form
        context['tags'] = self.tag_form
        return render(request, self.template_name, context=context)

    def post(self, request):
        user = request.user
        post_form = self.post_form(request.POST)
        image_form = self.image_form(request.POST, request.FILES, request=request)
        tag_form = self.tag_form(request.POST, request=request)
        context = self.get_user_context()
        context['title'] = 'Добавление поста'
        context['form'] = post_form
        context['image'] = image_form
        context['tags'] = tag_form

        if post_form.is_valid() and tag_form.is_valid() and image_form.is_valid():
            post_obj = post_form.save(commit=False)
            post_obj.user_id = user.pk
            post_obj.save()
            tag_form.save_for(post_obj)
            image_form.save_for(post_obj.pk, user.pk)
            return redirect('home')
        else:
            return render(request, self.template_name, context=context)


class ContactFormView(DataMixin, FormView):
    form_class = ContactForm
    template_name = 'users/contact.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Обратная связь')
        context.update(c_def)
        return context

    def form_valid(self, form):
        send_message(form.cleaned_data['name'], form.cleaned_data['email'], form.cleaned_data['content'])
        return redirect('home')


class LoginUser(DataMixin, LoginView):
    form_class = LoginForm
    template_name = 'registration/login.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Авторизация")
        context.update(c_def)
        return context


class RegisterUser(DataMixin, View):
    form_class = RegisterForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')

    def get(self, request):
        context = self.get_user_context()
        context['title'] = 'Регистрация'
        context['form'] = self.form_class

        return render(request, self.template_name, context=context)

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save_with_slag()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            send_email_verify(request, user)
            return redirect('confirm_email')
        context = {
            'form': form,
        }
        return render(request, self.template_name, context)


class ConfirmEmailView(DataMixin, View):
    model = User
    template_name = 'registration/confirm_email.html'

    def get(self, request):
        context = self.get_user_context()
        context['title'] = 'Подтверждение почты'

        return render(request, self.template_name, context=context)


class InvalidVerifyView(DataMixin, View):
    model = User
    template_name = 'registration/invalid_verify.html'

    def get(self, request):
        context = self.get_user_context()
        context['title'] = 'Что-то не так'
        return render(request, self.template_name, context=context)


class EmailVerify(View):
    def get(self, request, uidb64, token):
        user = self.get_user(uidb64)

        if user is not None and token_generator.check_token(user, token):
            user.email_verify = True
            user.save()
            login(request, user)
            return redirect('user')
        return redirect('invalid_verify')

    @staticmethod
    def get_user(uidb64):
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (
                TypeError,
                ValueError,
                OverflowError,
                User.DoesNotExist,
                ValidationError,
        ):
            user = None
        return user


def ajax_add_follower(request):
    if request.is_ajax():
        user_id = int(request.POST.get('user_id'))
        foreign_user_id = int(request.POST.get('foreign_user_id'))
        data = {
            'added': True,
            'user_id': user_id,
            'foreign_user_id': foreign_user_id
        }
        p_user = User.objects.get(id=user_id)
        f_user = User.objects.get(id=foreign_user_id)
        follow_inst = None
        for user in f_user.follows.all():
            if user.id == user_id:
                follow_inst = user
        try:
            f_user.objects.filter(follows__id=p_user.id)
        except Exception as e:
            f_user.follows.add(p_user)
        return JsonResponse(data)


def ajax_remove_follower(request):
    if request.is_ajax():
        user_id = int(request.POST.get('user_id'))
        foreign_user_id = int(request.POST.get('foreign_user_id'))
        data = {
            'removed': True,
            'user_id': user_id,
            'foreign_user_id': foreign_user_id
        }
        f_user = User.objects.get(id=foreign_user_id)
        f_user.follows.remove(User.objects.get(id=user_id))
        return JsonResponse(data)


def api_follow_info(request, user_id, foreign_user_id):
    p_user_f = User.objects.get(id=user_id).follows.all().count()
    f_user_f = User.objects.get(id=foreign_user_id).follows.all().count()
    user = User.objects.filter(id=request.user.id).values('id', 'username')
    f_user = User.objects.filter(id=user_id).values('id', 'username')
    response_list = []
    response_list.append({'follows_count': p_user_f})
    response_list.append({'followers_count': f_user_f})
    response_list.append({'user_that_followed': list(user)})
    response_list.append({'user_followed_by': list(f_user)})
    return JsonResponse(response_list, safe=False)


def ajax_add_like(request):
    if request.is_ajax():
        post_id = int(request.POST.get('post_id'))
        user_id = int(request.POST.get('user_id'))
        data = {
            'added': True,
            'post_id': post_id,
            'user_id': user_id
        }
        post_inst = Post.objects.get(id=post_id)
        user_inst = User.objects.get(id=user_id)

        try:
            like_inst = Like.objects.get(post=post_inst, liked_by=user_inst)
        except Exception as e:
            like = Like(post=post_inst, liked_by=user_inst, like=True)
            like.save()
        return JsonResponse(data)


def ajax_remove_like(request):
    if request.is_ajax():
        post_id = int(request.POST.get('post_id'))
        user_id = int(request.POST.get('user_id'))
        likes_id = int(request.POST.get('likes_id'))
        data = {
            'removed': True,
            'post_id': post_id,
            'user_id': user_id,
            'likes_id': likes_id
        }
        like = Like.objects.get(id=likes_id)
        like.delete()
        return JsonResponse(data)


def api_like_info(request, post_id):
    post = Post.objects.filter(id=post_id).annotate(likes_count=Count('like')).values('likes_count')
    likes = Like.objects.filter(post=post_id, liked_by=request.user.id).values('id', 'liked_by', 'like')
    response_list = []
    response_list.extend(post)
    response_list.append({'likes_from_users': list(likes)})

    return JsonResponse(response_list, safe=False)


class Followers(DataMixin, DetailView):
    model = User
    template_name = 'users/followers.html'
    pk_url_kwarg = 'user_id'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context_mixin = self.get_user_context(title="Подписчики")
        context_mixin['followers'] = context['user'].follows.all()
        context.update(context_mixin)
        return context


class Follows(DataMixin, DetailView):
    model = User
    template_name = 'users/follows.html'
    pk_url_kwarg = 'user_id'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context_mixin = self.get_user_context(title="Подписан")
        context_mixin['follows'] = get_folowers(context['user'])
        context.update(context_mixin)
        return context


class ForeignProfile(LoginRequiredMixin, DataMixin, View):
    model = User
    template_name = 'users/foreign_profile.html'

    def get(self, request, user_slug):
        context = self.get_user_context()
        context['user'] = request.user

        context_mixin = self.get_user_context(title=context['user'])
        context_mixin['foreign_user'] = User.objects.get(slug=user_slug)
        context_mixin['followers'] = context_mixin['foreign_user'].follows.all().count()
        context_mixin['follows'] = len(get_folowers(context_mixin['foreign_user']))
        context_mixin['user_images'] = Image.objects.filter(user=context_mixin['foreign_user'].pk).order_by('-id')
        context_mixin['user_images_count'] = len(context_mixin['user_images'])
        context.update(context_mixin)
        return render(request, self.template_name, context=context)

    def post(self, request, user_slug):
        context = self.get_user_context()
        context['user'] = request.user
        sub = request.POST.get('subscribe')
        unsub = request.POST.get('unsubscribe')
        context_mixin = self.get_user_context(title=context['user'])
        context_mixin['foreign_user'] = User.objects.get(slug=user_slug)
        context_mixin['followers'] = context_mixin['foreign_user'].follows.all().count()
        context_mixin['follows'] = len(get_folowers(context_mixin['foreign_user']))
        context_mixin['user_images'] = Image.objects.filter(user=context_mixin['foreign_user'].pk).order_by('-id')
        context_mixin['user_images_count'] = len(context_mixin['user_images'])
        context.update(context_mixin)
        # context = dict(list(context.items()) + list(context_mixin.items()))
        if sub is not None:
            subscribe(request, user_slug)
            return redirect('foreign_profile', user_slug=user_slug)
        elif unsub is not None:
            unsubscribe(request, user_slug)
            return redirect('foreign_profile', user_slug=user_slug)

        return render(request, self.template_name, context=context)


def pageNotFound(request, exception):
    return HttpResponseNotFound("<h1>Страница не найдена</h1>")


def serverError(request):
    return HttpResponseServerError("<h1>Ошибка сервера</h1>")

# class AddLikeView(View):
#     def post(self, request, *args, **kwargs):
#         post_id = int(request.POST.get('post_id'))
#         try:
#             user_id = int(request.POST.get('user_id'))
#         except Exception as e:
#             return redirect('login')
#         url_form = request.POST.get('url_form')
#
#         user_inst = User.objects.get(id=user_id)
#         post_inst = Post.objects.get(id=post_id)
#         try:
#             like_inst = Like.objects.get(post=post_inst, liked_by=user_inst)
#         except Exception as e:
#             like = Like(post=post_inst, liked_by=user_inst, like=True)
#             like.save()
#         return redirect(url_form)
#
#
# class RemoveLikeView(View):
#     def post(self, request, *args, **kwargs):
#         likes_id = int(request.POST.get('likes_id'))
#         url_form = request.POST.get('url_form')
#
#         like = Like.objects.get(id=likes_id)
#         like.delete()
#
#         return redirect(url_form)

# def index(request):
#     posts = Post.objects.all()
#     images = Image.objects.all()
#
#     context = {
#         'posts': posts,
#         'images': images,
#         'menu': menu,
#         'title': "Главная страница"
#     }
#     return render(request, "users/index.html", context=context)


# def addpage(request):
#     if request.method == 'POST':
#         post_form = AddPostForm(request.POST)
#         image_form = ImageForm(request.POST, request.FILES)
#         if post_form.is_valid():
#             new_post = Post(title=post_form.cleaned_data['title'],
#                             text=post_form.cleaned_data['text'],
#                             user_id=request.user.pk)
#             new_post.save()
#             if image_form.is_valid():
#                 for f in request.FILES.getlist('image'):
#                     new_image = Image(image=f, post_id=new_post.pk)
#                     new_image.save()
#                 return redirect('home')
#     else:
#         post_form = AddPostForm()
#         image_form = ImageForm()
#     return render(request, 'users/addpage.html',
#                   {'form': post_form, 'image': image_form, 'menu': menu, 'title': 'Добавление поста'})

# def addpage(request):
#     if request.method == 'POST':
#         post_form = AddPostForm(request.POST)
#         image_form = ImageForm(request.POST, request.FILES)
#         if post_form.is_valid():
#             new_post = Post(title=post_form.cleaned_data['title'],
#                             text=post_form.cleaned_data['text'],
#                             user_id=request.user.pk)
#             new_post.save()
#             if image_form.is_valid():
#                 for f in request.FILES.getlist('image'):
#                     new_image = Image(image=f, post_id=new_post.pk)
#                     new_image.save()
#                 return redirect('home')
#     else:
#         post_form = AddPostForm()
#         image_form = ImageForm()
#     return render(request, 'users/addpage.html',
#                   {'form': post_form, 'image': image_form, 'menu': menu, 'title': 'Добавление поста'})

# def show_post(request, post_id):
#     post = get_object_or_404(Post, pk=post_id)
#     context = {
#         'post': post,
#         'menu': menu,
#         'title': post.title
#     }
#     return render(request, 'users/post.html', context=context)

# def user(request):
#     user = get_object_or_404(User, pk=request.user.pk)
#     images = Image.objects.all()
#     context = {
#         'images': images,
#         'user': user,
#         'menu': menu,
#         'title': user.nic_name
#     }
#     return render(request, 'users/user.html', context=context)

# def index(request):
#     posts = Post.objects.all()
#     images = Image.objects.all()
#
#     context = {
#         'posts': posts,
#         'images': images,
#         'menu': menu,
#         'title': "Главная страница"
#     }
#     return render(request, "users/index.html", context=context)

# def post(self, request):
#     form = self.form_class(data=request.POST)
#
#     if form.is_valid():
#         user = form.get_user()
#         login(request, user)
#         return redirect('home')
#
#     context = {
#         'form': form,
#         'menu': self.get_user_context()['menu'],
#         'title': 'Авторизация'
#     }
#     return render(request, self.template_name, context)
