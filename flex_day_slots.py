from datetime import datetime


def build_day_slots(date, slots):
    """
    slots: [(slot_id, start, end), ...]
    """
    # 顯示用日期（人類友善）
    dt = datetime.strptime(date, "%Y-%m-%d")
    weekday = ["一", "二", "三", "四", "五", "六", "日"][dt.weekday()]
    display_date = f"{dt.month}/{dt.day}（週{weekday}）"

    buttons = []

    for slot_id, start, end in slots:
        buttons.append({
            "type": "button",
            "style": "secondary",
            "action": {
                "type": "postback",
                "label": f"{start}–{end}",
                "data": f"SLOT|{date}T{start}-{end}"
            }
        })

    # 沒有時段的保護（UX）
    if not buttons:
        buttons.append({
            "type": "text",
            "text": "當天已滿 😢",
            "color": "#999999",
            "size": "sm"
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
                    "type": "text",
                    "text": f"📅 {display_date}",
                    "size": "sm",
                    "color": "#666666"
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
