import sqlite3

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
    conn = get_connection()
    cur = conn.cursor()

    print("DEBUG book_slot:")
    print("  slot_id =", slot_id)

    cur.execute("SELECT id, status FROM slots WHERE id = ?", (slot_id,))
    row = cur.fetchone()
    print("  DB row =", row)

    cur.execute("""
        UPDATE slots
        SET status = 'booked',
            user_id = ?
        WHERE id = ?
          AND status = 'available'
    """, (user_id, slot_id))

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
