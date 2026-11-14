"""Duydun mu? ana döngü: her turda deprem, hava uyarıları, son dakika, planlı paylaşım ve video radarına bakar."""
import json
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

from . import config, images, instagram, mgm, notify, quake, render, sources, writer

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "state" / "state.json"
OUT = ROOT / "out"
PENDING = ROOT / "pending"
IST = timezone(timedelta(hours=3))


def load_state() -> dict:
    s = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}
    for k, v in {"posted": [], "scores": {}, "slots_done": [], "breaking": {}, "log": [], "quakes": [],
                 "mgm_alerts": [], "mgm_days": [], "radar": []}.items():
        s.setdefault(k, v)
    return s


def save_state(s: dict):
    s["posted"] = s["posted"][-800:]
    s["scores"] = dict(list(s["scores"].items())[-1500:])
    for k in ("slots_done", "quakes", "mgm_alerts", "mgm_days", "radar"):
        s[k] = s[k][-200:]
    s["log"] = s["log"][-300:]
    STATE.parent.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(s, ensure_ascii=False, indent=1), encoding="utf-8")


def caption_for(d: dict, credit: str = "") -> str:
    parts = [d.get("caption", "").strip(), f"Kaynak: {d['source']}"]
    if credit:
        parts.append(credit)
    parts.append(config.HASHTAGS)
    return "\n\n".join(p for p in parts if p)[:2150]


def _log(state, now, fmt, title, media, **extra):
    state["log"].append({"t": now.isoformat(timespec="minutes"), "fmt": fmt, "title": title, "media": media, **extra})


def publish_or_ask(state, now, pages: list[str], caption: str, title: str, fmt: str, review_reason: str = "",
                   item_id: str = ""):
    stem = f"{now:%Y%m%d_%H%M}_{abs(hash(title)) % 10**8}"
    paths = render.to_jpgs(pages, OUT, stem)
    if item_id:
        state["posted"].append(item_id)
    if review_reason and not config.DRY_RUN:
        folder = PENDING / stem
        folder.mkdir(parents=True, exist_ok=True)
        files = []
        for p in paths:
            shutil.copy(p, folder / p.name)
            files.append(p.name)
        post = {"type": "carousel" if len(files) > 1 else "image", "files": files, "caption": caption, "title": title}
        (folder / "post.json").write_text(json.dumps(post, ensure_ascii=False, indent=1), encoding="utf-8")
        num = notify.ask_approval(folder, post, review_reason)
        _log(state, now, fmt, title, f"onay-bekliyor#{num}", review=True)
        print("Onaya gönderildi:", title)
        return
    media = instagram.publish(paths, caption)
    _log(state, now, fmt, title, media)


def post_item(item: dict, fmt: str, state: dict, now: datetime):
    d = writer.write_post(item, fmt)
    if not d.get("headline"):
        print("Metin üretilemedi, atlandı:", item["title"])
        state["posted"].append(item["id"])
        return
    credit = ""
    if fmt == "breaking":
        pages = [render.breaking_html(d, now.strftime("%d.%m.%Y · %H:%M"))]
    elif fmt == "carousel":
        pages = render.carousel_html(d)
    else:
        photo = images.find_photo(d.get("image_query", ""))
        credit = photo["credit"] if photo else ""
        pages = [render.card_html(d, photo["bytes"] if photo else None)]
    reason = ""
    if item.get("review"):
        reason = "Haber bir kişiyle ilgili iddia, parti siyaseti ya da tek kaynaklı iddialı bilgi içeriyor."
    publish_or_ask(state, now, pages, caption_for(d, credit), item["title"], fmt, reason, item["id"])


# ------------------------------------------------------------------ özel modüller
def do_quakes(state, now) -> bool:
    for q in quake.recent(now.astimezone(timezone.utc)):
        if q["id"] in state["quakes"]:
            continue
        state["quakes"].append(q["id"])
        q["time_local"] = q["time"].astimezone(IST).strftime("%H.%M")
        cap = (f"🔴 {q['location']} merkezli {q['mag']:.1f} büyüklüğünde deprem meydana geldi.\n\n"
               f"AFAD'ın verilerine göre deprem saat {q['time_local']}'te, yerin yaklaşık {q.get('depth') or '-'} km "
               f"derinliğinde gerçekleşti. Gelişmeleri takip ediyoruz.\n\n"
               "Sen de hissettin mi? Bulunduğun yeri yorumlara yaz.\n\nKaynak: AFAD\n"
               "#deprem #sondakika #afad #" + "".join(ch for ch in (q["province"] or "").lower() if ch.isalpha()) + " #duydunmu")
        publish_or_ask(state, now, [render.quake_html(q, now.strftime("%d.%m.%Y · %H:%M"))], cap,
                       f"{q['location']} {q['mag']:.1f} deprem", "deprem")
        return True
    return False


