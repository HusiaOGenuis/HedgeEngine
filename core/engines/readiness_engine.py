def system_ready(signal):

    checks = []

    checks.append(signal.get("expected_value", 0) > 0.2)
    checks.append(signal.get("confidence") == "HIGH")
    checks.append(signal.get("asset_dna", 0) > 0.6)

    return all(checks)
