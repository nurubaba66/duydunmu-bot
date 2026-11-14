"""Meteoroloji Genel Müdürlüğü (MGM) MeteoUyarı verisi: bugün ve yarın için il bazında uyarılar."""
from datetime import datetime, timedelta, timezone

import requests

from . import config, maps

HDR = {"User-Agent": "Mozilla/5.0", "Origin": "https://www.mgm.gov.tr", "Referer": "https://www.mgm.gov.tr/"}
LEVELS = ["red", "orange", "yellow"]
LEVEL_TR = {"yellow": "SARI", "orange": "TURUNCU", "red": "KIRMIZI"}
EVENT_TR = {"thunderstorm": "gök gürültülü sağanak", "rain": "kuvvetli yağış", "wind": "kuvvetli rüzgar/fırtına",
            "snow": "kar", "fog": "sis", "cold": "soğuk", "hot": "sıcak", "ice": "buzlanma ve don",
            "dust": "toz taşınımı", "avalanche": "çığ", "snowmelt": "kar erimesi", "agricultural": "zirai don"}
IST = timezone(timedelta(hours=3))


def _plate(town_code: int) -> int:
    # MGM kodları 9 + plaka(2) + ilçe(2) biçiminde: 93415 -> 34
    return int(str(town_code)[1:3])


def fetch(day: str) -> list[dict]:
    try:
        r = requests.get(config.MGM_URL.format(day=day), headers=HDR, timeout=20)
        return r.json() if r.ok else []
    except Exception as e:
        print("[MGM hatası]", e)
        return []


def summarize(alerts: list[dict]) -> dict:
    """{'plates': {plaka: seviye}, 'events': set, 'alerts': [...], 'texts': {seviye: metin}}"""
    plates, events, texts, items = {}, set(), {}, []
    for a in alerts:
        for lvl in LEVELS:
            towns = (a.get("towns") or {}).get(lvl) or []
            if not towns:
                continue
            for tc in towns:
                p = _plate(tc)
                if LEVELS.index(lvl) < LEVELS.index(plates.get(p, "yellow")) or p not in plates:
                    plates[p] = lvl
            events.update((a.get("weather") or {}).get(lvl) or [])
            if (a.get("text") or {}).get(lvl):
                texts.setdefault(lvl, a["text"][lvl])
            items.append({"no": a.get("alertNo"), "level": lvl, "begin": a.get("begin"), "end": a.get("end"),
                          "plates": sorted({_plate(t) for t in towns})})
    return {"plates": plates, "events": events, "texts": texts, "alerts": items}


def names(plates) -> list[str]:
    return sorted((maps.BY_PLATE[p]["name"] for p in plates if p in maps.BY_PLATE), key=maps.norm)


def fmt_time(iso: str) -> str:
    try:
        # MGM saatleri "Z" ile gelse de sitede yerel saat olarak gösteriliyor (14.11 15:00Z -> 15.00)
        t = datetime.fromisoformat(iso.replace("Z", ""))
        return t.strftime("%d.%m %H.%M")
    except Exception:
        return ""


def max_level(s: dict) -> str | None:
    for lvl in LEVELS:
        if lvl in s["plates"].values():
            return lvl
    return None
