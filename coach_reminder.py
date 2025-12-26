from datetime import datetime
from linebot.models import FlexSendMessage


def build_coach_schedule_flex(date_str, rows):
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    weekday = ["一", "二", "三", "四", "五", "六", "日"][dt.weekday()]
    display_date = f"{dt.month}/{dt.day}（週{weekday}）"

    contents = [
        {
            "type": "text",
            "text": "🧑‍🏫 明天課表提醒",
            "weight": "bold",
            "size": "lg"
        },
        {
            "type": "text",
            "text": f"📅 {display_date}",
            "size": "sm",
            "color": "#666666"
        }
    ]

    if not rows:
        contents.append({
            "type": "text",
            "text": "🎉 明天沒有任何課程",
            "margin": "md"
        })
    else:
        for _, start, end in rows:
            contents.append({
                "type": "text",
                "text": f"⏰ {start}–{end}｜學員",
                "margin": "sm"
            })

        contents.append({
            "type": "text",
            "text": f"共 {len(rows)} 堂課",
            "size": "sm",
            "color": "#666666",
            "margin": "md"
        })

    return FlexSendMessage(
        alt_text="明天課表提醒",
        contents={
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": contents
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "button",
                        "style": "primary",
                        "action": {
                            "type": "postback",
                            "label": "📋 查看明天詳細課表",
                            "data": "COACH_VIEW_TOMORROW"
                        }
                    }
                ]
            }
        }
    )
