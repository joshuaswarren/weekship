"""Decide whether a piece of work was authored by a human, an AI agent or a plain bot."""
from __future__ import annotations

from .config import Config
from .model import AGENT, BOT, HUMAN, Item


def _login_key(login: str) -> str:
    return login.lower().removesuffix("[bot]")


def classify_origin(item: Item, cfg: Config) -> Item:
    """Set `origin` and `signals`. An agent signal outranks a bot signal outranks human."""
    login = _login_key(item.author)
    agent_signals: list[str] = []
    bot_signals: list[str] = []

    if login in cfg.agent_logins:
        agent_signals.append(f"author:{item.author}")
    elif login in cfg.bot_logins or item.author_type == "Bot" or item.author.endswith("[bot]"):
        bot_signals.append(f"author:{item.author}")

    branch = item.branch.lower()
    if any(branch.startswith(p) for p in cfg.agent_branch_prefixes):
        agent_signals.append(f"branch:{item.branch}")
    elif any(branch.startswith(p) for p in cfg.bot_branch_prefixes):
        bot_signals.append(f"branch:{item.branch}")

    trailer_res = cfg.trailer_res()
    for trailer in item.trailers:
        if any(r.search(trailer) for r in trailer_res):
            agent_signals.append(f"trailer:{trailer}")
            break

    identity_res = cfg.identity_res()
    for identity in item.identities:
        if any(r.search(identity) for r in identity_res):
            agent_signals.append(f"identity:{identity}")
            break

    for pattern in cfg.body_res():
        match = pattern.search(item.body)
        if match:
            agent_signals.append(f"body:{match.group(0)}")
            break

    if agent_signals:
        item.origin, item.signals = AGENT, tuple(agent_signals)
    elif bot_signals:
        item.origin, item.signals = BOT, tuple(bot_signals)
    else:
        item.origin, item.signals = HUMAN, ()
    return item
