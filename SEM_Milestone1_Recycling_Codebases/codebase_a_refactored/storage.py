"""Extracted database operations from the original HTTP handlers."""
import os
import sqlite3

DB_PATH = os.environ.get('SEM_DB_PATH', 'recycling_a_refactored.db')
SCHEMA = '''CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL, item_type TEXT NOT NULL,
    weight_kg REAL NOT NULL, address TEXT NOT NULL,
    pickup_date TEXT NOT NULL, estimated_reward_rm REAL NOT NULL,
    status TEXT NOT NULL)'''


def save_booking(user_id, item_type, weight, address, pickup_date, reward):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(SCHEMA)
        cursor = conn.execute('''INSERT INTO bookings
            (user_id,item_type,weight_kg,address,pickup_date,estimated_reward_rm,status)
            VALUES (?,?,?,?,?,?,?)''',
            (user_id, item_type, weight, address, pickup_date, reward, 'pending'))
        return cursor.lastrowid


def find_booking(booking_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute(SCHEMA)
        row = conn.execute('SELECT * FROM bookings WHERE id=?', (booking_id,)).fetchone()
        return dict(row) if row is not None else None
