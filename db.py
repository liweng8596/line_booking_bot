import sqlite3
from datetime import date, timedelta

DB_NAME = "booking.db"

# ================= 基本 =================


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS slots (
        id TEXT PRIMARY KEY,
        date TEXT,
        start_time TEXT,
        end_time TEXT,
        status TEXT,
        user_id TEXT
    )
    """)

    conn.commit()
    conn.close()


# ================= 查詢 =================
def get_available_dates():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT date
        FROM slots
        WHERE status = 'available'
        ORDER BY date
    """)

    dates = [row[0] for row in cursor.fetchall()]
    conn.close()
    return dates


def get_available_slots_by_date(date):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, date, start_time, end_time
        FROM slots
        WHERE date = ?
          AND status = 'available'
        ORDER BY start_time
    """, (date,))

    rows = cursor.fetchall()
    conn.close()
    return rows


def get_all_slots_by_date(date):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, date, start_time, end_time, status, user_id
        FROM slots
        WHERE date = ?
        ORDER BY start_time
    """, (date,))

    rows = cursor.fetchall()
    conn.close()
    return rows


def get_user_booked_slots(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, date, start_time, end_time
        FROM slots
        WHERE status = 'booked'
          AND user_id = ?
        ORDER BY date, start_time
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()
    return rows


# ================= 動作 =================
def book_slot(slot_id, user_id):
    """
    slot_id 格式：YYYY-MM-DDT10:00-11:00
    """
    try:
        date_part, time_part = slot_id.split("T", 1)
        start, end = time_part.split("-", 1)
    except ValueError:
        print("❌ slot_id format error:", slot_id)
        return False

    conn = get_connection()
    cur = conn.cursor()

    print("DEBUG book_slot:")
    print("  date =", date_part)
    print("  start =", start)
    print("  end =", end)

    cur.execute("""
        UPDATE slots
        SET status = 'booked',
            user_id = ?
        WHERE date = ?
          AND start_time = ?
          AND end_time = ?
          AND status = 'available'
    """, (user_id, date_part, start, end))

    print("  rowcount =", cur.rowcount)

    success = cur.rowcount == 1
    conn.commit()
    conn.close()
    return success


def cancel_slot(slot_id, user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE slots
        SET status = 'available',
            user_id = NULL
        WHERE id = ?
          AND user_id = ?
    """, (slot_id, user_id))

    success = cur.rowcount == 1
    conn.commit()
    conn.close()
    return success


def lock_slot(slot_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE slots
        SET status = 'blocked'
        WHERE id = ?
    """, (slot_id,))

    conn.commit()
    conn.close()


def unlock_slot(slot_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE slots
        SET status = 'available',
            user_id = NULL
        WHERE id = ?
    """, (slot_id,))

    conn.commit()
    conn.close()


def get_tomorrow_bookings():
    tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_id, date, start_time, end_time
        FROM slots
        WHERE date = ?
          AND booked = 1
    """, (tomorrow,))

    rows = cursor.fetchall()
    conn.close()

    return rows


def get_tomorrow_schedule_for_coach():
    tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_id, start_time, end_time
        FROM slots
        WHERE date = ?
          AND booked = 1
        ORDER BY start_time
    """, (tomorrow,))

    rows = cursor.fetchall()
    conn.close()

    return tomorrow, rows
