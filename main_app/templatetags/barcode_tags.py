from django import template
import base64

register = template.Library()

@register.filter
def b64encode(value):
    """Encode binary data as base64 for display in HTML"""
    if value:
        return base64.b64encode(value).decode('utf-8')
    return ''