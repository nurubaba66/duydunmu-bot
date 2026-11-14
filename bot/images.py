"""Habere uygun, ticari kullanıma açık fotoğraf bulur (Openverse, anahtar gerektirmez)."""
import requests

UA = {"User-Agent": "DuydunMuBot/1.0"}


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
