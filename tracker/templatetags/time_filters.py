from django import template
register = template.Library()
@register.filter
def hours(minutes):
    minutes = int(minutes)
    h = minutes // 60
    m = minutes % 60
    if h == 0:
        return f'{m} мин'
    return f'{h} ч {m} мин'
