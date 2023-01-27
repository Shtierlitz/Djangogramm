from django import template

from users.models import User, Image

register = template.Library()

@register.simple_tag()
def user_post(user_id):
    return User.objects.get(id=user_id)

@register.simple_tag()
def post_image(post_id, post_1=None):
    if not post_1:
        try:
            image_list = Image.objects.filter(post=post_id)
            return image_list
        except Exception as e:
            return None
    try:
        image_list = Image.objects.filter(post=post_id)
        return image_list[0]
    except Exception as e:
        return None

@register.simple_tag(takes_context=True)
def is_follow(context, user_id):
    request = context['request']
    foreign_user = User.objects.get(id=user_id)
    for user in foreign_user.follows.all():
        if user.id == request.user.id:
            return True
    return False



@register.simple_tag()
def count_follows(user_id):
    count = User.objects.get(id=user_id).follows.all().count()
    return count


@register.simple_tag(takes_context=True)
def is_subscribed(context, user):
    request = context['request']
    try:
        subscriber = User.objects.get(pk=user.pk).follows.get(pk=request.user.id)
    except Exception as e:
        subscriber = False
    return subscriber

