"""E-posta/issue onayı: sahibi 'paylaş' yazarsa bekleyen içeriği paylaşır, 'geç' yazarsa kapatır."""
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

from . import config, instagram, notify
from .main import IST, PENDING, load_state, save_state


def run(issue: int, body: str, author: str):
    if author.lower() != config.OWNER_LOGIN.lower():
        print("Sahibi olmayan yorum, yok sayıldı.")
        return
    text = body.strip().lower().split("\n")[0]
    folder = next((p.parent for p in PENDING.glob("*/issue.json")
                   if json.loads(p.read_text())["issue"] == issue), None)
    if not folder:
        print("Bu issue için bekleyen içerik yok.")
        return
    if "geç" in text or "gec" in text or "iptal" in text:
        notify.comment(issue, "Tamam reis, paylaşılmadı. 👍", close=True)
        shutil.rmtree(folder)
        return
    if "paylaş" not in text and "paylas" not in text and "evet" not in text:
        return
    post = json.loads((folder / "post.json").read_text(encoding="utf-8"))
    files = [folder / f for f in post["files"]]
    media = instagram.publish(files, post["caption"])
    state = load_state()
    state["log"].append({"t": datetime.now(IST).isoformat(timespec="minutes"), "fmt": post["type"],
                         "title": post["title"], "media": media, "manual": True})
    save_state(state)
    shutil.rmtree(folder)
    notify.comment(issue, "Paylaşıldı reis ✅", close=True)


if __name__ == "__main__":
    run(int(sys.argv[1]), os.environ.get("COMMENT_BODY", ""), os.environ.get("COMMENT_AUTHOR", ""))
