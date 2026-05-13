from django import template

register = template.Library()

@register.filter
def grade_count(submissions, grade):
    return sum(1 for s in submissions if s.grade_letter == grade)

@register.filter  
def mul(value, arg):
    try: return float(value) * float(arg)
    except: return 0

@register.filter
def div(value, arg):
    try: return float(value) / float(arg) if float(arg) else 0
    except: return 0

@register.filter
def subtract(value, arg):
    try: return float(value) - float(arg)
    except: return 0

@register.filter
def get_item(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(str(key), '')
    return ''
