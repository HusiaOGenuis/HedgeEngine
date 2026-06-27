
import os

os.makedirs("core/learning", exist_ok=True)

with open("core/learning/__init__.py", "w") as f:
    pass

print("✅ Learning module fixed")