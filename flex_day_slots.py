def build_day_slots(date, slots):
    buttons = []

    for start, end in slots:
        buttons.append({
            "type": "button",
            "style": "secondary",
            "action": {
                "type": "postback",
                "label": f"{start}–{end}",
                "data": f"SLOT|{date}T{start}-{end}"
            }
        })

    if not buttons:
        buttons.append({
            "type": "text",
            "text": "當天已滿 😢",
            "size": "sm",
            "color": "#999999"
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
                    "text": "⏰ 選擇時段（2 / 3）",
                    "weight": "bold",
                    "size": "lg"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": buttons
                },
                {
                    "type": "button",
                    "style": "secondary",
                    "action": {
                        "type": "postback",
                        "label": "⬅ 回選日期",
                        "data": "BACK|DATE"
                    }
                }
            ]
        }
    }
