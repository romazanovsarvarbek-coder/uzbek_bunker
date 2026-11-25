"""Bunker o'yini uchun barcha aiogram 3.x handlerlari."""

from __future__ import annotations

import random
from collections import Counter

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.config import MIN_PLAYERS
from bot.keyboards import bot_pm_keyboard, lobby_keyboard, voting_keyboard
from bot.state import GamePhase, GameState, Player, games

router = Router()


# ---------------------------------------------------------------------------
# Yordamchi funksiyalar
# ---------------------------------------------------------------------------


def _format_lobby_text(game: GameState) -> str:
    count = len(game.players)
    capacity_text = (
        f"🛡 Bunker sig'imi: <b>{max(1, round(count / 2))} kishi</b>"
        if count >= MIN_PLAYERS
        else f"⏳ Boshlash uchun kamida <b>{MIN_PLAYERS} kishi</b> kerak"
    )
    players_lines = (
        "\n".join(
            f"{idx}. {p.mention_html}"
            for idx, p in enumerate(game.players.values(), start=1)
        )
        if game.players
        else "<i>Hozircha hech kim qo'shilmagan.</i>"
    )
    return (
        "🏚 <b>BUNKER O'YINI — LOBI OCHILDI!</b>\n\n"
        "Falokat yaqinlashmoqda! Bunkerda joylar soni cheklangan. "
        "O'yinda qatnashish uchun quyidagi <b>«Qo'shilish ➕»</b> tugmasini bosing.\n\n"
        f"👥 <b>Ishtirokchilar ({count}):</b>\n"
        f"{players_lines}\n\n"
        f"{capacity_text}\n\n"
        "💡 <i>Eslatma: O'yin boshlanganda shaxsiy xususiyatlaringizni olish uchun "
        "botga shaxsiy xabarda /start bosgan bo'lishingiz shart!</i>"
    )


def _format_pm_card(player: Player, game: GameState) -> str:
    return (
        "🔐 <b>SIZNING BUNKER KARTANGIZ</b>\n\n"
        f"🌍 <b>Falokat:</b> {game.catastrophe['title']}\n"
        f"🛡 <b>Bunker sig'imi:</b> {game.bunker_capacity} kishi "
        f"(jami {len(game.players)} ishtirokchi)\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"💼 <b>Kasbingiz:</b> {player.profession}\n"
        f"🩺 <b>Sog'lig'ingiz:</b> {player.health}\n"
        f"🎒 <b>Buyumingiz:</b> {player.item}\n"
        f"😨 <b>Fobiyangiz:</b> {player.phobia}\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🗣 <i>Muhokama chog'ida o'zingizni himoya qiling va bunkerga "
        "nima uchun aynan siz kerak ekanligingizni isbotlang!</i>"
    )


async def _is_host_or_admin(
    bot: Bot, chat_id: int, user_id: int, game: GameState
) -> bool:
    if user_id == game.host_id:
        return True
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in {"administrator", "creator"}
    except Exception:
        return False


async def _send_player_traits(bot: Bot, player: Player, game: GameState) -> bool:
    try:
        await bot.send_message(
            chat_id=player.user_id,
            text=_format_pm_card(player, game),
        )
        player.pm_delivered = True
        return True
    except (TelegramForbiddenError, TelegramBadRequest):
        player.pm_delivered = False
        return False


