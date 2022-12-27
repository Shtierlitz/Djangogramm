from django.core.mail import EmailMessage
import datetime
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator as token_generator

from users.models import *

menu = [{'title': "О сайте", 'url_name': "about"},
        {'title': "Личный кабинет", 'url_name': 'user'},
        {'title': "Добавить пост", 'url_name': "add_page"},
        {'title': "Обратная связь", 'url_name': "contact"}]


class DataMixin:
    def get_user_context(self, **kwargs):
        context = kwargs
        images = Image.objects.all()
        user_menu = menu.copy()
        if not self.request.user.is_authenticated:
            user_menu.pop(1)
            user_menu.pop(1)
        context['menu'] = user_menu
        context['images'] = images
        return context


def send_email_verify(request, user):
    current_site = get_current_site(request)
    context = {
        'user': user,
        'domain': current_site.domain,
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "token": token_generator.make_token(user),
    }
    message = render_to_string(
        'registration/verify_email.html',
        context=context
    )
    email = EmailMessage(
        'Verify email',
        message,
        to=[user.email],
    )
    email.send()


def tag_creator(string) -> list:
    """Creates list of #tags and avoid creation of empty "#"-tag if space in the and."""
    lst = []
    s = string.split(',')
    for _ in s:
        st = _.replace(" ", "")
        st = '#' + st
        lst.append(st)
    if lst[-1][-1] == '#':
        del lst[-1]
    return lst


def get_d_m_y(param) -> str:
    """Returns date, month, or year string"""
    date_month_year = str(datetime.datetime.utcnow())
    if param == 'd':
        return date_month_year[8:10]
    if param == 'm':
        return date_month_year[5:7]
    if param == 'y':
        return date_month_year[0:4]
