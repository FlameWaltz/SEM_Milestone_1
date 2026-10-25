"""Codebase B: layered Flask API with same contract as Codebase A."""
import os
from flask import Flask, jsonify, request
from reward import RATES_RM_PER_KG
from repository import BookingRepository
from service import BookingService, ValidationError

app = Flask(__name__)
service = BookingService(BookingRepository(os.environ.get('SEM_DB_PATH', 'recycling_b.db')))


@app.get('/api/materials')
def list_materials():
    return jsonify({'rates_rm_per_kg': RATES_RM_PER_KG})


@app.post('/api/quote')
def quote():
    try:
        return jsonify(service.quote(request.get_json(silent=True) or {}))
    except ValidationError as error:
        return jsonify({'error': str(error)}), 400


@app.post('/api/bookings')
def create_booking():
    try:
        return jsonify(service.create_booking(request.get_json(silent=True) or {})), 201
    except ValidationError as error:
        return jsonify({'error': str(error)}), 400


@app.get('/api/bookings/<int:booking_id>')
def get_booking(booking_id):
    try:
        return jsonify(service.get_booking(booking_id))
    except LookupError as error:
        return jsonify({'error': str(error)}), 404


if __name__ == '__main__':
    app.run(debug=False)
