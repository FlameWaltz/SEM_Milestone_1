"""Codebase A, refactored by extracting domain, validation and storage functions."""
from flask import Flask, jsonify, request
from checks import ValidationError, validate_booking, validate_quote
from reward import RATES_RM_PER_KG, calculate_reward
from storage import find_booking, save_booking

app = Flask(__name__)


@app.get('/api/materials')
def list_materials():
    return jsonify({'rates_rm_per_kg': RATES_RM_PER_KG})


@app.post('/api/quote')
def quote():
    try:
        item_type, weight = validate_quote(request.get_json(silent=True) or {})
        return jsonify({'item_type': item_type, 'weight_kg': weight,
                        'estimated_reward_rm': calculate_reward(item_type, weight)})
    except ValidationError as error:
        return jsonify({'error': str(error)}), 400


@app.post('/api/bookings')
def create_booking():
    try:
        fields = validate_booking(request.get_json(silent=True) or {})
        item_type, weight = fields[1], fields[2]
        reward = calculate_reward(item_type, weight)
        booking_id = save_booking(*fields, reward)
        return jsonify({'booking_id': booking_id, 'estimated_reward_rm': reward,
                        'status': 'pending'}), 201
    except ValidationError as error:
        return jsonify({'error': str(error)}), 400


@app.get('/api/bookings/<int:booking_id>')
def get_booking(booking_id):
    record = find_booking(booking_id)
    if record is None:
        return jsonify({'error': 'Booking not found'}), 404
    return jsonify(record)


if __name__ == '__main__':
    app.run(debug=False)
