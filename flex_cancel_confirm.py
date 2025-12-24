def build_cancel_confirm_flex(slot_id, date, start, end):
    return {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "確認取消預約",
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
                        "type": "message",
                        "label": "確認取消",
                        "text": f"CANCEL_CONFIRM|{slot_id}"
                    }
                },
                {
                    "type": "button",
                    "style": "secondary",
                    "action": {
                        "type": "message",
                        "label": "不取消",
                        "text": "不取消"
                    }
                }
            ]
        }
    }
