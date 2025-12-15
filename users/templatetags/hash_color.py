from django import template
import hashlib

register = template.Library()

@register.filter
def hash_color(value):
    h = hashlib.md5(value.encode()).hexdigest()
    return "#" + h[:6]
