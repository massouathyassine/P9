from django import template

register = template.Library()


@register.filter
def model_type(instance):
    return type(instance).__name__

@register.filter
def star_range(value):
    return range(value)
