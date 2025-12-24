from collections import defaultdict

def build_schedule_carousel(slots):
    """
    slots: [(id, date, start_time, end_time), ...]
    """
    grouped = defaultdict(list)

    for slot_id, date, start, end in slots:
        grouped[date].append((slot_id, start, end))

    bubbles = []

    for date, day_slots in grouped.items():
        contents = [
            {
                "type": "text",
                "text": f"日期 {date}",
                "weight": "bold",
                "size": "lg"
            }
        ]

        for slot_id, start, end in day_slots[:5]:
            contents.append({
                "type": "button",
                "style": "secondary",
                "action": {
                    "type": "pos
