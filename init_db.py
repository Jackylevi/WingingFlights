import sqlite3
import os

DATABASE_FILE = 'database.db'

db_path = os.path.join(os.path.dirname(__file__), DATABASE_FILE)

print(f"Database path: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions (
            email TEXT PRIMARY KEY,
            max_price INTEGER NOT NULL,
            min_days INTEGER NOT NULL,
            max_days INTEGER NOT NULL,
            origin_airport TEXT NOT NULL,
            subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    print("Subscriptions table created successfully.")

    conn.commit()
    conn.close()
except sqlite3.Error as e:
    print(f"An error occurred while creating the database: {e}")

print("Database initialized successfully.")
