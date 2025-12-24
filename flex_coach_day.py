def build_coach_day_flex(date, slots):
    contents = []

    for _, _, start, end, status, student in slots:
        if status == "booked":
            label = f"{start}-{end} 已預約"
            color = "#E53935"
        elif status == "blocked":
            label = f"{start}-{end} 固定課"
            color = "#FB8C00"
        else:
            label = f"{start}-{end} 空堂"
            color = "#43A047"

        contents.append({
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {"type": "text", "text": label, "color": color}
            ]
        })

    return {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": f"📅 {date} 課表", "weight": "bold"}
            ] + contents
        }
    }
