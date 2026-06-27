def enrich_with_research(signal):

    # ✅ SIMULATED HOOK (replace with real DB calls later)
    dna_map = {
        "EURUSD": 0.55,
        "GBPUSD": 0.58,
        "USDJPY": 0.52,
        "AUDUSD": 0.54,
        "USDCAD": 0.45,
        "EURJPY": 0.72,
        "GBPJPY": 0.78,
        "XAUUSD": 0.80,
        "XAGUSD": 0.75,
        "BTCUSD": 0.90,
        "ETHUSD": 0.85,
        "NAS100": 0.88
    }

    signal["asset_dna"] = dna_map.get(signal["symbol"], 0.6)

    # ✅ dynamic volatility (placeholder logic → plug DB later)
    signal["atr_percentile"] = 0.5 + signal["asset_dna"] * 0.5

    # ✅ correlation proxy (crypto higher)
    signal["correlation"] = 0.4 if "USD" not in signal["symbol"] else 0.2

    # ✅ regime proxy
    signal["market_regime"] = 0.6 + signal["signal_score"] * 0.4

    signal["session_quality"] = 1.0
    signal["portfolio_context"] = 0.5

    return signal
