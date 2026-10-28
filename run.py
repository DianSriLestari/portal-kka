import uvicorn
import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print("=" * 60)
    print(">>> MEMULAI PORTAL PEMBELAJARAN KKA FASE E (SMAN 7 PONTIANAK)")
    print(f">>> Port: {port}")
    print("=" * 60)
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)
