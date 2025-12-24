def build_day_slots(date, slots):
    """
    slots: [(slot_id, date, start_time, end_time), ...]
    """
    contents = [
        {
            "type": "text",
            "text": f"📅 {date} 可預約時段",
            "weight": "bold",
            "size": "lg"
        }
    ]

    for slot_id, _, start, end in slots:
        contents.append({
            "type": "button",
            "style": "secondary",
            "action": {
                "type": "postback",
                "label": f"{start}–{end}",
                "data": f"SLOT|{date}T{start}-{end}"
            }
        })

    return {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": contents
        }
    }
