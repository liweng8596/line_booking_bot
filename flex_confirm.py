def build_confirm_flex(slot_id, date, start, end):
    return {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
                {
                    "type": "text",
                    "text": "請確認你的預約",
                    "weight": "bold",
                    "size": "lg"
                },
                {
                    "type": "text",
                    "text": f"{date} {start}–{end}",
                    "margin": "md"
                },
                {
                    "type": "button",
                    "style": "primary",
                    "action": {
                        "type": "postback",
                        "label": "✅ 確認預約",
                        "data": f"CONFIRM|{slot_id}"
                    }
                }
            ]
        }
    }
