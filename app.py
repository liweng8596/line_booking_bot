import os
from fastapi import FastAPI, Request, HTTPException
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent,
    TextMessage,
    TextSendMessage,
    FlexSendMessage,
    PostbackEvent,
)
from dotenv import load_dotenv

from flex import build_schedule_carousel
from flex_coach_day import build_coach_day_flex
from db import (
    get_available_dates,
    get_available_slots_by_date,
    get_all_slots_by_date,
    book_slot,
    get_user_booked_slots,
    cancel_slot,
)

# ================= 使用者狀態暫存 =================
USER_SELECTED_DATE = {}
USER_SLOT_CACHE = {}

# ================= 教練 ID =================
COACH_IDS = {
    "U17fdee62c51888ebea77d8b696eb38e4",
}

# ================= 初始化 =================
load_dotenv()
app = FastAPI()

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
parser = WebhookParser(os.getenv("LINE_CHANNEL_SECRET"))


@app.post("/webhook")
async def webhook(request: Request):
    # ===== 驗證簽章 =====
    try:
        signature = request.headers["x-line-signature"]
    except KeyError:
        raise HTTPException(status_code=400, detail="Missing signature")

    body = (await request.body()).decode("utf-8")

    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # ===== 處理事件 =====
    for event in events:
        user_id = event.source.user_id

        # =====================================================
        # 🟦 Postback（所有按鈕）
        # =====================================================
        if isinstance(event, PostbackEvent):
            data = event.postback.data

            # ---------- 📅 選擇日期 ----------
            if data.startswith("DATE|"):
                date = data.split("|", 1)[1]
                USER_SELECTED_DATE[user_id] = date

                slots = get_available_slots_by_date(date)
                if not slots:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=f"{date} 沒有可預約的時段 😢")
                    )
                    continue

                flex = FlexSendMessage(
                    alt_text=f"{date} 可預約時段",
                    contents=build_schedule_carousel(slots)
                )

                line_bot_api.reply_message(
                    event.reply_token,
                    [
                        TextSendMessage(text=f"📅 已選擇日期：{date}"),
                        flex
                    ]
                )
                continue

            # ---------- ⏰ 選擇時段 ----------
            if data.startswith("SLOT|"):
                slot_id = data.split("|", 1)[1]

                # 防呆（不再炸）
                if "T" not in slot_id or "-" not in slot_id:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="❌ 時段資料錯誤")
                    )
                    continue

                date, time_range = slot_id.split("T", 1)
                start, end = time_range.split("-", 1)

                USER_SLOT_CACHE[user_id] = slot_id

                from flex_confirm import build_confirm_flex

                flex = FlexSendMessage(
                    alt_text="確認預約",
                    contents=build_confirm_flex(slot_id, date, start, end)
                )

                line_bot_api.reply_message(
                    event.reply_token,
                    [
                        TextSendMessage(text=f"⏰ 已選擇時段：{start}-{end}"),
                        flex
                    ]
                )
                continue

            # ---------- ✅ 確認預約 ----------
            if data.startswith("CONFIRM|"):
                slot_id = data.split("|", 1)[1]
                success = book_slot(slot_id, user_id)

                reply = (
                    f"✅ 預約成功！\n{slot_id.replace('T', ' ')}"
                    if success else
                    "❌ 此時段已被其他人預約 😢"
                )

                USER_SLOT_CACHE.pop(user_id, None)
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=reply)
                )
                continue

            # ---------- ❌ 確認取消 ----------
            if data.startswith("CANCEL_CONFIRM|"):
                slot_id = data.split("|", 1)[1]
                success = cancel_slot(slot_id, user_id)

                reply = "❌ 已成功取消預約" if success else "取消失敗，請稍後再試"

                USER_SLOT_CACHE.pop(user_id, None)
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=reply)
                )
                continue

        # =====================================================
        # 👨‍🏫 教練查課（Flex）
        # =====================================================
            if user_id in COACH_IDS and user_text.startswith("查課"):
                parts = user_text.split()
                if len(parts) != 2:
                    reply = "用法：查課 YYYY-MM-DD"
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
                    continue
            
                date = parts[1]
                slots = get_all_slots_by_date(date)
            
                if not slots:
                    reply = f"{date} 沒有任何課程"
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
                    continue
            
                flex = FlexSendMessage(
                    alt_text=f"{date} 課表",
                    contents=build_coach_day_flex(date, slots)
                )
                line_bot_api.reply_message(event.reply_token, flex)
                continue
                # ---------- 📅 預約 ----------
                if user_text == "預約":
                    from flex_date_picker import build_date_picker
            
                    dates = get_available_dates()
                    if not dates:
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text="目前沒有可預約的日期 😢")
                        )
                        continue
            
                    flex = FlexSendMessage(
                        alt_text="請選擇日期",
                        contents=build_date_picker(dates)
                    )
                    line_bot_api.reply_message(event.reply_token, flex)
                    continue

            # ---------- ❌ 取消 ----------
            if user_text == "取消":
                slots = get_user_booked_slots(user_id)
                if not slots:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="你目前沒有已預約的課程")
                    )
                    continue

                from flex_cancel_list import build_cancel_list_flex

                flex = FlexSendMessage(
                    alt_text="取消預約",
                    contents=build_cancel_list_flex(slots)
                )
                line_bot_api.reply_message(event.reply_token, flex)
                continue

            # ---------- 其他 ----------
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="請輸入「預約」或「取消」")
            )

    return "OK"
