from datetime import datetime
from linebot.models import TextSendMessage


def send_reminder(line_bot_api, bookings):
    for user_id, date, start, end in bookings:
        dt = datetime.strptime(date, "%Y-%m-%d")
        weekday = ["一", "二", "三", "四", "五", "六", "日"][dt.weekday()]
        display_date = f"{dt.month}/{dt.day}（週{weekday}）"

        message = (
            "👋 提醒你明天有一堂課喔！\n\n"
            f"📅 {display_date}\n"
            f"⏰ {start}–{end}\n\n"
            "如果需要改時間，現在跟我說就可以 😊"
        )

        line_bot_api.push_message(
            user_id,
            TextSendMessage(text=message)
        )
