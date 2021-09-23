from django import template

register = template.Library()


@register.filter
def form_to_class_name(value):
    return value.__class__._meta.model.__name__


@register.filter
def form_to_list_url(value):
    return value.__class__._meta.model.get_list_url()


@register.filter
def object_to_class_name(value):
    return value.__class__.__name__
