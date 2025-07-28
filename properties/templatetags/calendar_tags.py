from django import template

register = template.Library()

@register.filter
def get_availability(availability_data, day):
    """Get availability data for a specific day"""
    return availability_data.get(day, {}) 