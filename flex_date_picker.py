def build_date_picker(dates):
    buttons = []

    for d in dates:
        buttons.append({
            "type": "button",
            "style": "secondary",
            "action": {
                "type": "postback",   # ✅ 一定要是 postback
                "label": d,
                "data": f"DATE|{d}"   # ✅ 不是 text
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
