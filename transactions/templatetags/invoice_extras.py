from django import template

register = template.Library()

@register.filter
def price_after_discount(item_price, sale):
    try:
        sub_total = float(sale.sub_total)
        discount_amount = float(sale.discount_amount)
        if sub_total > 0:
            discount_share = (float(item_price) / sub_total) * discount_amount
            return float(item_price) - discount_share
        else:
            return float(item_price)
    except Exception:
        return item_price
