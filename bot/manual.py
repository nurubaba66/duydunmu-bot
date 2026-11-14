"""Elle hazırlanan paylaşımları yayınlar: manual/<klasör>/post.json"""
import json
import sys
from datetime import datetime
from pathlib import Path

from . import instagram
from .main import IST, load_state, save_state


def run(folder: str):
    base = Path(folder)
    post = json.loads((base / "post.json").read_text(encoding="utf-8"))
    files = [base / f for f in post["files"]]
    if post["type"] == "reel":
        media = instagram.publish_reel(files[0], post["caption"])
    else:
        media = instagram.publish(files, post["caption"])
    state = load_state()
    now = datetime.now(IST)
    state["log"].append({"t": now.isoformat(timespec="minutes"), "fmt": post["type"], "title": post["title"],
                         "media": media, "manual": True})
    save_state(state)
    (base / "PAYLASILDI").write_text(f"{now.isoformat()} {media}\n", encoding="utf-8")


if __name__ == "__main__":
    run(sys.argv[1])
