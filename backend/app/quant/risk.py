from __future__ import annotations

from app.config import get_settings
from app.models.trade import Trade
from app.quant.constants import CONTRACT_MULTIPLIER


def evaluate_trade_risk(
    trade: Trade,
    open_position_count: int = 0,
    realized_loss_today: float = 0.0,
) -> tuple[bool, str]:
    settings = get_settings()

    if open_position_count >= settings.max_open_positions:
        return (
            False,
            f"{open_position_count} positions already open "
            f"(limit {settings.max_open_positions}).",
        )

    if realized_loss_today <= -settings.max_daily_loss:
        return (
            False,
            f"Realized loss today ${-realized_loss_today:.2f} has hit the daily limit "
            f"${settings.max_daily_loss:.2f}.",
        )

    total_risk = trade.max_loss * trade.quantity * CONTRACT_MULTIPLIER
    if total_risk > settings.max_position_risk:
        return False, f"Max loss ${total_risk:.2f} exceeds limit ${settings.max_position_risk:.2f}."

    return True, "Within risk limits."


def kelly_fraction(win_probability: float, win_loss_ratio: float) -> float:
    if win_loss_ratio <= 0:
        return 0.0
    fraction = win_probability - (1 - win_probability) / win_loss_ratio
    return max(0.0, min(1.0, fraction))
