def build_confirm_flex(slot_id: str, date: str, start: str, end: str):
    return {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "確認預約",
                    "weight": "bold",
                    "size": "lg"
                },
                {
                    "type": "text",
                    "text": f"{date} {start}–{end}",
                    "margin": "md"
                }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "action": {
                        "type": "postback",              # ✅ 改這裡
                        "label": "確認預約",
                        "data": f"CONFIRM|{slot_id}"    # ✅ text → data
                    }
                },
                {
                    "type": "button",
                    "style": "secondary",
                    "action": {
                        "type": "message",              # ⭕ 保留 message
                        "label": "取消",
                        "text": "取消"
                    }
                }
            ]
        }
    }