async def _finalize_voting(
    bot: Bot, game: GameState, message: Message | None
) -> None:
    if not game.votes:
        return

    counts = Counter(game.votes.values())
    max_votes = max(counts.values())
    top_target_ids = [uid for uid, c in counts.items() if c == max_votes]

    is_tie = len(top_target_ids) > 1
    eliminated_id = random.choice(top_target_ids)
    eliminated = game.players[eliminated_id]
    eliminated.is_alive = False

    # Kim kimga ovoz bergani ro'yxati
    vote_details_lines = []
    for voter_id, target_id in game.votes.items():
        voter = game.players.get(voter_id)
        target = game.players.get(target_id)
        if voter and target:
            vote_details_lines.append(
                f"• {voter.mention_html} ➔ {target.mention_html}"
            )

    # Har bir nomzod olgan ovozlar soni
    tally_lines = []
    for target_id, vote_num in counts.most_common():
        target = game.players.get(target_id)
        if target:
            tally_lines.append(f"• {target.mention_html}: <b>{vote_num}</b> ta ovoz")

    if is_tie:
        tied_names = ", ".join(
            game.players[uid].mention_html for uid in top_target_ids
        )
        verdict_text = (
            f"⚖️ <b>Ovozlar teng kelib qoldi!</b> ({tied_names})\n"
            f"🎲 Qur'a tashlash natijasida {eliminated.mention_html} bunkerdan haydaldi!"
        )
    else:
        verdict_text = (
            f"🚪 Eng ko'p ovoz ({max_votes} ta) to'plagan "
            f"{eliminated.mention_html} bunkerdan haydaldi!"
        )

    result_text = (
        f"📊 <b>{game.round_number}-RAUND OVOZ BERISH NATIJALARI</b>\n\n"
        "<b>Ovozlar taqsimoti:</b>\n"
        + "\n".join(tally_lines)
        + "\n\n<b>Kim kimga ovoz berdi:</b>\n"
        + "\n".join(vote_details_lines)
        + f"\n\n{verdict_text}"
    )

    game.votes.clear()
    game.vote_message_id = None
    game.phase = GamePhase.DISCUSSION

    if message is not None:
        try:
            await message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass

    await bot.send_message(chat_id=game.chat_id, text=result_text)

    # O'yin yakunlanishini tekshirish
    alive = game.alive_players
    if len(alive) <= game.bunker_capacity:
        survivors_lines = "\n".join(
            f"🏆 {idx}. {p.mention_html} — <i>{p.profession}</i>"
            for idx, p in enumerate(alive, start=1)
        )
        win_text = (
            "🎉 <b>O'YIN YAKUNLANDI! BUNKER ESHIKLARI YOPILDI!</b>\n\n"
            f"🌍 <b>Falokat:</b> {game.catastrophe['title']}\n"
            f"🛡 <b>Bunker sig'imi:</b> {game.bunker_capacity} kishi\n\n"
            "<b>Omon qolgan baxtli insonlar:</b>\n"
            f"{survivors_lines}\n\n"
            "👏 Barcha g'oliblarni tabriklaymiz! Yangi o'yin boshlash uchun /bunker buyrug'ini bering."
        )
        await bot.send_message(chat_id=game.chat_id, text=win_text)
        games.pop(game.chat_id, None)
    else:
        next_round = game.round_number + 1
        game.round_number = next_round
        await bot.send_message(
            chat_id=game.chat_id,
            text=(
                f"👥 Tirik qolganlar: <b>{len(alive)} kishi</b> | "
                f"🛡 Bunker sig'imi: <b>{game.bunker_capacity} kishi</b>\n\n"
                f"Boshlovchi keyingi muhokamani boshlash uchun /kengash buyrug'ini bersin."
            ),
        )


# ---------------------------------------------------------------------------
# Shaxsiy xabar (PM) va umumiy buyruqlar
# ---------------------------------------------------------------------------


