"""Vercel Serverless Webhook entrypoint (FastAPI + aiogram 3.x)."""

from __future__ import annotations

import logging
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Update
from fastapi import FastAPI, Header, HTTPException, Request

# Loyiha ildiz katalogini sys.path ga qo'shish (Vercel muhitida xavfsiz import uchun)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from bot.config import BOT_TOKEN, BOT_USERNAME, WEBHOOK_SECRET  # noqa: E402
from bot.handlers import router  # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher()
dp.include_router(router)

app = FastAPI(title="Uzbek Bunker Telegram Bot")


@app.get("/api/webhook")
async def webhook_health(request: Request, setup: str | None = None) -> dict:
    """Healthcheck va ixtiyoriy bir bosqichli webhook sozlash."""
    if setup == "1":
        host = request.headers.get("host")
        if not host:
            raise HTTPException(status_code=400, detail="Host header topilmadi")
        webhook_url = f"https://{host}/api/webhook"
        kwargs: dict = {"url": webhook_url, "drop_pending_updates": True}
        if WEBHOOK_SECRET:
            kwargs["secret_token"] = WEBHOOK_SECRET
        await bot.set_webhook(**kwargs)
        return {
            "status": "webhook_set",
            "webhook_url": webhook_url,
            "bot": f"@{BOT_USERNAME}",
        }

    return {"status": "ok", "bot": f"@{BOT_USERNAME}"}


@app.post("/api/webhook")
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
) -> dict:
    """Telegramdan kelgan webhook yangilanishlarini qabul qiladi."""
    if WEBHOOK_SECRET and x_telegram_bot_api_secret_token != WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Noto'g'ri secret token")

    data = await request.json()
    update = Update.model_validate(data, context={"bot": bot})
    await dp.feed_update(bot=bot, update=update)
    return {"ok": True}

