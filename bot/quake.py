"""AFAD deprem verisi: belirli büyüklüğün üstündeki yeni depremleri bulur."""
import re
from datetime import datetime, timedelta, timezone

import requests

from . import config, maps

UA = {"User-Agent": "Mozilla/5.0 (compatible; DuydunMuBot/1.0)"}


def recent(now_utc: datetime) -> list[dict]:
    start = (now_utc - timedelta(minutes=config.QUAKE_MAX_AGE_MIN)).strftime("%Y-%m-%dT%H:%M:%S")
    end = (now_utc + timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%S")
    try:
        r = requests.get(config.AFAD_URL, params={"start": start, "end": end, "minmag": config.QUAKE_MIN_MAG,
                                                  "orderby": "timedesc", "format": "json"}, headers=UA, timeout=20)
        data = r.json()
    except Exception as e:
        print("[AFAD hatası]", e)
        return []
    out = []
    for q in data if isinstance(data, list) else []:
        try:
            mag = float(q.get("magnitude"))
            t = datetime.fromisoformat(str(q.get("date")).replace("Z", "")).replace(tzinfo=timezone.utc)
        except Exception:
            continue
        loc = q.get("location") or ""
        prov = q.get("province") or ""
        if not prov:
            m = re.search(r"\(([^)]+)\)", loc)
            prov = m.group(1) if m else loc
        if str(q.get("country", "Türkiye")) not in ("Türkiye", "Turkey", "None", ""):
            continue
        out.append({"id": f"afad-{q.get('eventID') or q.get('eventId') or t.isoformat()}", "mag": mag,
                    "location": loc.title() if loc.isupper() else loc, "province": prov,
                    "district": q.get("district") or "", "depth": q.get("depth"), "time": t,
                    "plate": (maps.province(prov) or {}).get("plate")})
    return out
