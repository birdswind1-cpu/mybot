import asyncio
import os

from dotenv import load_dotenv
from google import genai
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

# Load .env file
load_dotenv()

# Get API keys from .env
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "မင်္ဂလာပါ! မေးချင်တာများကို မေးနိုင်ပါပြီ။"
    )


def ask_gemini(user_message):
    return client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=user_message,
    )


async def ai_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )

    try:
        response = await asyncio.wait_for(
            asyncio.to_thread(ask_gemini, user_message),
            timeout=30
        )

        if response.text:
            await update.message.reply_text(response.text)
        else:
            await update.message.reply_text(
                "Gemini က အဖြေမပြန်နိုင်သေးပါဘူး။ ထပ်မေးကြည့်ပါ။"
            )

    except asyncio.TimeoutError:
        await update.message.reply_text(
            "Gemini response နောက်ကျနေပါတယ်။ ခဏနေပြီး ပြန်မေးပေးပါ။"
        )

    except Exception as e:
        error_msg = str(e)

        print("Gemini Error:", error_msg)

        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            await update.message.reply_text(
                "Request များနေပါတယ်။ ခဏစောင့်ပြီး ပြန်မေးပေးပါ။"
            )
        else:
            await update.message.reply_text(
                "Error ဖြစ်သွားပါတယ်။"
            )


if name == "main":
    app = (
        ApplicationBuilder()
        .token(TELEGRAM_TOKEN)
        .connect_timeout(30.0)
        .read_timeout(30.0)
        .write_timeout(30.0)
        .build()
    )

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            ai_reply
        )
    )

    print("AI Bot စတင် အလုပ်လုပ်နေပါပြီ...")

    app.run_polling()