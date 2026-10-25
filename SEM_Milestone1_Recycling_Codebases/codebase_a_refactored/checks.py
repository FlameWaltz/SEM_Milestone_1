"""Extracted validation from the original create_booking() and quote() handlers."""
from datetime import date
from reward import RATES_RM_PER_KG


class ValidationError(ValueError):
    pass


def validate_quote(data):
    item_type = data.get('item_type')
    weight = data.get('weight_kg')
    if not isinstance(item_type, str) or not item_type.strip():
        raise ValidationError('Invalid item_type')
    item_type = item_type.strip().lower()
    if isinstance(weight, bool) or not isinstance(weight, (int, float)) or weight <= 0:
        raise ValidationError('Invalid weight_kg')
    if item_type not in RATES_RM_PER_KG:
        raise ValidationError('Unsupported item_type')
    return item_type, weight


def validate_booking(data):
    user_id = data.get('user_id')
    if isinstance(user_id, bool) or not isinstance(user_id, int) or user_id <= 0:
        raise ValidationError('Invalid user_id')
    item_type, weight = validate_quote(data)
    address = data.get('address')
    if not isinstance(address, str) or not address.strip():
        raise ValidationError('Invalid address')
    pickup_date = data.get('pickup_date')
    if not isinstance(pickup_date, str):
        raise ValidationError('Invalid pickup_date')
    try:
        if date.fromisoformat(pickup_date).isoformat() != pickup_date:
            raise ValidationError('Invalid pickup_date')
    except ValueError:
        raise ValidationError('Invalid pickup_date')
    return user_id, item_type, weight, address.strip(), pickup_date
