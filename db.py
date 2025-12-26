import sqlite3
from datetime import date, timedelta, datetime

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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS date_overrides (
        date TEXT PRIMARY KEY,
        status TEXT NOT NULL CHECK (status IN ('open', 'closed')),
        reason TEXT,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

# ================= 判斷某天是否開課 =================


def is_open_date(date_str: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT status FROM date_overrides WHERE date = ?",
        (date_str,)
    )
    row = cur.fetchone()
    conn.close()

    if row:
        return row[0] == "open"

    weekday = datetime.strptime(date_str, "%Y-%m-%d").weekday()
    return weekday <= 3   # 週一～週四開

# ================= 查詢 =================


def get_available_dates():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT DISTINCT date
        FROM slots
        WHERE status = 'available'
        ORDER BY date
    """)
    rows = cur.fetchall()
    conn.close()

    return [d for (d,) in rows if is_open_date(d)]


def get_available_slots_by_date(date):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT date, start_time, end_time
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
        SELECT date, start_time, end_time, status, user_id
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
        SELECT date, start_time, end_time
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
    try:
        date_part, time_part = slot_id.split("T", 1)
        start, end = time_part.split("-", 1)
    except ValueError:
        return False

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE slots
        SET status = 'booked',
            user_id = ?
        WHERE date = ?
          AND start_time = ?
          AND end_time = ?
          AND status = 'available'
    """, (user_id, date_part, start, end))

    success = cur.rowcount == 1
    conn.commit()
    conn.close()
    return success


def get_open_status_for_range(days: int = 14):
    """
    回傳未來 N 天的 (date_str, status, source)
    status: 'open' / 'closed'
    source: 'default' / 'override'
    """
    today = date.today()
    results = []

    for i in range(days):
        d = today + timedelta(days=i)
        date_str = d.strftime("%Y-%m-%d")

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT status FROM date_overrides WHERE date = ?",
            (date_str,)
        )
        row = cur.fetchone()
        conn.close()

        if row:
            results.append((date_str, row[0], "override"))
        else:
            weekday = d.weekday()
            if weekday <= 3:
                results.append((date_str, "open", "default"))
            else:
                results.append((date_str, "closed", "default"))

    return results


def cancel_slot_by_time(date_str, start_time, end_time, user_id):
    """
    取消指定時段的預約（使用 date + time）
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE slots
        SET status = 'available',
            user_id = NULL
        WHERE date = ?
          AND start_time = ?
          AND end_time = ?
          AND status = 'booked'
          AND user_id = ?
    """, (date_str, start_time, end_time, user_id))

    success = cur.rowcount == 1
    conn.commit()
    conn.close()
    return success