@router.message(Command("start"))
async def cmd_start(message: Message, bot: Bot) -> None:
    if message.chat.type != "private":
        return

    user = message.from_user
    delivered_any = False

    if user:
        for game in games.values():
            player = game.players.get(user.id)
            if (
                player is not None
                and game.phase != GamePhase.LOBBY
                and not player.pm_delivered
            ):
                ok = await _send_player_traits(bot, player, game)
                if ok:
                    delivered_any = True

    if delivered_any:
        await message.answer(
            "✅ Ajoyib! Sizga faol o'yindagi shaxsiy xususiyatlaringiz yuborildi. "
            "Endi guruhga qaytib muhokamani davom ettirishingiz mumkin!"
        )
        return

    await message.answer(
        "👋 <b>Assalomu alaykum! «Bunker» o'yini botiga xush kelibsiz!</b>\n\n"
        "Men guruhlarda psixologik «Bunker» o'yinini to'liq avtomatlashtirilgan tarzda "
        "o'tkazib beraman.\n\n"
        "📌 <b>Qanday o'ynaladi?</b>\n"
        "1. Meni biror guruhga qo'shing (admin huquqi bilan bo'lsa yaxshiroq).\n"
        "2. Guruhda /bunker buyrug'ini yuboring va do'stlaringiz bilan lobiga qo'shiling.\n"
        "3. O'yin boshlanganda barcha maxfiy xususiyatlaringizni aynan shu yerga yuboraman!\n\n"
        "📖 Qoidalar bilan tanishish uchun /qoidalar buyrug'ini bosing."
    )


