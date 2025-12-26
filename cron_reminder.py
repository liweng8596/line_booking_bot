import os
from dotenv import load_dotenv
from linebot import LineBotApi

from db import get_tomorrow_bookings, get_tomorrow_schedule_for_coach
from reminder import send_reminder
from coach_reminder import build_coach_schedule_message

load_dotenv()

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))

# 你的教練 LINE user_id（你已經有）
COACH_IDS = {
    "U17fdee62c51888ebea77d8b696eb38e4",
}


def main():
    # ===== 學員提醒 =====
    bookings = get_tomorrow_bookings()
    if bookings:
        send_reminder(line_bot_api, bookings)

    # ===== 教練課表 =====
    date_str, rows = get_tomorrow_schedule_for_coach()
    coach_flex = build_coach_schedule_flex(date_str, rows)

    for coach_id in COACH_IDS:
        line_bot_api.push_message(coach_id, coach_msg)


if __name__ == "__main__":
    main()
