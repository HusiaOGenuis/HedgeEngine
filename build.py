import sys
import os

def build_prod():
    print("\n🚀 Building PRODUCTION system...")
    os.system("python scripts/build_system.py")
    os.system("python scripts/build_ev_curve.py")
    os.system("python scripts/update_ev_engine.py")

def build_research():
    print("\n🔬 Building RESEARCH system...")
    os.system("python scripts/build_validation.py")

if __name__ == "__main__":
    if "--prod" in sys.argv:
        build_prod()
    elif "--research" in sys.argv:
        build_research()
    else:
        print("Usage:")
        print("  python build.py --prod")
        print("  python build.py --research")