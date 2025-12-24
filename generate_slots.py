from datetime import datetime, timedelta
import sqlite3

DB_NAME = "booking.db"

# 🔒 固定課設定
FIXED_CLASSES = [
    {"weekday": 0, "start": "19:00", "end": "20:00"},  # 週一
    {"weekday": 4, "start": "17:00", "end": "17:45"},  # 週三
]

# 🕒 教練可上課時段（每天）
DAILY_TIME_SLOTS = [
    ("10:00", "11:00"),
    ("11:00", "12:00"),
    ("14:00", "15:00"),
    ("15:00", "16:00"),
    ("19:00", "20:00"),
]

def get_next_week_dates():
    today = datetime.today()
    start = today + timedelta(days=(7 - today.weekday()))
    return [start + timedelta(days=i) for i in range(7)]

def is_fixed_class(date, start_time):
    for fc in FIXED_CLASSES:
        if date.weekday() == fc["weekday"] and start_time == fc["start"]:
            return True
    return False

def generate_slots():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    for date in get_next_week_dates():
        date_str = date.strftime("%Y-%m-%d")

        for start_time, end_time in DAILY_TIME_SLOTS:
            slot_id = f"{date_str}T{start_time}"

            status = "blocked" if is_fixed_class(date, start_time) else "available"

            cursor.execute("""
            INSERT OR IGNORE INTO slots (id, date, start_time, end_time, status, user_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (slot_id, date_str, start_time, end_time, status, None))

    conn.commit()
    conn.close()
    print("下週課表已產生完成")

if __name__ == "__main__":
    generate_slots()
