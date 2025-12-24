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

from flex import build_schedule_carousel
from flex_coach import build_coach_day_slots
from db import (
    get_available_dates,
    get_available_slots_by_date,
    get_all_slots_by_date,
    book_slot,
    get_user_booked_slots,
    cancel_slot,
)
from flex_coach_day import build_coach_day_flex

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


def get_display_name(user_id: str) -> str:
    try:
        profile = line_bot_api.get_profile(user_id)
        return profile.display_name
    except Exception:
        return "已預約"


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
        if not isinstance(event, MessageEvent) or not isinstance(event.message, TextMessage):
            continue

        user_text = event.message.text.strip()
        user_id = event.source.user_id

        # ================= 教練查課 =================
        flex_message = FlexSendMessage(
               alt_text=f"{date} 課表",
               contents=build_coach_day_flex(date, slots)
        )
           
        line_bot_api.reply_message(event.reply_token, flex_message)

        # ================= 預約：Step 1 選日期 =================
        if user_text == "預約":
            dates = get_available_dates()

            if not dates:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="目前沒有可預約的日期 😢")
                )
                continue

            from flex_date_picker import build_date_picker

            flex_message = FlexSendMessage(
                alt_text="請選擇日期",
                contents=build_date_picker(dates)
            )

            line_bot_api.reply_message(event.reply_token, flex_message)
            continue

        # ================= 預約：Step 2 點日期 =================
        elif user_text.startswith("DATE|"):
            date = user_text.split("|", 1)[1]
            USER_SELECTED_DATE[user_id] = date

            slots = get_available_slots_by_date(date)

            if not slots:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=f"{date} 沒有可預約的時段 😢")
                )
                continue

            flex_message = FlexSendMessage(
                alt_text=f"{date} 可預約時段",
                contents=build_schedule_carousel(slots)
            )

            line_bot_api.reply_message(event.reply_token, flex_message)
            continue

        # ================= 點時段（立即預約） =================
        elif user_text.startswith("SLOT|"):
            slot_id = user_text.split("|", 1)[1]
            
            date, time_range = slot_id.split("T")
            start, end = time_range.split("-")
            
            USER_SLOT_CACHE[user_id] = slot_id
            
            from flex_confirm import build_confirm_flex
            
            flex_message = FlexSendMessage(
                alt_text="確認預約",
                contents=build_confirm_flex(slot_id, date, start, end)
            )
            
            line_bot_api.reply_message(event.reply_token, flex_message)
            continue


            if success:
                reply_text = f"✅ 預約成功！\n{slot_id.replace('T', ' ')}"
            else:
                reply_text = "❌ 此時段已被預約"

            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply_text)
            )
            continue
        #=============== comfirm處理
        elif user_text.startswith("CONFIRM|"):
            slot_id = user_text.split("|", 1)[1]
            
            success = book_slot(slot_id, user_id)
            
            if success:
                reply_text = f"✅ 預約成功！\n{slot_id.replace('T', ' ')}"
            else:
                reply_text = "❌ 此時段已被其他人預約 😢"
            
            USER_SLOT_CACHE.pop(user_id, None)
            
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply_text)
            )
            continue
        # ================= 取消 =================
        elif user_text == "取消":
            slots = get_user_booked_slots(user_id)
            USER_CANCEL_CACHE[user_id] = slots

            if not slots:
                reply_text = "你目前沒有已預約的課程"
            else:
                lines = ["❌ 你的預約課程（輸入數字取消）："]
                for idx, (_, date, start, end) in enumerate(slots, start=1):
                    lines.append(f"{idx}. {date} {start}-{end}")
                reply_text = "\n".join(lines)

            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply_text)
            )
            continue

        # ================= 輸入數字取消 =================
        elif user_text.isdigit() and user_id in USER_CANCEL_CACHE:
            idx = int(user_text) - 1
            slots = USER_CANCEL_CACHE[user_id]
        
            if idx < 0 or idx >= len(slots):
                reply_text = "請輸入正確的數字"
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=reply_text)
                )
                continue
        
            slot_id, date, start, end = slots[idx]
        
            from flex_cancel_confirm import build_cancel_confirm_flex
        
            USER_SLOT_CACHE[user_id] = slot_id  # 暫存要取消的
        
            flex_message = FlexSendMessage(
                alt_text="確認取消預約",
                contents=build_cancel_confirm_flex(slot_id, date, start, end)
            )
        
            line_bot_api.reply_message(event.reply_token, flex_message)
            continue
        #===================確認取消=================
        elif user_text.startswith("CANCEL_CONFIRM|"):
            slot_id = user_text.split("|", 1)[1]
           
            success = cancel_slot(slot_id, user_id)
           
            if success:
                reply_text = "❌ 已成功取消預約"
            else:
                reply_text = "取消失敗，請稍後再試"
           
            USER_CANCEL_CACHE.pop(user_id, None)
            USER_SLOT_CACHE.pop(user_id, None)
           
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply_text)
            )
            continue
        # ================= 其他 =================
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="請輸入「預約」或「取消」")
            )

    return "OK"
