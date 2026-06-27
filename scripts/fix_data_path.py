import os

def find_file(filename):
    for root, dirs, files in os.walk(".."):
        if filename in files:
            return os.path.abspath(os.path.join(root, filename))
    return None

path = find_file("trade_ledger.csv")

os.makedirs("config", exist_ok=True)

if path:
    with open("config/data_path.txt", "w") as f:
        f.write(path)
    print("✅ FOUND:", path)
else:
    print("❌ trade_ledger.csv NOT FOUND")