def build_date_picker(dates: list[str]):
    bubbles = []

    for d in dates:
        bubbles.append({
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": f"日期 {d}",
                        "weight": "bold",
                        "size": "lg",
                        "align": "center"
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
                            "label": "選擇這天",
                            "text": f"DATE|{d}"
                        }
                    }
                ]
            }
        })

    return {
        "type": "carousel",
        "contents": bubbles
    }
