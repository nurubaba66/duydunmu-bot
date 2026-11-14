"""Duydun mu? ana döngü. GitHub Actions her 15 dakikada bir çalıştırır."""
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from . import config, images, instagram, render, sources, writer

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "state" / "state.json"
OUT = ROOT / "out"
IST = timezone(timedelta(hours=3))


def load_state() -> dict:
    if STATE.exists():
        return json.loads(STATE.read_text(encoding="utf-8"))
    return {"posted": [], "scores": {}, "slots_done": [], "breaking": {}, "log": []}


def save_state(s: dict):
    s["posted"] = s["posted"][-500:]
    s["scores"] = dict(list(s["scores"].items())[-800:])
    s["slots_done"] = s["slots_done"][-60:]
    s["log"] = s["log"][-200:]
    STATE.parent.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(s, ensure_ascii=False, indent=1), encoding="utf-8")


def caption_for(d: dict, credit: str = "") -> str:
    parts = [d.get("caption", "").strip(), f"Kaynak: {d['source']}"]
    if credit:
        parts.append(credit)
    parts.append(config.HASHTAGS)
    return "\n\n".join(p for p in parts if p)[:2150]


def post(item: dict, fmt: str, state: dict, now: datetime):
    d = writer.write_post(item, fmt)
    if not d.get("headline"):
        print("Metin üretilemedi, atlandı:", item["title"])
        state["posted"].append(item["id"])
        return False
    stem = f"{now:%Y%m%d_%H%M}_{item['id']}"
    credit = ""
    if fmt == "breaking":
        pages = [render.breaking_html(d, now.strftime("%d.%m.%Y · %H:%M"))]
    elif fmt == "carousel":
        pages = render.carousel_html(d)
    else:
        photo = images.find_photo(d.get("image_query", ""))
        if photo:
            credit = photo["credit"]
        pages = [render.card_html(d, photo["bytes"] if photo else None)]
    paths = render.to_jpgs(pages, OUT, stem)
    media_id = instagram.publish(paths, caption_for(d, credit))
    state["posted"].append(item["id"])
    state["log"].append({"t": now.isoformat(timespec="minutes"), "fmt": fmt, "title": item["title"], "media": media_id})
    return True


def main():
    if not config.ANTHROPIC_API_KEY:
        sys.exit("ANTHROPIC_API_KEY eksik")
    now = datetime.now(IST)
    today = now.strftime("%Y-%m-%d")
    state = load_state()

    items = [i for i in sources.fetch_all() if i["id"] not in state["posted"]]
    new = [i for i in items if i["id"] not in state["scores"]]
    if new:
        for it in writer.score_items(new):
            state["scores"][it["id"]] = {"score": it["score"], "breaking": it["breaking"], "category": it["category"]}
    for it in items:
        it.update(state["scores"].get(it["id"], {"score": 0, "breaking": False, "category": "GÜNDEM"}))
    ranked = sorted([i for i in items if i["score"] >= config.MIN_SCORE], key=lambda x: (-x["score"], x["age_min"]))

    # 1) Son dakika: sadece güvenilir kaynak, taze ve gerçekten önemli
    br_count = state["breaking"].get(today, 0)
    for it in ranked:
        if (it["breaking"] and it["trusted"] and it["age_min"] <= config.BREAKING_MAX_AGE_MIN
                and it["score"] >= 8 and br_count < config.MAX_BREAKING_PER_DAY):
            if post(it, "breaking", state, now):
                state["breaking"][today] = br_count + 1
            save_state(state)
            return

    # 2) Planlı paylaşım saatleri
    slot = f"{today}-{now.hour}"
    if now.hour in config.POST_SLOTS and slot not in state["slots_done"]:
        state["slots_done"].append(slot)
        if ranked:
            fmt = "carousel" if now.hour in (12, 18) else "card"
            post(ranked[0], fmt, state, now)
        else:
            print("Bu saat için yeterince güçlü haber yok.")
    save_state(state)


if __name__ == "__main__":
    main()
