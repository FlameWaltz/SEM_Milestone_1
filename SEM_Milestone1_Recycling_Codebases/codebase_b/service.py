"""Application business rules shared by quote and booking flows."""
from datetime import date
from reward import RATES_RM_PER_KG, calculate_reward


class ValidationError(ValueError):
    pass


class BookingService:
    def __init__(self, repository):
        self.repository = repository

    def validate_quote(self, data):
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

    def quote(self, data):
        item_type, weight = self.validate_quote(data)
        return {'item_type': item_type, 'weight_kg': weight,
                'estimated_reward_rm': calculate_reward(item_type, weight)}

    def create_booking(self, data):
        user_id = data.get('user_id')
        if isinstance(user_id, bool) or not isinstance(user_id, int) or user_id <= 0:
            raise ValidationError('Invalid user_id')
        item_type, weight = self.validate_quote(data)
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
        reward = calculate_reward(item_type, weight)
        booking_id = self.repository.save(user_id, item_type, weight, address.strip(),
                                          pickup_date, reward)
        return {'booking_id': booking_id, 'estimated_reward_rm': reward,
                'status': 'pending'}

    def get_booking(self, booking_id):
        record = self.repository.find(booking_id)
        if record is None:
            raise LookupError('Booking not found')
        return record
