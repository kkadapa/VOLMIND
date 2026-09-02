from __future__ import annotations

from alpaca.trading.enums import OrderClass, OrderSide, TimeInForce
from alpaca.trading.requests import LimitOrderRequest, OptionLegRequest

from app.alpaca.client import get_trading_client
from app.models.trade import Trade


def get_account():
    return get_trading_client().get_account()


def get_open_positions():
    return get_trading_client().get_all_positions()


def get_clock():
    return get_trading_client().get_clock()


def close_position(trade: Trade):
    """Submit closing (sell-to-close) orders for every leg of an open trade.

    Uses Alpaca's own close_position, which submits a market order sized to flatten
    the position -- correct for the single-leg trades the strategy pricer currently
    produces. Multi-leg spreads would need per-leg netting, not yet a case that arises.
    """
    client = get_trading_client()
    return [client.close_position(leg.symbol) for leg in trade.legs]


def submit_trade(trade: Trade, limit_price: float):
    client = get_trading_client()

    if len(trade.legs) == 1:
        leg = trade.legs[0]
        request = LimitOrderRequest(
            symbol=leg.symbol,
            qty=trade.quantity,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.DAY,
            limit_price=limit_price,
        )
        return client.submit_order(request)

    order_legs = [
        OptionLegRequest(symbol=leg.symbol, side=OrderSide.BUY, ratio_qty=1)
        for leg in trade.legs
    ]
    request = LimitOrderRequest(
        qty=trade.quantity,
        side=OrderSide.BUY,
        time_in_force=TimeInForce.DAY,
        order_class=OrderClass.MLEG,
        limit_price=limit_price,
        legs=order_legs,
    )
    return client.submit_order(request)
