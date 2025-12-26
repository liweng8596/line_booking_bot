from datetime import datetime
from linebot.models import FlexSendMessage


def build_reminder_flex(slot_id, date, start, end):
    dt = datetime.strptime(date, "%Y-%m-%d")
    weekday = ["一", "二", "三", "四", "五", "六", "日"][dt.weekday()]
    display_date = f"{dt.month}/{dt.day}（週{weekday}）"

    return {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
                {
                    "type": "text",
                    "text": "👋 明天上課提醒",
                    "weight": "bold",
                    "size": "lg"
                },
                {
                    "type": "text",
                    "text": f"📅 {display_date}\n⏰ {start}–{end}",
                    "wrap": True
                },
                {
                    "type": "text",
                    "text": "需要調整嗎？",
                    "size": "sm",
                    "color": "#666666"
                }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {
                    "type": "button",
                    "style": "secondary",
                    "action": {
                        "type": "postback",
                        "label": "🔄 改期",
                        "data": f"REMINDER_RESCHEDULE|{slot_id}"
                    }
                },
                {
                    "type": "button",
                    "style": "danger",
                    "action": {
                        "type": "postback",
                        "label": "❌ 取消",
                        "data": f"REMINDER_CANCEL|{slot_id}"
                    }
                }
            ]
        }
    }


def send_reminder(line_bot_api, bookings):
    for user_id, date, start, end in bookings:
        slot_id = f"{date}T{start}-{end}"
        flex = build_reminder_flex(slot_id, date, start, end)

        line_bot_api.push_message(
            user_id,
            FlexSendMessage(
                alt_text="明天上課提醒",
                contents=flex
            )
        )