def do_mgm(state, now) -> bool:
    today_raw, tom_raw = mgm.fetch("today"), mgm.fetch("tomorrow")
    t, m = mgm.summarize(today_raw), mgm.summarize(tom_raw)
    if not t["plates"] and not m["plates"]:
        return False
    day = now.strftime("%Y-%m-%d")
    new_severe = [a for a in t["alerts"] + m["alerts"]
                  if a["level"] in ("orange", "red") and f'{a["no"]}-{a["level"]}' not in state["mgm_alerts"]]
    # Bugün elle ya da otomatik bir hava uyarısı paylaşıldıysa sabah bülteni tekrar yapılmaz
    weather_done = any(l["t"].startswith(day) and (l.get("fmt") == "hava" or any(k in l.get("title", "").lower()
                       for k in ("sarı kod", "turuncu kod", "kırmızı kod", "mgm", "meteoroloji")))
                       for l in state["log"])
    bulletin_due = now.hour >= config.MGM_BULLETIN_HOUR and day not in state["mgm_days"] and not weather_done
    if not (new_severe or bulletin_due):
        return False
    for a in t["alerts"] + m["alerts"]:
        state["mgm_alerts"].append(f'{a["no"]}-{a["level"]}')
    state["mgm_days"].append(day)
    months = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
    d1 = f"{now.day} {months[now.month - 1]}"
    tm = now + timedelta(days=1)
    d2 = f"{tm.day} {months[tm.month - 1]}"
    pages = render.mgm_pages(t, m, d1, d2)
    worst = mgm.max_level(t) or mgm.max_level(m)
    lines = [f"⚠️ Meteoroloji {mgm.LEVEL_TR[worst].lower()} kodlu uyarı yaptı."]
    if t["plates"]:
        lines.append(f"📍 BUGÜN ({d1}) – {len(t['plates'])} il: " + ", ".join(mgm.names(t["plates"])) + ".")
    if m["plates"]:
        lines.append(f"📍 YARIN ({d2}) – {len(m['plates'])} il: " + ", ".join(mgm.names(m["plates"])) + ".")
    txt = next(iter(t["texts"].values()), "") or next(iter(m["texts"].values()), "")
    if txt:
        lines.append(txt)
    lines += ["Senin olduğun yerde hava nasıl?", "Kaynak: Meteoroloji Genel Müdürlüğü",
              "#havadurumu #meteoroloji #uyarı #gündem #duydunmu"]
    publish_or_ask(state, now, pages, "\n\n".join(lines), f"MGM uyarı {day}", "hava")
    return True


def do_radar(state, now, items):
    key = f"{now:%Y-%m-%d}-{now.hour}"
    if now.hour not in config.RADAR_HOURS or key in state["radar"]:
        return
    state["radar"].append(key)
    vids = [i for i in items if i.get("video")] or items
    body = writer.radar(vids, sources.trends())
    notify.open_issue(f"🎬 Video radarı · {now:%d.%m %H:%M}",
                      "Reis, bugün Reels için görüntüsü olabilecek olaylar bunlar. Videosunu bulursan bana gönder, "
                      "kurgulayıp paylaşayım.\n\n" + body, labels=("radar",))


# ------------------------------------------------------------------ tek tur
def cycle(now: datetime | None = None):
    now = now or datetime.now(IST)
    today = now.strftime("%Y-%m-%d")
    state = load_state()
    try:
        if not config.DRY_RUN:
            if do_quakes(state, now):
                return
            if do_mgm(state, now):
                return

        items = [i for i in sources.fetch_all() if i["id"] not in state["posted"]]
        cutoff = (now - timedelta(hours=48)).isoformat(timespec="minutes")
        recent = [l["title"] for l in state["log"] if l["t"] >= cutoff]
        new = [i for i in items if i["id"] not in state["scores"]]
        if new:
            for it in writer.score_items(new[:40], recent):
                state["scores"][it["id"]] = {k: it.get(k) for k in ("score", "breaking", "category", "review", "video")}
        for it in items:
            it.update(state["scores"].get(it["id"]) or {"score": 0, "breaking": False, "category": "GÜNDEM"})
        ranked = sorted([i for i in items if (i.get("score") or 0) >= config.MIN_SCORE],
                        key=lambda x: (-x["score"], x["age_min"]))

        if config.DRY_RUN:
            print("En iyi haberler:", [(i["score"], i["category"], i["title"]) for i in ranked[:10]])
            for it, fmt in zip(ranked[:3], ["card", "carousel", "breaking"]):
                post_item(it, fmt, {"posted": [], "log": []}, now)
            return

        do_radar(state, now, ranked)

        # Son dakika: güvenilir kaynak, taze, önemli, onay gerektirmeyen
        br = state["breaking"].get(today, 0)
        for it in ranked:
            if (it.get("breaking") and it["trusted"] and not it.get("review") and it["age_min"] <= config.BREAKING_MAX_AGE_MIN
                    and it["score"] >= 8 and br < config.MAX_BREAKING_PER_DAY):
                post_item(it, "breaking", state, now)
                state["breaking"][today] = br + 1
                return

        # Elle paylaşımdan sonraki 60 dakika planlı paylaşım yok
        last_manual = max((l["t"] for l in state["log"] if l.get("manual")), default="")
        if last_manual and last_manual >= (now - timedelta(minutes=60)).isoformat(timespec="minutes"):
            print("Az önce elle paylaşım yapıldı, planlı paylaşım bekliyor.")
            return

        slot = f"{today}-{now.hour}"
        if now.hour in config.POST_SLOTS and slot not in state["slots_done"]:
            state["slots_done"].append(slot)
            last_cat = next((l.get("cat") for l in reversed(state["log"]) if l.get("cat")), None)
            pool = ranked
            if now.hour in config.LIGHT_SLOTS:
                light = [i for i in ranked if i["category"] in config.LIGHT_CATEGORIES]
                pool = light or ranked
            pick = next((i for i in pool if i["category"] != last_cat), pool[0] if pool else None)
            if pick:
                fmt = "carousel" if now.hour in config.CAROUSEL_SLOTS else "card"
                post_item(pick, fmt, state, now)
                if state["log"]:
                    state["log"][-1]["cat"] = pick["category"]
            else:
                print("Bu saat için yeterince güçlü haber yok.")
    finally:
        if not config.DRY_RUN:
            save_state(state)


def main():
    if not config.ANTHROPIC_API_KEY or not (config.IG_ACCESS_TOKEN or config.DRY_RUN):
        print("Anahtarlar henüz eklenmedi, bekleniyor.")
        return
    cycle()


if __name__ == "__main__":
    main()
