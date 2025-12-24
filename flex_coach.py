# flex_coach.py

def build_coach_day_slots(date, slots):
    rows = []

    for slot_id, start, end, status, student in slots:
        if status == "blocked":
            action_label = "🔓 解鎖"
            action_text = f"UNLOCK|{slot_id}"
            status_text = "已鎖"
        elif status == "booked":
            action_label = "🔓 解鎖"
            action_text = f"UNLOCK|{slot_id}"
            status_text = student
        else:
            action_label = "🔒 鎖"
            action_text = f"LOCK|{slot_id}"
            status_text = "空堂"

        rows.append({
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {"type": "text", "text": f"{start}–{end}", "flex": 3},
                {"type": "text", "text": status_text, "flex": 3},
                {
                    "type": "button",
                    "action": {
                        "type": "message",
                        "label": action_label,
                        "text": action_text
                    }
                }
            ]
        })

    return {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": f"📅 {date} 課表", "weight": "bold"},
                *rows
            ]
        }
    }
