"""Codebase A: single-file Flask API for a recycling booking prototype.
Experiment rates are illustrative and are NOT Trash4Cash's official rates.
"""
import os
import sqlite3
from datetime import date
from flask import Flask, jsonify, request

app = Flask(__name__)
DB_PATH = os.environ.get('SEM_DB_PATH', 'recycling_a.db')


@app.get('/api/materials')
def list_materials():
    return jsonify({'rates_rm_per_kg': {
        'paper': 0.50, 'plastic': 0.80, 'metal': 1.20, 'ewaste': 2.50
    }})


@app.post('/api/quote')
def quote():
    data = request.get_json(silent=True) or {}
    item_type = data.get('item_type')
    weight = data.get('weight_kg')
    if not isinstance(item_type, str) or not item_type.strip():
        return jsonify({'error': 'Invalid item_type'}), 400
    item_type = item_type.strip().lower()
    if isinstance(weight, bool) or not isinstance(weight, (int, float)) or weight <= 0:
        return jsonify({'error': 'Invalid weight_kg'}), 400
    if item_type == 'paper':
        rate = 0.50
    elif item_type == 'plastic':
        rate = 0.80
    elif item_type == 'metal':
        rate = 1.20
    elif item_type == 'ewaste':
        rate = 2.50
    else:
        return jsonify({'error': 'Unsupported item_type'}), 400
    return jsonify({'item_type': item_type, 'weight_kg': weight,
                    'estimated_reward_rm': round(weight * rate, 2)})


@app.post('/api/bookings')
def create_booking():
    data = request.get_json(silent=True) or {}
    user_id = data.get('user_id')
    item_type = data.get('item_type')
    weight = data.get('weight_kg')
    address = data.get('address')
    pickup_date = data.get('pickup_date')
    if isinstance(user_id, bool) or not isinstance(user_id, int) or user_id <= 0:
        return jsonify({'error': 'Invalid user_id'}), 400
    if not isinstance(item_type, str) or not item_type.strip():
        return jsonify({'error': 'Invalid item_type'}), 400
    item_type = item_type.strip().lower()
    if isinstance(weight, bool) or not isinstance(weight, (int, float)) or weight <= 0:
        return jsonify({'error': 'Invalid weight_kg'}), 400
    if not isinstance(address, str) or not address.strip():
        return jsonify({'error': 'Invalid address'}), 400
    address = address.strip()
    if not isinstance(pickup_date, str):
        return jsonify({'error': 'Invalid pickup_date'}), 400
    try:
        if date.fromisoformat(pickup_date).isoformat() != pickup_date:
            return jsonify({'error': 'Invalid pickup_date'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid pickup_date'}), 400
    if item_type == 'paper':
        rate = 0.50
    elif item_type == 'plastic':
        rate = 0.80
    elif item_type == 'metal':
        rate = 1.20
    elif item_type == 'ewaste':
        rate = 2.50
    else:
        return jsonify({'error': 'Unsupported item_type'}), 400
    reward = round(weight * rate, 2)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL, item_type TEXT NOT NULL,
            weight_kg REAL NOT NULL, address TEXT NOT NULL,
            pickup_date TEXT NOT NULL, estimated_reward_rm REAL NOT NULL,
            status TEXT NOT NULL)''')
        cursor = conn.execute('''INSERT INTO bookings
            (user_id,item_type,weight_kg,address,pickup_date,estimated_reward_rm,status)
            VALUES (?,?,?,?,?,?,?)''',
            (user_id, item_type, weight, address, pickup_date, reward, 'pending'))
        booking_id = cursor.lastrowid
    return jsonify({'booking_id': booking_id, 'estimated_reward_rm': reward,
                    'status': 'pending'}), 201


@app.get('/api/bookings/<int:booking_id>')
def get_booking(booking_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute('''CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL, item_type TEXT NOT NULL,
            weight_kg REAL NOT NULL, address TEXT NOT NULL,
            pickup_date TEXT NOT NULL, estimated_reward_rm REAL NOT NULL,
            status TEXT NOT NULL)''')
        result = conn.execute('SELECT * FROM bookings WHERE id=?', (booking_id,)).fetchone()
    if result is None:
        return jsonify({'error': 'Booking not found'}), 404
    return jsonify(dict(result))


if __name__ == '__main__':
    app.run(debug=False)
