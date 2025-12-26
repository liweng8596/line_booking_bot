import os
from dotenv import load_dotenv
from linebot import LineBotApi

from db import get_tomorrow_bookings
from reminder import send_reminder

load_dotenv()

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))


def main():
    bookings = get_tomorrow_bookings()
    if not bookings:
        return

    send_reminder(line_bot_api, bookings)


if __name__ == "__main__":
    main()
