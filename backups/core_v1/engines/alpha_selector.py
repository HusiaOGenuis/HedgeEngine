def rank_and_select(signals):

    # ✅ rank by EV * DNA (true alpha score)
    ranked = sorted(
        signals,
        key=lambda x: x["expected_value"] * x["asset_dna"],
        reverse=True
    )

    # ✅ select top 5 only
    return ranked[:5]
