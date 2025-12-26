import os
from datetime import datetime
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

# ===== DB =====
from db import (
    init_db,
    get_available_dates,
    get_available_slots_by_date,
    get_all_slots_by_date,
    get_user_booked_slots,
    book_slot,
    cancel_slot_by_time,
    get_open_status_for_range,
)

# ===== Flex =====
from flex_day_slots import build_day_slots
from flex_confirm import build_confirm_flex
from flex_date_picker import build_date_picker
from flex_coach_day import build_coach_day_flex
from flex_cancel_confirm import build_cancel_confirm_flex
from flex_cancel_list import build_cancel_list_flex

# ================= 初始化 =================
load_dotenv()
print("🚀 calling init_db")
init_db()

app = FastAPI()
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
parser = WebhookParser(os.getenv("LINE_CHANNEL_SECRET"))

# ================= 狀態 =================
USER_SLOT_CACHE = {}

COACH_IDS = {
    "U17fdee62c51888ebea77d8b696eb38e4",
}

# ================= Quick Reply =================


def main_quick_reply():
    return QuickReply(items=[
        QuickReplyButton(action=MessageAction(label="📅 預約", text="預約")),
        QuickReplyButton(action=MessageAction(label="❌ 取消", text="取消")),
    ])

# ================= Health =================


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

# ================= Message Handler =================


def handle_message(event: MessageEvent, user_id: str):
    text = event.message.text.strip()

    # ===== 教練：未來課表 =====
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
        lines = [f"📅 未來 {days} 天課表狀態\n"]

        for date_str, status, source in rows:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            weekday = "一二三四五六日"[dt.weekday()]
            icon = "🔓" if status == "open" and source == "override" else "✅" if status == "open" else "❌"
            lines.append(f"{dt.month:02}/{dt.day:02}（{weekday}） {icon}")

        reply_text(event, "\n".join(lines))
        return

    # ===== 教練：查課 =====
    if user_id in COACH_IDS and text.startswith("查課"):
        parts = text.split()
        if len(parts) != 2:
            reply_text(event, "用法：查課 YYYY-MM-DD")
            return

        slots = get_all_slots_by_date(parts[1])
        if not slots:
            reply_text(event, f"{parts[1]} 沒有任何課程")
            return

        flex = FlexSendMessage(
            alt_text="課表",
            contents=build_coach_day_flex(parts[1], slots)
        )
        line_bot_api.reply_message(event.reply_token, flex)
        return

    # ===== 預約 =====
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

    # ===== 取消 =====
    if text == "取消":
        slots = get_user_booked_slots(user_id)
        if not slots:
            reply_text(event, "你目前沒有已預約的課程")
            return

        flex = FlexSendMessage(
            alt_text="取消預約",
            contents=build_cancel_list_flex(slots)
        )
        line_bot_api.reply_message(event.reply_token, flex)
        return

    # fallback
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="請選擇功能 👇", quick_reply=main_quick_reply())
    )

# ================= Postback Handler =================


def handle_postback(event: PostbackEvent, user_id: str):
    data = event.postback.data

    # 選日期
    if data.startswith("DATE|"):
        date = data.split("|", 1)[1]
        slots = get_available_slots_by_date(date)

        if not slots:
            reply_text(event, f"{date} 沒有可預約的時段")
            return

        flex = FlexSendMessage(
            alt_text="可預約時段",
            contents=build_day_slots(date, slots)
        )
        line_bot_api.reply_message(event.reply_token, flex)
        return

    # 選時段
    if data.startswith("SLOT|"):
        slot_id = data.split("|", 1)[1]
        date, time_range = slot_id.split("T", 1)
        start, end = time_range.split("-", 1)

        USER_SLOT_CACHE[user_id] = slot_id

        flex = FlexSendMessage(
            alt_text="確認預約",
            contents=build_confirm_flex(slot_id, date, start, end)
        )
        line_bot_api.reply_message(event.reply_token, flex)
        return

    # 確認預約
    if data.startswith("CONFIRM|"):
        slot_id = data.split("|", 1)[1]
        success = book_slot(slot_id, user_id)
        USER_SLOT_CACHE.pop(user_id, None)

        reply_text(
            event,
            f"✅ 預約成功！\n{slot_id.replace('T', ' ')}" if success else "❌ 此時段已被其他人預約"
        )
        return

    # ===== 取消流程 =====

    # 預覽取消
    if data.startswith("CANCEL_PREVIEW|"):
        _, date, start, end = data.split("|", 3)

        flex = FlexSendMessage(
            alt_text="確認取消",
            contents=build_cancel_confirm_flex(date, start, end)
        )
        line_bot_api.reply_message(event.reply_token, flex)
        return

    # 確認取消
    if data.startswith("CANCEL_CONFIRM|"):
        _, date, start, end = data.split("|", 3)

        success = cancel_slot_by_time(date, start, end, user_id)
        reply_text(
            event,
            f"❌ 已取消 {date} {start}-{end}" if success else "⚠️ 取消失敗，可能已取消或非你的預約"
        )
        return

# ================= Utils =================


def reply_text(event, text: str):
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=text))
