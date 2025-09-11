from django import template

register = template.Library()

@register.filter
def add_class(field, css_class):
    """
    Add CSS class to form field widget
    """
    if hasattr(field, 'as_widget'):
        return field.as_widget(attrs={'class': css_class})
    return field