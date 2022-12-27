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



