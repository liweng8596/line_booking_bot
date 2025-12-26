from datetime import datetime


def build_confirm_flex(slot_id, date, start, end):
    dt = datetime.strptime(date, "%Y-%m-%d")
    weekday = ["一", "二", "三", "四", "五", "六", "日"][dt.weekday()]
    display_date = f"{dt.month}/{dt.day}（週{weekday}）"

    return {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
                {
                    "type": "text",
                    "text": "✅ 確認你的預約（3 / 3）",
                    "weight": "bold",
                    "size": "lg"
                },
                {
                    "type": "text",
                    "text": "我會幫你保留以下時段 👇",
                    "size": "sm",
                    "color": "#555555"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "text",
                            "text": f"📅 日期：{display_date}"
                        },
                        {
                            "type": "text",
                            "text": f"⏰ 時間：{start}–{end}"
                        }
                    ]
                },
                {
                    "type": "button",
                    "style": "primary",
                    "action": {
                        "type": "postback",
                        "label": "✅ 確認預約",
                        "data": f"CONFIRM|{slot_id}"
                    }
                },
                {
                    "type": "button",
                    "style": "secondary",
                    "action": {
                        "type": "postback",
                        "label": "⬅ 修改時間",
                        "data": "BACK|DATE"
                    }
                }
            ]
        }
    }
