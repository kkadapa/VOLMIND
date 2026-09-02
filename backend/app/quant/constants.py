from __future__ import annotations

# Standard equity option contract controls 100 shares. Alpaca quotes/order prices are
# always per-share; every dollar-denominated figure (risk limits, P&L) must be scaled by
# this to mean anything in real money. Order submission itself (limit_price) stays
# per-share -- that's what the Alpaca API expects -- so this only applies at the sites
# that compute or compare dollar amounts.
CONTRACT_MULTIPLIER = 100
