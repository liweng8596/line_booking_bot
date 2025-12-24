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
                            "type": "postback",   # ✅ 改這裡
                            "label": "選擇這天",
                            "data": f"DATE|{d}"  # ✅ text → data
                        }
                    }
                ]
            }
        })

    return {
        "type": "carousel",
        "contents": bubbles
    }
