"""SQLite persistence adapter: no HTTP or business calculations."""
import sqlite3


class BookingRepository:
    def __init__(self, db_path):
        self.db_path = db_path

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute('''CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL, item_type TEXT NOT NULL,
            weight_kg REAL NOT NULL, address TEXT NOT NULL,
            pickup_date TEXT NOT NULL, estimated_reward_rm REAL NOT NULL,
            status TEXT NOT NULL)''')
        return conn

    def save(self, user_id, item_type, weight, address, pickup_date, reward):
        with self._connect() as conn:
            cursor = conn.execute('''INSERT INTO bookings
                (user_id,item_type,weight_kg,address,pickup_date,estimated_reward_rm,status)
                VALUES (?,?,?,?,?,?,?)''',
                (user_id,item_type,weight,address,pickup_date,reward,'pending'))
            return cursor.lastrowid

    def find(self, booking_id):
        with self._connect() as conn:
            result = conn.execute('SELECT * FROM bookings WHERE id=?',
                                  (booking_id,)).fetchone()
            return dict(result) if result is not None else None
