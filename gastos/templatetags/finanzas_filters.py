from decimal import Decimal
from django import template

register = template.Library()


@register.filter
def formato_monto(value):
    if value in (None, ''):
        return '$0,00'

    try:
        numero = Decimal(str(value))
    except (TypeError, ValueError, ArithmeticError):
        return '$0,00'

    formato = f'{numero:,.2f}'
    formato = formato.replace(',', 'X')
    formato = formato.replace('.', ',')
    formato = formato.replace('X', '.')
    return f'${formato}'
