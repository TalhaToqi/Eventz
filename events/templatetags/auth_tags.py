from django import template

register = template.Library()

@register.filter
def is_organizer(user):
    return user.groups.filter(name='Organizers').exists()
