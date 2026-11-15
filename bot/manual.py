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
    if post.get("render") and not post.get("files"):  # metinden carousel üret (fotoğrafı kendisi bulur)
        from . import images, render
        d = post["render"]
        if d.get("photo_file"):  # sahibinin verdiği fotoğraf
            photo = {"bytes": (base / d["photo_file"]).read_bytes(), "credit": ""}
        else:
            photo = images.best_photo(d.get("place_query", ""), d.get("image_query", ""))
        if photo and photo["credit"]:
            post["caption"] += "\n\n" + photo["credit"]
        pb = photo["bytes"] if photo else None
        pages = [render.card_html(d, pb)] if post["type"] == "image" else render.carousel_html(d, pb)
        paths = render.to_jpgs(pages, base, "kart")
        post["files"] = [Path(x).name for x in paths]
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