@router.message(Command("help", "qoidalar"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "📖 <b>«BUNKER» O'YINI QOIDALARI VA BUYRUQLAR</b>\n\n"
        "Yer yuzida dahshatli falokat yuz berdi! Tirik qolish uchun yer osti bunkeriga "
        "kirish kerak, ammo joylar soni ishtirokchilarning yarmigagina yetadi.\n\n"
        "<b>Buyruqlar:</b>\n"
        "• /bunker — Yangi o'yin lobisini ochish (guruhda)\n"
        "• /kengash — Muhokama raundini boshlash (boshlovchi/admin)\n"
        "• /ovozberish — Haydash uchun ovoz berishni boshlash (boshlovchi/admin)\n"
        "• /holat — Joriy o'yin holatini ko'rish\n"
        "• /bekor — Faol o'yinni majburiy to'xtatish (boshlovchi/admin)\n\n"
        "⚠️ <b>Muhim:</b> O'yin boshlanishidan oldin barcha qatnashchilar botga "
        "shaxsiy xabarda /start bosgan bo'lishi kerak."
    )


# ---------------------------------------------------------------------------
# Guruh buyruqlari
# ---------------------------------------------------------------------------


@router.message(Command("bunker"))
async def cmd_bunker(message: Message) -> None:
    if message.chat.type not in {"group", "supergroup"}:
        await message.answer(
            "ℹ️ /bunker buyrug'i faqat guruhlarda ishlaydi. "
            "Meni guruhga qo'shing va o'sha yerda /bunker yozing!"
        )
        return

    chat_id = message.chat.id
    user = message.from_user
    if not user:
        return

    if chat_id in games:
        existing = games[chat_id]
        if existing.phase == GamePhase.LOBBY:
            await message.answer(
                "⚠️ Bu guruhda allaqachon ochiq lobi bor! "
                "Yuqoridagi tugma orqali qo'shiling yoki /bekor bilan yoping."
            )
        else:
            await message.answer(
                "⚠️ Bu guruhda hozir o'yin davom etmoqda! "
                "Holatni ko'rish uchun /holat, to'xtatish uchun /bekor buyrug'idan foydalaning."
            )
        return

    game = GameState(chat_id=chat_id, host_id=user.id)
    game.players[user.id] = Player(
        user_id=user.id,
        full_name=user.full_name,
        username=user.username,
    )
    games[chat_id] = game

    sent = await message.answer(
        _format_lobby_text(game),
        reply_markup=lobby_keyboard(),
    )
    game.lobby_message_id = sent.message_id


@router.message(Command("kengash"))
async def cmd_kengash(message: Message, bot: Bot) -> None:
    if message.chat.type not in {"group", "supergroup"}:
        return

    game = games.get(message.chat.id)
    if not game:
        await message.answer("ℹ️ Hozircha faol o'yin yo'q. Boshlash uchun /bunker yozing.")
        return

    if not message.from_user or not await _is_host_or_admin(
        bot, message.chat.id, message.from_user.id, game
    ):
        await message.answer("⛔️ Bu buyruqni faqat o'yin boshlovchisi yoki guruh admini bera oladi.")
        return

    if game.phase == GamePhase.LOBBY:
        await message.answer("⚠️ O'yin hali boshlanmadi! Avval lobida «O'yinni boshlash 🚀» ni bosing.")
        return

    if game.phase == GamePhase.VOTING:
        await message.answer("⚠️ Hozir ovoz berish ketmoqda! Avval ovoz berishni yakunlang.")
        return

    game.phase = GamePhase.DISCUSSION
    alive_list = "\n".join(
        f"{idx}. {p.mention_html}"
        for idx, p in enumerate(game.alive_players, start=1)
    )
    await message.answer(
        f"🗣 <b>{game.round_number}-RAUND KENGASH BOSHLANDI!</b>\n\n"
        f"🌍 <b>Falokat:</b> {game.catastrophe['title']}\n\n"
        "Har bir ishtirokchi navbat bilan o'zining birorta xususiyatini ochib, "
        "bunkerda qolishga loyiq ekanini isbotlasin.\n\n"
        f"👥 <b>Kengash a'zolari ({len(game.alive_players)} kishi):</b>\n"
        f"{alive_list}\n\n"
        "🗳 Muhokama tugagach, boshlovchi /ovozberish buyrug'ini bersin."
    )


@router.message(Command("ovozberish"))
async def cmd_ovozberish(message: Message, bot: Bot) -> None:
    if message.chat.type not in {"group", "supergroup"}:
        return

    game = games.get(message.chat.id)
    if not game:
        await message.answer("ℹ️ Hozircha faol o'yin yo'q. Boshlash uchun /bunker yozing.")
        return

    if not message.from_user or not await _is_host_or_admin(
        bot, message.chat.id, message.from_user.id, game
    ):
        await message.answer("⛔️ Ovoz berishni faqat o'yin boshlovchisi yoki guruh admini boshlay oladi.")
        return

    if game.phase == GamePhase.LOBBY:
        await message.answer("⚠️ O'yin hali boshlanmagan!")
        return

    if game.phase == GamePhase.VOTING:
        await message.answer("⚠️ Ovoz berish allaqachon davom etmoqda!")
        return

    game.votes.clear()
    game.phase = GamePhase.VOTING

    sent = await message.answer(
        f"🗳 <b>{game.round_number}-RAUND: OVOZ BERISH BOSHLANDI!</b>\n\n"
        "Bunkerdan kimni haydash kerak deb o'ylaysiz? Quyidagi tugmalardan birini tanlang.\n"
        f"<i>Ovoz berganlar: 0 / {len(game.alive_players)}</i>",
        reply_markup=voting_keyboard(game),
    )
    game.vote_message_id = sent.message_id


@router.message(Command("holat"))
async def cmd_holat(message: Message) -> None:
    if message.chat.type not in {"group", "supergroup"}:
        return

    game = games.get(message.chat.id)
    if not game:
        await message.answer("ℹ️ Bu guruhda hozir faol o'yin yo'q.")
        return

    if game.phase == GamePhase.LOBBY:
        await message.answer(_format_lobby_text(game), reply_markup=lobby_keyboard())
        return

    phase_names = {
        GamePhase.DISCUSSION: "🗣 Muhokama",
        GamePhase.VOTING: "🗳 Ovoz berish",
    }
    alive_text = "\n".join(f"✅ {p.mention_html}" for p in game.alive_players)
    dead_text = (
        "\n".join(f"❌ {p.mention_html}" for p in game.dead_players)
        if game.dead_players
        else "<i>Yo'q</i>"
    )
    await message.answer(
        f"📊 <b>O'YIN HOLATI ({game.round_number}-raund)</b>\n\n"
        f"📍 <b>Bosqich:</b> {phase_names.get(game.phase, game.phase.value)}\n"
        f"🌍 <b>Falokat:</b> {game.catastrophe['title']}\n"
        f"🛡 <b>Bunker sig'imi:</b> {game.bunker_capacity} kishi\n\n"
        f"<b>Tiriklar ({len(game.alive_players)}):</b>\n{alive_text}\n\n"
        f"<b>Haydalganlar ({len(game.dead_players)}):</b>\n{dead_text}"
    )


@router.message(Command("bekor"))
async def cmd_bekor(message: Message, bot: Bot) -> None:
    if message.chat.type not in {"group", "supergroup"}:
        return

    game = games.get(message.chat.id)
    if not game:
        await message.answer("ℹ️ Bekor qilinadigan faol o'yin yo'q.")
        return

    if not message.from_user or not await _is_host_or_admin(
        bot, message.chat.id, message.from_user.id, game
    ):
        await message.answer("⛔️ O'yinni faqat boshlovchi yoki guruh admini bekor qila oladi.")
        return

    games.pop(message.chat.id, None)
    await message.answer("🛑 O'yin to'xtatildi va lobi tozalandi. Yangi o'yin uchun /bunker yozing.")


# ---------------------------------------------------------------------------
# Callback Query handlerlari (Lobi va Ovoz berish)
# ---------------------------------------------------------------------------


@router.callback_query(F.data.startswith("lobby:"))
async def cb_lobby(callback: CallbackQuery, bot: Bot) -> None:
    if not callback.message or not callback.from_user:
        return

    chat_id = callback.message.chat.id
    user = callback.from_user
    action = callback.data.split(":", 1)[1]

    game = games.get(chat_id)
    if not game or game.phase != GamePhase.LOBBY:
        await callback.answer("Bu lobi endi faol emas.", show_alert=True)
        return

    if action == "join":
        if user.id in game.players:
            await callback.answer("Siz allaqachon ro'yxatdasiz!")
            return
        game.players[user.id] = Player(
            user_id=user.id,
            full_name=user.full_name,
            username=user.username,
        )
        await callback.answer("Siz o'yinga qo'shildingiz! ✅")
        try:
            await callback.message.edit_text(
                _format_lobby_text(game),
                reply_markup=lobby_keyboard(),
            )
        except TelegramBadRequest:
            pass
        return

    if action == "leave":
        if user.id not in game.players:
            await callback.answer("Siz ro'yxatda yo'qsiz.")
            return
        game.players.pop(user.id)
        await callback.answer("Siz lobidan chiqdingiz.")
        try:
            await callback.message.edit_text(
                _format_lobby_text(game),
                reply_markup=lobby_keyboard(),
            )
        except TelegramBadRequest:
            pass
        return

    if action == "cancel":
        if not await _is_host_or_admin(bot, chat_id, user.id, game):
            await callback.answer("Faqat boshlovchi yoki admin yopa oladi!", show_alert=True)
            return
        games.pop(chat_id, None)
        await callback.answer("Lobi yopildi.")
        try:
            await callback.message.edit_text("❌ Bunker o'yini lobisi bekor qilindi.")
        except TelegramBadRequest:
            pass
        return

    if action == "start":
        if not await _is_host_or_admin(bot, chat_id, user.id, game):
            await callback.answer("Faqat boshlovchi yoki admin boshlay oladi!", show_alert=True)
            return

        if len(game.players) < MIN_PLAYERS:
            await callback.answer(
                f"O'yinni boshlash uchun kamida {MIN_PLAYERS} kishi kerak!",
                show_alert=True,
            )
            return

        game.assign_traits()
        game.phase = GamePhase.DISCUSSION
        game.round_number = 1

        await callback.answer("O'yin boshlanmoqda! 🚀")
        try:
            await callback.message.edit_reply_markup(reply_markup=None)
        except TelegramBadRequest:
            pass

        # Guruhga falokatni e'lon qilish
        players_text = "\n".join(
            f"{idx}. {p.mention_html}"
            for idx, p in enumerate(game.players.values(), start=1)
        )
        await bot.send_message(
            chat_id=chat_id,
            text=(
                "🚨 <b>DIQQAT! O'YIN BOSHLANDI!</b>\n\n"
                f"🌍 <b>FALOKAT: {game.catastrophe['title']}</b>\n"
                f"{game.catastrophe['description']}\n\n"
                f"👥 <b>Ishtirokchilar ({len(game.players)} kishi):</b>\n"
                f"{players_text}\n\n"
                f"🛡 <b>Bunker sig'imi:</b> {game.bunker_capacity} kishi\n\n"
                "📩 Hamma o'yinchilarning shaxsiy xabariga (lichkasiga) maxfiy "
                "xususiyatlari yuborilmoqda..."
            ),
        )

        # Har bir o'yinchining lichkasiga xususiyatlarni yuborish
        blocked_players: list[Player] = []
        for player in game.players.values():
            ok = await _send_player_traits(bot, player, game)
            if not ok:
                blocked_players.append(player)

        if blocked_players:
            mentions = ", ".join(p.mention_html for p in blocked_players)
            await bot.send_message(
                chat_id=chat_id,
                text=(
                    f"⚠️ <b>Diqqat!</b> {mentions} — botga shaxsiy xabarda "
                    "<b>«Botga start bosing»</b> (/start)!\n"
                    "Botga /start bosishingiz bilan maxfiy xususiyatlaringiz avtomatik yuboriladi."
                ),
                reply_markup=bot_pm_keyboard(),
            )

        await bot.send_message(
            chat_id=chat_id,
            text="🗣 1-raundni boshlash uchun boshlovchi /kengash buyrug'ini bersin!",
        )


@router.callback_query(F.data.startswith("vote:"))
async def cb_vote(callback: CallbackQuery, bot: Bot) -> None:
    if not callback.message or not callback.from_user:
        return

    chat_id = callback.message.chat.id
    voter_id = callback.from_user.id
    payload = callback.data.split(":", 1)[1]

    game = games.get(chat_id)
    if not game or game.phase != GamePhase.VOTING:
        await callback.answer("Hozir faol ovoz berish yo'q.", show_alert=True)
        return

    if payload == "finish":
        if not await _is_host_or_admin(bot, chat_id, voter_id, game):
            await callback.answer(
                "Ovoz berishni faqat boshlovchi yoki admin yakunlay oladi!",
                show_alert=True,
            )
            return
        if not game.votes:
            await callback.answer("Hali hech kim ovoz bermadi!", show_alert=True)
            return
        await callback.answer("Ovoz berish yakunlandi!")
        await _finalize_voting(bot, game, callback.message)
        return

    # Ovoz beruvchini tekshirish
    voter = game.players.get(voter_id)
    if not voter or not voter.is_alive:
        await callback.answer("Siz bu o'yinda ovoz bera olmaysiz!", show_alert=True)
        return

    try:
        target_id = int(payload)
    except ValueError:
        await callback.answer("Noto'g'ri tanlov.", show_alert=True)
        return

    if target_id == voter_id:
        await callback.answer("O'zingizga ovoz bera olmaysiz!", show_alert=True)
        return

    target = game.players.get(target_id)
    if not target or not target.is_alive:
        await callback.answer("Bu o'yinchi allaqachon o'yindan chiqqan!", show_alert=True)
        return

    game.votes[voter_id] = target_id
    await callback.answer(f"Siz {target.short_name} ga ovoz berdingiz! ✅")

    alive_count = len(game.alive_players)
    voted_count = len(game.votes)

    if voted_count >= alive_count:
        await _finalize_voting(bot, game, callback.message)
        return

    try:
        await callback.message.edit_text(
            f"🗳 <b>{game.round_number}-RAUND: OVOZ BERISH BOSHLANDI!</b>\n\n"
            "Bunkerdan kimni haydash kerak deb o'ylaysiz? Quyidagi tugmalardan birini tanlang.\n"
            f"<i>Ovoz berganlar: {voted_count} / {alive_count}</i>",
            reply_markup=voting_keyboard(game),
        )
    except TelegramBadRequest:
        pass

