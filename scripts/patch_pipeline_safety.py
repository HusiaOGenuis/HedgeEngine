import re

path = "core/pipeline.py"

with open(path, "r") as f:
    code = f.read()

# Add safe fallback for EV
code = re.sub(
    "signal.update\\(ev_data\\)",
    """signal.update(ev_data)
        if signal.get("expected_value") is None:
            signal["expected_value"] = 0""",
    code
)

with open(path, "w") as f:
    f.write(code)

print("✅ Pipeline safety patch applied")