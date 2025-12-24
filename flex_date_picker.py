from datetime import datetime

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

    for d in dates:
        # d 格式：YYYY-MM-DD
        dt = datetime.strptime(d, "%Y-%m-%d")
        weekday = WEEKDAY_MAP[dt.weekday()]

        label = f"{d}（週{weekday}）"

        buttons.append({
            "type": "button",
            "style": "secondary",
            "action": {
                "type": "postback",
                "label": label,      # 👈 顯示：日期 + 星期
                "data": f"DATE|{d}"  # 👈 後端還是只收日期
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
                    "text": "📅 請選擇日期",
                    "weight": "bold",
                    "size": "lg"
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
