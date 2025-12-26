from datetime import datetime, date as today_date

WEEKDAY_MAP = {
    0: "一",
    1: "二",
    2: "三",
    3: "四",
    4: "五",
    5: "六",
    6: "日",
}


def build_date_picker(dates):
    buttons = []
    today = today_date.today()

    for d in dates:
        # d 格式：YYYY-MM-DD
        dt = datetime.strptime(d, "%Y-%m-%d")
        weekday = WEEKDAY_MAP[dt.weekday()]

        # ===== UX：今天 / 明天提示 =====
        tag = ""
        delta = (dt.date() - today).days
        if delta == 0:
            tag = "（今天）"
        elif delta == 1:
            tag = "（明天）"

        # 顯示用 label（人類友善）
        label = f"{dt.month}/{dt.day}{tag}（週{weekday}）"

        buttons.append({
            "type": "button",
            "style": "secondary",
            "action": {
                "type": "postback",
                "label": label,
                "data": f"DATE|{d}"  # 後端仍使用 YYYY-MM-DD
            }
        })

    return {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
                {
                    "type": "text",
                    "text": "📅 選擇預約日期（1 / 3）",
                    "weight": "bold",
                    "size": "lg"
                },
                {
                    "type": "text",
                    "text": "只顯示還有空的日期",
                    "size": "sm",
                    "color": "#666666"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": buttons
                }
            ]
        }
    }
