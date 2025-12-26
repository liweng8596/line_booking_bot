from datetime import datetime


def build_day_slots(date, slots):
    """
    slots: DB 回傳的任意 tuple
    我們只取 start / end（倒數兩個欄位）
    """
    buttons = []

    for row in slots:
        # ✅ 保證不管 DB 回傳幾個欄位都安全
        start = row[-2]
        end = row[-1]

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
