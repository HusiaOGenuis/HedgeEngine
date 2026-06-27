import os

def find_file(filename):
    for root, dirs, files in os.walk("."):
        if filename in files:
            return os.path.join(root, filename)
    return None

# Save path globally
path = find_file("trade_ledger.csv")

if path is None:
    print("❌ trade_ledger.csv not found")
else:
    with open("config/data_path.txt", "w") as f:
        f.write(path)

    print("✅ Data path saved:", path)