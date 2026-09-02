#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from dotenv import load_dotenv

from app.services.scanner import Scanner


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Scan symbols for options opportunities.")
    parser.add_argument("symbols", nargs="+", help="Underlying ticker symbols to scan.")
    args = parser.parse_args()

    scanner = Scanner()
    results = scanner.scan(args.symbols)
    for state in results:
        opportunity = state["opportunity"]
        print(
            f"{opportunity.underlying_symbol}: "
            f"divergence={state.get('divergence_score')} "
            f"risk_approved={state.get('risk_approved')}"
        )


if __name__ == "__main__":
    main()
