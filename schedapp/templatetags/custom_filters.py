from django import template
import re

register = template.Library()

@register.filter(name='remove_symbols')
def remove_symbols(value):
    # Replace any symbols you want to remove with an empty string
    cleaned_value = re.sub(r'[^\w\s]', '', value)
    return cleaned_value