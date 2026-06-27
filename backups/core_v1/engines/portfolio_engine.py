def portfolio_optimize(signals):

    # ✅ sort by alpha score
    signals = sorted(
        signals,
        key=lambda x: x["expected_value"] * x["asset_dna"],
        reverse=True
    )

    selected = []
    total_risk = 0

    for s in signals:

        risk = s.get("recommended_risk", 0.01)

        # ✅ enforce total risk cap (~5%)
        if total_risk + risk > 0.05:
            continue

        # ✅ avoid correlation stacking
        correlated = any(
            abs(s["correlation"] - x["correlation"]) < 0.05
            for x in selected
        )

        if correlated:
            continue

        selected.append(s)
        total_risk += risk

    return selected
