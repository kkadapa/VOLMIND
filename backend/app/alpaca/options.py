from __future__ import annotations

import re
from datetime import datetime, timezone

from alpaca.data.requests import OptionChainRequest, OptionLatestQuoteRequest
from loguru import logger

from app.alpaca.client import get_option_data_client
from app.models.opportunity import OptionLeg, OptionType

_OCC_SYMBOL_RE = re.compile(r"^(?P<root>[A-Z]+)(?P<expiry>\d{6})(?P<type>[CP])(?P<strike>\d{8})$")


def _parse_occ_symbol(contract_symbol: str) -> tuple[OptionType, float, datetime]:
    match = _OCC_SYMBOL_RE.match(contract_symbol)
    if not match:
        raise ValueError(f"Unrecognized OCC option symbol: {contract_symbol}")
    option_type = OptionType.CALL if match["type"] == "C" else OptionType.PUT
    strike = int(match["strike"]) / 1000
    expiry = datetime.strptime(match["expiry"], "%y%m%d").replace(tzinfo=timezone.utc)
    return option_type, strike, expiry


def get_option_chain(symbol: str) -> list[OptionLeg]:
    client = get_option_data_client()
    request = OptionChainRequest(underlying_symbol=symbol)
    chain = client.get_option_chain(request)

    legs: list[OptionLeg] = []
    for contract_symbol, snapshot in chain.items():
        quote = snapshot.latest_quote
        greeks = snapshot.greeks
        if quote is None:
            continue
        try:
            option_type, strike, expiry = _parse_occ_symbol(contract_symbol)
        except ValueError:
            # Post-corporate-action "adjusted" contracts (e.g. a root of "BA1"
            # after a split/spinoff) don't match the standard OCC format. Skip
            # just this one contract rather than failing the whole chain --
            # and the whole scan, for every symbol in a multi-symbol request.
            logger.warning("get_option_chain: skipping unparseable contract {}", contract_symbol)
            continue
        if expiry.date() <= datetime.now(timezone.utc).date():
            # A contract expiring today (0DTE) or earlier can already be
            # rejected by Alpaca as "expired" by the time an order reaches
            # it, even though the chain snapshot still returns a live quote
            # for it. Not a tradeable candidate -- exclude it at the source
            # so nothing downstream (pricing, diligence, execution) ever
            # considers it.
            continue
        legs.append(
            OptionLeg(
                symbol=contract_symbol,
                option_type=option_type,
                strike=strike,
                expiry=expiry,
                bid=quote.bid_price,
                ask=quote.ask_price,
                implied_volatility=snapshot.implied_volatility,
                delta=greeks.delta if greeks else None,
                gamma=greeks.gamma if greeks else None,
                theta=greeks.theta if greeks else None,
                vega=greeks.vega if greeks else None,
            )
        )
    return legs


def get_option_quote(symbol: str) -> tuple[float, float] | None:
    """Latest (bid, ask) for one option contract, used to mark an open position."""
    client = get_option_data_client()
    quote = client.get_option_latest_quote(
        OptionLatestQuoteRequest(symbol_or_symbols=symbol)
    ).get(symbol)
    if quote is None:
        return None
    return quote.bid_price, quote.ask_price
