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
    """Instagram medyayı herkese açık bir adresten çeker; dosyayı geçici olarak barındırır (birkaç servis denenir)."""
    mime = "video/mp4" if path.suffix == ".mp4" else "image/jpeg"
    errors = []
    # 0) catbox.moe (kalıcı, doğrudan dosya adresi)
    try:
        with open(path, "rb") as f:
            r = requests.post("https://catbox.moe/user/api.php", data={"reqtype": "fileupload"},
                              files={"fileToUpload": (path.name, f, mime)}, timeout=120,
                              headers={"User-Agent": "DuydunMuBot/1.0"})
        if r.text.strip().startswith("https://"):
            return r.text.strip()
        errors.append(f"catbox: {r.status_code} {r.text[:80]}")
    except Exception as e:
        errors.append(f"catbox: {e}")
    # 1) tmpfiles.org (60 dk)
    try:
        with open(path, "rb") as f:
            r = requests.post("https://tmpfiles.org/api/v1/upload", files={"file": (path.name, f, mime)}, timeout=120)
        url = r.json()["data"]["url"].replace("tmpfiles.org/", "tmpfiles.org/dl/", 1).replace("http://", "https://")
        return url
    except Exception as e:
        errors.append(f"tmpfiles: {e}")
    # 2) litterbox.catbox.moe (72 saat)
    try:
        with open(path, "rb") as f:
            r = requests.post("https://litterbox.catbox.moe/resources/internals/api.php",
                              data={"reqtype": "fileupload", "time": "72h"},
                              files={"fileToUpload": (path.name, f, mime)}, timeout=120)
        if r.text.strip().startswith("https://"):
            return r.text.strip()
        errors.append(f"litterbox: {r.status_code}")
    except Exception as e:
        errors.append(f"litterbox: {e}")
    # 3) 0x0.st
    try:
        with open(path, "rb") as f:
            r = requests.post("https://0x0.st", files={"file": (path.name, f, mime)},
                              headers={"User-Agent": "DuydunMuBot/1.0"}, timeout=120)
        if r.text.strip().startswith("http"):
            return r.text.strip()
        errors.append(f"0x0: {r.status_code}")
    except Exception as e:
        errors.append(f"0x0: {e}")
    raise RuntimeError("Medya yüklenemedi: " + " | ".join(errors))


def _wait_ready(container_id: str, tries: int = 30):
    st = {}
    for _ in range(tries):
        st = _check(requests.get(_api(container_id), params={"fields": "status_code,status", "access_token": config.IG_ACCESS_TOKEN}, timeout=30))
        code = st.get("status_code")
        if code in ("FINISHED", "PUBLISHED"):
            return
        if code in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"Instagram medyayı işleyemedi: {st}")
        time.sleep(5)
    raise RuntimeError(f"Instagram işlemi zamanında bitmedi: {st}")


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


def publish_reel(path: Path, caption: str) -> str:
    """Videoyu üçüncü taraf sunucu kullanmadan, doğrudan Instagram'a yükler (resumable upload)."""
    if config.DRY_RUN:
        print("[DENEME] Reels paylaşılmadı:", path.name)
        return "dry-run"
    uid, tok = ig_user_id(), config.IG_ACCESS_TOKEN
    c = _check(requests.post(_api(f"{uid}/media"), data={
        "media_type": "REELS", "upload_type": "resumable", "caption": caption,
        "share_to_feed": "true", "access_token": tok}, timeout=60))
    upload_uri = c.get("uri") or f"https://rupload.facebook.com/ig-api-upload/{config.GRAPH_VERSION}/{c['id']}"
    data = path.read_bytes()
    r = requests.post(upload_uri, data=data, timeout=600, headers={
        "Authorization": f"OAuth {tok}", "offset": "0", "file_size": str(len(data))})
    print("Video yüklendi:", r.status_code, r.text[:200])
    if not r.ok:
        raise RuntimeError(f"Video yüklenemedi: {r.text[:300]}")
    _wait_ready(c["id"], tries=90)
    res = _check(requests.post(_api(f"{uid}/media_publish"), data={"creation_id": c["id"], "access_token": tok}, timeout=60))
    print("Reels paylaşıldı:", res.get("id"))
    return res.get("id", "")
