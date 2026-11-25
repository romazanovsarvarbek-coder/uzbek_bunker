"""Inline tugmalar (klaviaturalar) moduli."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.config import BOT_USERNAME
from bot.state import GameState


def lobby_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Qo'shilish ➕", callback_data="lobby:join"),
        InlineKeyboardButton(text="Chiqish ➖", callback_data="lobby:leave"),
    )
    builder.row(
        InlineKeyboardButton(text="O'yinni boshlash 🚀", callback_data="lobby:start"),
    )
    builder.row(
        InlineKeyboardButton(text="Lobini yopish ❌", callback_data="lobby:cancel"),
    )
    return builder.as_markup()


def voting_keyboard(game: GameState) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for player in game.alive_players:
        vote_count = sum(1 for target_id in game.votes.values() if target_id == player.user_id)
        badge = f" ({vote_count})" if vote_count > 0 else ""
        builder.button(
            text=f"🎯 {player.short_name}{badge}",
            callback_data=f"vote:{player.user_id}",
        )
    builder.adjust(2)
    builder.row(
        InlineKeyboardButton(
            text="Ovoz berishni yakunlash ⏹",
            callback_data="vote:finish",
        )
    )
    return builder.as_markup()


def bot_pm_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="Botga start bosish 🤖",
            url=f"https://t.me/{BOT_USERNAME}?start=bunker",
        )
    )
    return builder.as_markup()

