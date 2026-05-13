"""
Matematik formulalarni avtomatik tanish va MathJax uchun $...$ ichiga olish.

Misol:
  "x^2 + x^3"     → "$x^2 + x^3$"
  "salom dunyo"   → "salom dunyo"   (formula yo'q)
  "$x^2$ - bor"   → "$x^2$ - bor"   (allaqachon $ ichida)
"""
import re
from django import template
from django.utils.safestring import mark_safe
from django.template.defaultfilters import stringfilter

register = template.Library()


# LaTeX yoki matematik belgilari
MATH_PATTERN = re.compile(r'[\^_]|\\[a-zA-Z]+|\\frac|\\sqrt|\\sum|\\int|\\lim|\\alpha|\\beta|\\pi')


@register.filter(name='auto_math')
@stringfilter
def auto_math(value):
    """
    Matnni ko'rib, formulalarni avtomatik $...$ ichiga oladi.
    Allaqachon $...$ yoki \\(...\\) ichida bo'lsa tegmaydi.
    """
    if not value:
        return ''

    # Allaqachon LaTeX wrapper bormi?
    if '$' in value or '\\(' in value or '\\[' in value:
        return mark_safe(value)

    # Matematik belgilar bormi?
    if not MATH_PATTERN.search(value):
        return value

    # Butun matnni $...$ ichiga olamiz
    # Lekin ehtiyot bo'lib — agar matnda oddiy gap ham bo'lsa,
    # faqat formulali qismni o'rab olishga harakat qilamiz

    # Sodda variant: oraliqlarga qarab tokenlarga bo'lib chiqamiz
    parts = re.split(r'\s+', value)
    result = []
    for p in parts:
        if MATH_PATTERN.search(p):
            # Bu token formula — $...$ ichiga olamiz
            # Lekin oxiridagi tinish belgilarini ajratamiz
            m = re.match(r'^(.*?)([.,;:!?]?)$', p)
            if m:
                formula, punct = m.group(1), m.group(2)
                result.append(f'${formula}${punct}')
            else:
                result.append(f'${p}$')
        else:
            result.append(p)

    return mark_safe(' '.join(result))