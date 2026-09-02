from __future__ import annotations

from app.models.opportunity import OptionLeg, OptionType

# How far (as a fraction of spot) a strike may sit from the underlying price and
# still be considered "near the money." Contracts outside this band are usually
# thin/stale-quoted and can carry unreliable or missing delta data -- including
# them lets a deep ITM/OTM contract get picked just because it's the only one
# with a cached Greek, which produces a nonsensical "probability."
MONEYNESS_BAND = 0.15


def implied_probability_from_chain(legs: list[OptionLeg], underlying_price: float) -> float:
    """Approximate P(price above spot at expiry) from a near-the-money call's delta.

    This is a rough proxy, not a real risk-neutral probability: call delta is
    N(d1), not N(d2) (the actual risk-neutral P(S_T > K) under Black-Scholes), and
    using it here additionally assumes strike ~= spot so the distinction is small.
    It also collapses every expiration in the chain into one number rather than
    picking a horizon-matched one. Treat this as a coarse market-sentiment signal,
    not a calibrated distribution -- Agent 5 in the product spec (skew, per-expiry
    term structure, liquidity-weighted) is not yet implemented.
    """
    near_money_calls = [
        leg
        for leg in legs
        if leg.option_type == OptionType.CALL
        and leg.delta is not None
        and underlying_price > 0
        and abs(leg.strike - underlying_price) / underlying_price <= MONEYNESS_BAND
    ]
    if not near_money_calls:
        return 0.5
    atm_call = min(near_money_calls, key=lambda leg: abs(leg.strike - underlying_price))
    return max(0.0, min(1.0, atm_call.delta))
