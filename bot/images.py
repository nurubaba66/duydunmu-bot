"""Habere uygun, ticari kullanıma açık fotoğraf bulur (Openverse, anahtar gerektirmez)."""
import requests

UA = {"User-Agent": "DuydunMuBot/1.0 (https://github.com/nurubaba66/duydunmu-bot)"}


def find_photo(query: str) -> dict | None:
    if not query:
        return None
    try:
        r = requests.get(
            "https://api.openverse.org/v1/images/",
            params={"q": query, "license_type": "commercial,modification", "aspect_ratio": "wide",
                    "size": "large", "mature": "false", "page_size": 10},
            headers=UA, timeout=20,
        )
        for res in r.json().get("results", []):
            url = res.get("url")
            if not url or res.get("width", 0) < 1000:
                continue
            head = requests.get(url, headers=UA, timeout=20)
            if head.ok and head.headers.get("content-type", "").startswith("image/"):
                creator = res.get("creator") or "bilinmiyor"
                lic = (res.get("license") or "").upper()
                return {"bytes": head.content, "credit": f"Fotoğraf: {creator} ({lic}, Openverse)"}
    except Exception as e:
        print(f"[fotoğraf bulunamadı] {e}")
    return None


COMMONS = "https://commons.wikimedia.org/w/api.php"
OK_LIC = ("CC BY", "CC0", "PUBLIC DOMAIN", "PD")


def find_real_photo(query: str) -> dict | None:
    """Haberde geçen gerçek yerin/kurumun serbest lisanslı gerçek fotoğrafı (Wikimedia Commons)."""
    if not query:
        return None
    try:
        r = requests.get(COMMONS, headers=UA, timeout=20, params={
            "action": "query", "format": "json", "generator": "search", "gsrsearch": f"{query} filetype:bitmap",
            "gsrnamespace": 6, "gsrlimit": 10, "prop": "imageinfo", "iiprop": "url|size|extmetadata",
            "iiurlwidth": 1600})
        pages = sorted((r.json().get("query") or {}).get("pages", {}).values(), key=lambda p: p.get("index", 99))
        for p in pages:
            ii = (p.get("imageinfo") or [{}])[0]
            meta = ii.get("extmetadata") or {}
            lic = (meta.get("LicenseShortName", {}).get("value") or "").upper()
            if not lic.startswith(OK_LIC) or ii.get("width", 0) < 1000 or ii.get("width", 0) < ii.get("height", 1):
                continue
            url = ii.get("thumburl") or ii.get("url")
            img = requests.get(url, headers=UA, timeout=30)
            if not (img.ok and img.headers.get("content-type", "").startswith("image/jpeg")):
                continue
            import re
            artist = re.sub(r"<[^>]+>", "", meta.get("Artist", {}).get("value") or "").strip()[:40] or "Wikimedia"
            return {"bytes": img.content, "credit": f"Fotoğraf: {artist} ({lic}, Wikimedia Commons)", "real": True}
    except Exception as e:
        print(f"[gerçek fotoğraf bulunamadı] {e}")
    return None


def best_photo(place: str, generic: str) -> dict | None:
    return find_real_photo(place) or find_photo(generic)
