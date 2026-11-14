"""Instagram Graph API ile tek görsel ve karusel paylaşımı."""
import time
from pathlib import Path

import requests

from . import config


def _api(path: str) -> str:
    return f"{config.GRAPH_HOST}/{config.GRAPH_VERSION}/{path}"


def _check(r: requests.Response) -> dict:
    data = r.json()
    if "error" in data:
        raise RuntimeError(f"Instagram API hatası: {data['error'].get('message')}")
    return data


def ig_user_id() -> str:
    if config.IG_USER_ID:
        return config.IG_USER_ID
    tok = {"access_token": config.IG_ACCESS_TOKEN}
    # Instagram Login token'ı
    r = requests.get(_api("me"), params={**tok, "fields": "user_id,username"}, timeout=30).json()
    if r.get("user_id"):
        return str(r["user_id"])
    # Business/system-user token'ı: bağlı Instagram hesaplarını ara
    r = requests.get(_api("me/accounts"), params={**tok, "fields": "instagram_business_account"}, timeout=30).json()
    for acc in r.get("data", []):
        if acc.get("instagram_business_account"):
            return acc["instagram_business_account"]["id"]
    raise RuntimeError("Instagram hesap ID'si bulunamadı. IG_USER_ID secret'ını ekleyin.")


def upload_public(path: Path) -> str:
    """Instagram görseli herkese açık bir adresten çeker; geçici olarak (72 saat) barındırır."""
    with open(path, "rb") as f:
        r = requests.post("https://litterbox.catbox.moe/resources/internals/api.php",
                          data={"reqtype": "fileupload", "time": "72h"},
                          files={"fileToUpload": (path.name, f, "image/jpeg")}, timeout=60)
    url = r.text.strip()
    if not url.startswith("https://"):
        raise RuntimeError(f"Görsel yüklenemedi: {url[:200]}")
    return url


def _wait_ready(container_id: str):
    for _ in range(30):
        st = _check(requests.get(_api(container_id), params={"fields": "status_code", "access_token": config.IG_ACCESS_TOKEN}, timeout=30))
        if st.get("status_code") in ("FINISHED", None):
            return
        if st.get("status_code") == "ERROR":
            raise RuntimeError("Instagram görseli işleyemedi")
        time.sleep(4)


def publish(paths: list[Path], caption: str) -> str:
    if config.DRY_RUN:
        print("[DENEME] Paylaşılmadı:", [p.name for p in paths], "\n", caption)
        return "dry-run"
    uid, tok = ig_user_id(), config.IG_ACCESS_TOKEN
    urls = [upload_public(p) for p in paths]
    if len(urls) == 1:
        c = _check(requests.post(_api(f"{uid}/media"), data={"image_url": urls[0], "caption": caption, "access_token": tok}, timeout=60))
    else:
        kids = []
        for u in urls:
            k = _check(requests.post(_api(f"{uid}/media"), data={"image_url": u, "is_carousel_item": "true", "access_token": tok}, timeout=60))
            _wait_ready(k["id"])
            kids.append(k["id"])
        c = _check(requests.post(_api(f"{uid}/media"), data={"media_type": "CAROUSEL", "children": ",".join(kids), "caption": caption, "access_token": tok}, timeout=60))
    _wait_ready(c["id"])
    res = _check(requests.post(_api(f"{uid}/media_publish"), data={"creation_id": c["id"], "access_token": tok}, timeout=60))
    print("Paylaşıldı:", res.get("id"))
    return res.get("id", "")
