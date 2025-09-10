from django import template
import random

register = template.Library()

@register.filter
def lookup(dictionary, key):
    """
    Template filter to look up dictionary values by key.
    Usage: {{ dict|lookup:key }}
    """
    if isinstance(dictionary, dict) and key in dictionary:
        return dictionary[key]
    return None

@register.filter
def get_item(dictionary, key):
    """
    Alternative template filter to get dictionary items.
    Usage: {{ dict|get_item:key }}
    """
    try:
        return dictionary[key]
    except (KeyError, TypeError):
        return None

@register.filter
def add_values(value_list):
    """
    Template filter to sum a list of values.
    Usage: {{ list|add_values }}
    """
    try:
        if isinstance(value_list, (list, tuple)):
            return sum(float(x) for x in value_list if x is not None)
        return 0
    except (ValueError, TypeError):
        return 0

@register.filter
def max_by(items, attribute):
    """
    Template filter to find the maximum item by attribute.
    Usage: {{ items|max_by:'attribute_name' }}
    """
    try:
        if hasattr(items, 'values'):
            items = items.values()
        return max(items, key=lambda x: getattr(x, attribute, 0) if hasattr(x, attribute) else x.get(attribute, 0))
    except (ValueError, TypeError, AttributeError):
        return None

@register.filter
def mul(value, multiplier):
    """
    Template filter to multiply values.
    Usage: {{ value|mul:5 }}
    """
    try:
        return float(value) * float(multiplier)
    except (ValueError, TypeError):
        return 0

@register.simple_tag
def random(min_val, max_val):
    """
    Template tag to generate random numbers.
    Usage: {% random 10 100 %}
    """
    try:
        return random.randint(int(min_val), int(max_val))
    except (ValueError, TypeError):
        return 0

@register.filter
def percentage(value, total):
    """
    Calculate percentage of value from total.
    Usage: {{ value|percentage:total }}
    """
    try:
        if float(total) == 0:
            return 0
        return round((float(value) / float(total)) * 100, 2)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def format_trend(trend_value):
    """
    Format trend values with appropriate icons.
    Usage: {{ trend|format_trend }}
    """
    try:
        if isinstance(trend_value, str):
            if trend_value.lower() == 'increasing':
                return '📈 Increasing'
            elif trend_value.lower() == 'decreasing':
                return '📉 Decreasing'
            else:
                return '➡️ Stable'
        return str(trend_value)
    except:
        return 'Unknown'

@register.filter
def dict_values(dictionary):
    """
    Get values from dictionary as list.
    Usage: {{ dict|dict_values }}
    """
    try:
        return list(dictionary.values())
    except (AttributeError, TypeError):
        return []

@register.filter
def slice_list(value_list, slice_str):
    """
    Slice a list similar to Python slicing.
    Usage: {{ list|slice_list:"0:5" }}
    """
    try:
        if ':' in slice_str:
            start, end = slice_str.split(':')
            start = int(start) if start else None
            end = int(end) if end else None
            return value_list[start:end]
        else:
            index = int(slice_str)
            return [value_list[index]]
    except (ValueError, IndexError, TypeError):
        return []

@register.inclusion_tag('ai_forecast/widgets/metric_card.html')
def metric_card(title, value, label, icon=None, color='primary'):
    """
    Inclusion tag for metric cards.
    Usage: {% metric_card "Title" value "Label" icon="fas fa-chart" color="success" %}
    """
    return {
        'title': title,
        'value': value,
        'label': label,
        'icon': icon,
        'color': color,
    }

@register.inclusion_tag('ai_forecast/widgets/trend_indicator.html')
def trend_indicator(trend, value=None):
    """
    Inclusion tag for trend indicators.
    Usage: {% trend_indicator "increasing" 5.2 %}
    """
    return {
        'trend': trend,
        'value': value,
    }