"""Har bir guruh uchun izolyatsiyalangan o'yin holati (In-Memory Dictionary)."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum

from bot.data import CATASTROPHES, HEALTH_CONDITIONS, ITEMS, PHOBIAS, PROFESSIONS


class GamePhase(str, Enum):
    LOBBY = "lobby"
    DISCUSSION = "discussion"
    VOTING = "voting"


@dataclass
class Player:
    user_id: int
    full_name: str
    username: str | None = None
    profession: str = ""
    health: str = ""
    item: str = ""
    phobia: str = ""
    is_alive: bool = True
    pm_delivered: bool = False

    @property
    def mention_html(self) -> str:
        safe_name = (
            self.full_name.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        return f'<a href="tg://user?id={self.user_id}">{safe_name}</a>'

    @property
    def short_name(self) -> str:
        return self.full_name[:28] + ("…" if len(self.full_name) > 28 else "")


@dataclass
class GameState:
    chat_id: int
    host_id: int
    phase: GamePhase = GamePhase.LOBBY
    round_number: int = 0
    bunker_capacity: int = 0
    catastrophe: dict[str, str] = field(default_factory=dict)
    players: dict[int, Player] = field(default_factory=dict)
    votes: dict[int, int] = field(default_factory=dict)  # voter_id -> target_id
    lobby_message_id: int | None = None
    vote_message_id: int | None = None

    @property
    def alive_players(self) -> list[Player]:
        return [p for p in self.players.values() if p.is_alive]

    @property
    def dead_players(self) -> list[Player]:
        return [p for p in self.players.values() if not p.is_alive]

    def assign_traits(self) -> None:
        """O'yinchilarga tasodifiy xususiyatlar va falokatni taqsimlaydi."""
        self.catastrophe = random.choice(CATASTROPHES)
        player_list = list(self.players.values())
        count = len(player_list)

        professions = _sample_with_fallback(PROFESSIONS, count)
        healths = _sample_with_fallback(HEALTH_CONDITIONS, count)
        items = _sample_with_fallback(ITEMS, count)
        phobias = _sample_with_fallback(PHOBIAS, count)

        for idx, player in enumerate(player_list):
            player.profession = professions[idx]
            player.health = healths[idx]
            player.item = items[idx]
            player.phobia = phobias[idx]
            player.is_alive = True
            player.pm_delivered = False

        # Bunker sig'imi qatnashchilar sonining yarmiga (yaxlitlangan holda) teng
        self.bunker_capacity = max(1, round(count / 2))


def _sample_with_fallback(pool: list[str], count: int) -> list[str]:
    if count <= len(pool):
        return random.sample(pool, count)
    result = random.sample(pool, len(pool))
    result.extend(random.choices(pool, k=count - len(pool)))
    random.shuffle(result)
    return result


# Guruh ID -> GameState (o'nlab guruhlarda bir vaqtda izolyatsiyalangan holatda ishlaydi)
games: dict[int, GameState] = {}

