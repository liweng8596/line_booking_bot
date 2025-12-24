import os
from fastapi import FastAPI, Request, HTTPException
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent,
    TextMessage,
    TextSendMessage,
    FlexSendMessage,
)
from dotenv import load_dotenv
from flex_coach import build_coach_day_slots

from flex import build_schedule_carousel
from db import (
    get_available_dates,
    get_available_slots_by_date,
    get_all_slots_by_date,
    book_slot,
    get_user_booked_slots,
    cancel_slot,
)

def get_display_name(user_id: str) -> str:
    try:
        profile = line_bot_api.get_profile(user_id)
        return profile.display_name
    except Exception as e:
        print("取得顯示名稱失敗:", e)
        return "已預約"
        
# ===== 使用者暫存 =====
USER_SELECTED_DATE = {}
USER_SLOT_CACHE = {}
USER_CANCEL_CACHE = {}

# ===== 教練 LINE user_id =====
COACH_IDS = {
    "U17fdee62c51888ebea77d8b696eb38e4",
}

# ===== 初始化 =====
load_dotenv()
app = FastAPI()

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
parser = WebhookParser(os.getenv("LINE_CHANNEL_SECRET"))


@app.post("/webhook")
async def webhook(request: Request):
    try:
        signature = request.headers["x-line-signature"]
    except KeyError:
        raise HTTPException(status_code=400, detail="Missing signature")

    body = (await request.body()).decode("utf-8")

    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    for event in events:
        if not (
            isinstance(event, MessageEvent)
            and isinstance(event.message, TextMessage)
        ):
            continue

        user_text = event.message.text.strip()
        user_id = event.source.user_id


        # ===== 教練查課 =====
        if user_id in COACH_IDS and user_text.startswith("查課"):
            parts = user_text.split()

            if len(parts) != 2:
                reply_text = "用法：查課 YYYY-MM-DD"
            else:
                date = parts[1]
                slots = get_all_slots_by_date(date)

                if not slots:
                    reply_text = f"{date} 沒有任何課程"
                else:
                    lines = [f"📅 {date} 課表"]
                    for _, _, start, end, status, student in slots:
                        if status == "booked":
                            name = get_display_name(student)
                            lines.append(f"{start}–{end}｜{name}")
                        elif status == "blocked":
                            lines.append(f"{start}–{end}｜（固定課）")
                        else:
                            lines.append(f"{start}–{end}｜（空堂）")

                    reply_text = "\n".join(lines)

            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply_text)
            )
            continue

        # ===== 預約（Flex）=====
        if user_text == "預約":
            slots = []

            dates = get_available_dates()
            for d in dates:
                day_slots = get_available_slots_by_date(d)
                slots.extend(day_slots)

            if not slots:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="目前沒有可預約的時段 😢")
                )
                continue

            flex_message = FlexSendMessage(
                alt_text="下週課表",
                contents=build_schedule_carousel(slots)
            )

            line_bot_api.reply_message(event.reply_token, flex_message)
            continue

        # ===== 取消 =====
        elif user_text == "取消":
            slots = get_user_booked_slots(user_id)
            USER_CANCEL_CACHE[user_id] = slots
            USER_SLOT_CACHE.pop(user_id, None)

            if not slots:
                reply_text = "你目前沒有已預約的課程"
            else:
                lines = ["❌ 你的預約課程（輸入數字取消）："]
                for idx, (_, date, start, end) in enumerate(slots, start=1):
                    lines.append(f"{idx}. {date} {start}-{end}")
                reply_text = "\n".join(lines)

        # ===== 點 Flex 按鈕 =====
        elif user_text.startswith("SLOT|"):
            slot_id = user_text.split("|", 1)[1].strip()
            success = book_slot(slot_id, user_id)

            if success:
                reply_text = f"✅ 預約成功！\n{slot_id.replace('T', ' ')}"
            else:
                reply_text = "❌ 此時段已被預約"

        # ===== 輸入數字 =====
        elif user_text.isdigit():
            idx = int(user_text) - 1

            if user_id in USER_CANCEL_CACHE:
                slots = USER_CANCEL_CACHE[user_id]

                if idx < 0 or idx >= len(slots):
                    reply_text = "請輸入正確的數字"
                else:
                    slot_id, date, start, end = slots[idx]
                    success = cancel_slot(slot_id, user_id)
                    reply_text = (
                        f"❌ 已取消：\n{date} {start}-{end}"
                        if success else "取消失敗，請稍後再試"
                    )

                USER_CANCEL_CACHE.pop(user_id, None)

            elif user_id in USER_SLOT_CACHE:
                slots = USER_SLOT_CACHE[user_id]

                if idx < 0 or idx >= len(slots):
                    reply_text = "請輸入正確的數字"
                else:
                    slot_id, date, start, end = slots[idx]
                    success = book_slot(slot_id, user_id)
                    reply_text = (
                        f"✅ 預約成功！\n{date} {start}-{end}"
                        if success else "❌ 此時段已被預約"
                    )

                USER_SLOT_CACHE.pop(user_id, None)

            else:
                reply_text = "請先輸入「預約」或「取消」"

        # ===== 其他 =====
        else:
            reply_text = "請輸入「預約」或「取消」"

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )

    return "OK"
