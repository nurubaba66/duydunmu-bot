"""RSS kaynaklarından haberleri toplar."""
import hashlib
import re
import time
from datetime import datetime, timezone

import feedparser
import requests

from . import config

UA = {"User-Agent": "Mozilla/5.0 (compatible; DuydunMuBot/1.0)"}


def _clean(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", text).strip()


def _published(entry) -> datetime:
    for key in ("published_parsed", "updated_parsed"):
        t = entry.get(key)
        if t:
            return datetime.fromtimestamp(time.mktime(t), tz=timezone.utc)
    return datetime.now(timezone.utc)


def item_id(title: str, link: str) -> str:
    return hashlib.sha1((link or title).encode("utf-8")).hexdigest()[:16]


def fetch_all() -> list[dict]:
    items, now = [], datetime.now(timezone.utc)
    for src in config.SOURCES:
        try:
            raw = requests.get(src["url"], headers=UA, timeout=20).content
            feed = feedparser.parse(raw)
        except Exception as e:  # bir kaynak çökerse diğerleri devam eder
            print(f"[kaynak hatası] {src['url']}: {e}")
            continue
        for e in feed.entries[:30]:
            title, link = _clean(e.get("title")), e.get("link", "")
            if not title:
                continue
            pub = _published(e)
            age_h = (now - pub).total_seconds() / 3600
            if age_h > config.MAX_ITEM_AGE_HOURS or age_h < -1:
                continue
            items.append({
                "id": item_id(title, link),
                "source": src["name"],
                "trusted": src["trusted"],
                "title": title,
                "summary": _clean(e.get("summary") or e.get("description"))[:900],
                "link": link,
                "published": pub.isoformat(),
                "age_min": int(age_h * 60),
                "breaking_hint": bool(re.search(r"son dakika|flaş", title, re.I)),
            })
    # aynı başlıkları ele
    seen, unique = set(), []
    for it in sorted(items, key=lambda x: x["age_min"]):
        key = re.sub(r"\W", "", it["title"].lower())[:60]
        if key not in seen:
            seen.add(key)
            unique.append(it)
    print(f"{len(unique)} güncel haber toplandı")
    return unique


def trends() -> list[dict]:
    """Google Trends Türkiye: o an en çok aranan konular."""
    try:
        feed = feedparser.parse(requests.get(config.TRENDS_URL, headers=UA, timeout=20).content)
        return [{"title": _clean(e.get("title")), "traffic": e.get("ht_approx_traffic", "")} for e in feed.entries[:25]]
    except Exception as e:
        print("[trend hatası]", e)
        return []
