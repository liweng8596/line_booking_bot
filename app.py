from datetime import datetime
from db import get_open_status_for_range
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent,
    TextMessage,
    TextSendMessage,
    FlexSendMessage,
    PostbackEvent,
    QuickReply,
    QuickReplyButton,
    MessageAction,
)

from db import (
    get_available_dates,
    get_available_slots_by_date,
    get_all_slots_by_date,
    book_slot,
    get_user_booked_slots,
    # cancel_slot,
)

from flex_day_slots import build_day_slots
from flex_coach_day import build_coach_day_flex
from flex_cancel_confirm import build_cancel_confirm_flex
from flex_confirm import build_confirm_flex
from flex_date_picker import build_date_picker

# ================= 初始化 =================
load_dotenv()
app = FastAPI()

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
parser = WebhookParser(os.getenv("LINE_CHANNEL_SECRET"))

# ================= 狀態快取 =================
USER_SLOT_CACHE = {}

# ================= 教練 ID =================
COACH_IDS = {
    "U17fdee62c51888ebea77d8b696eb38e4",
}

# ================= Quick Reply =================


def main_quick_reply():
    return QuickReply(items=[
        QuickReplyButton(action=MessageAction(label="📅 預約", text="預約")),
        QuickReplyButton(action=MessageAction(label="❌ 取消", text="取消")),
    ])


@app.api_route("/", methods=["GET", "HEAD"])
@app.api_route("/health", methods=["GET", "HEAD"])
async def health():
    return PlainTextResponse("ok")


# ================= Webhook =================
@app.post("/webhook")
async def webhook(request: Request):
    signature = request.headers.get("x-line-signature")
    if not signature:
        raise HTTPException(status_code=400, detail="Missing signature")

    body = (await request.body()).decode("utf-8")

    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    for event in events:
        user_id = event.source.user_id

        if isinstance(event, PostbackEvent):
            handle_postback(event, user_id)
            continue

        if isinstance(event, MessageEvent) and isinstance(event.message, TextMessage):
            handle_message(event, user_id)
            continue

    return "OK"


def handle_message(event: MessageEvent, user_id: str):
    text = event.message.text.strip()

    # ================= 教練：查未來課表 =================
    if user_id in COACH_IDS and text.startswith("課表"):
        parts = text.split()
        days = 14

        if len(parts) == 2:
            try:
                days = int(parts[1])
            except ValueError:
                reply_text(event, "用法：課表 或 課表 14")
                return

        rows = get_open_status_for_range(days)

        lines = ["📅 未來 {} 天課表狀態\n".format(days)]
        for date_str, status, source in rows:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            weekday = "一二三四五六日"[dt.weekday()]

            if status == "open" and source == "override":
                icon = "🔓"
            elif status == "open":
                icon = "✅"
            else:
                icon = "❌"

            lines.append(f"{dt.month:02}/{dt.day:02}（{weekday}） {icon}")

        reply_text(event, "\n".join(lines))
        return

    # ===== 下面接原本邏輯 =====


# ================= Postback Handler =================
def handle_postback(event: PostbackEvent, user_id: str):
    data = event.postback.data

    # 📅 選日期
    if data.startswith("DATE|"):
        date = data.split("|", 1)[1]
        slots = get_available_slots_by_date(date)

        if not slots:
            reply_text(event, f"{date} 沒有可預約的時段")
            return

        flex = FlexSendMessage(
            alt_text=f"{date} 可預約時段",
            contents=build_day_slots(date, slots)
        )
        line_bot_api.reply_message(event.reply_token, flex)
        return

    # ⏰ 選時段
    if data.startswith("SLOT|"):
        slot_id = data.split("|", 1)[1]

        try:
            date, time_range = slot_id.split("T", 1)
            start, end = time_range.split("-", 1)
        except ValueError:
            reply_text(event, "❌ 時段資料錯誤")
            return

        USER_SLOT_CACHE[user_id] = slot_id

        flex = FlexSendMessage(
            alt_text="確認預約",
            contents=build_confirm_flex(slot_id, date, start, end)
        )
        line_bot_api.reply_message(event.reply_token, flex)
        return

    # ✅ 確認預約
    if data.startswith("CONFIRM|"):
        slot_id = data.split("|", 1)[1]

        if USER_SLOT_CACHE.get(user_id) != slot_id:
            reply_text(event, "⚠️ 此預約已過期，請重新選擇")
            return

        success = book_slot(slot_id, user_id)
        USER_SLOT_CACHE.pop(user_id, None)

        reply = (
            f"✅ 預約成功！\n{slot_id.replace('T', ' ')}"
            if success else
            "❌ 此時段已被其他人預約"
        )
        reply_text(event, reply)
        return

    # ❌ 確認取消
    if data.startswith("CANCEL_CONFIRM|"):
        slot_id = data.split("|", 1)[1]
        success = cancel_slot(slot_id, user_id)
        reply_text(event, "❌ 已成功取消預約" if success else "取消失敗")
        return

    # 🔙 回選日期
    if data == "BACK|DATE":
        dates = get_available_dates()
        flex = FlexSendMessage(
            alt_text="請選擇日期",
            contents=build_date_picker(dates)
        )
        line_bot_api.reply_message(event.reply_token, flex)
        return


# ================= Message Handler =================
def handle_message(event: MessageEvent, user_id: str):
    text = event.message.text.strip()

    # 👨‍🏫 教練查課
    if user_id in COACH_IDS and text.startswith("查課"):
        parts = text.split()
        if len(parts) != 2:
            reply_text(event, "用法：查課 YYYY-MM-DD")
            return

        date = parts[1]
        slots = get_all_slots_by_date(date)

        if not slots:
            reply_text(event, f"{date} 沒有任何課程")
            return

        flex = FlexSendMessage(
            alt_text=f"{date} 課表",
            contents=build_coach_day_flex(date, slots)
        )
        line_bot_api.reply_message(event.reply_token, flex)
        return

    # 📅 預約
    if text == "預約":
        dates = get_available_dates()
        if not dates:
            reply_text(event, "目前沒有可預約的日期 😢")
            return

        flex = FlexSendMessage(
            alt_text="請選擇日期",
            contents=build_date_picker(dates)
        )
        line_bot_api.reply_message(event.reply_token, flex)
        return

    # ❌ 取消
    # if text == "取消":
    #     slots = get_user_booked_slots(user_id)
    #     if not slots:
    #         reply_text(event, "你目前沒有已預約的課程")
    #         return

    #     flex = FlexSendMessage(
    #         alt_text="取消預約",
    #         contents=build_cancel_confirm_flex(slots)
    #     )
    #     line_bot_api.reply_message(event.reply_token, flex)
    #     return

    # fallback
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(
            text="請選擇功能 👇",
            quick_reply=main_quick_reply()
        )
    )


# ================= Utils =================
def reply_text(event, text: str):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=text)
    )
