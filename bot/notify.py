"""Onay gereken içerikler için GitHub issue açar; GitHub bunu sahibine e-posta olarak gönderir.
E-postaya "paylaş" diye cevap vermek issue'ya yorum yazar, approve.py bunu yakalayıp paylaşır."""
import json
from pathlib import Path

import requests

from . import config, instagram

API = "https://api.github.com"


def _h():
    return {"Authorization": f"Bearer {config.GITHUB_TOKEN}", "Accept": "application/vnd.github+json"}


def open_issue(title: str, body: str, labels=("onay",)) -> int | None:
    if not config.GITHUB_TOKEN:
        print("[bildirim yok] GITHUB_TOKEN eksik:", title)
        return None
    r = requests.post(f"{API}/repos/{config.GITHUB_REPO}/issues", headers=_h(),
                      json={"title": title, "body": body, "labels": list(labels), "assignees": [config.OWNER_LOGIN]},
                      timeout=30)
    if not r.ok:
        print("[issue açılamadı]", r.status_code, r.text[:200])
        return None
    return r.json()["number"]


def comment(num: int, body: str, close: bool = False):
    requests.post(f"{API}/repos/{config.GITHUB_REPO}/issues/{num}/comments", headers=_h(), json={"body": body}, timeout=30)
    if close:
        requests.patch(f"{API}/repos/{config.GITHUB_REPO}/issues/{num}", headers=_h(), json={"state": "closed"}, timeout=30)


def ask_approval(folder: Path, post: dict, reason: str) -> int | None:
    """Hazır içeriği pending klasörüne koyar, önizlemeli issue açar."""
    previews = []
    for f in post["files"][:4]:
        p = folder / f
        if p.suffix == ".jpg":
            try:
                previews.append(f"![önizleme]({instagram.upload_public(p)})")
            except Exception as e:
                print("[önizleme yüklenemedi]", e)
    body = (f"**Reis, şu habere bir baksan iyi olur.**\n\nNeden soruyorum: {reason}\n\n" + "\n".join(previews) +
            f"\n\n**Açıklama:**\n\n> " + post["caption"].replace("\n", "\n> ") +
            "\n\n---\nBu e-postaya **paylaş** yazarak cevap ver → hemen paylaşılır.\n"
            "**geç** yazarsan paylaşılmaz.")
    num = open_issue(f"🟡 Onay: {post['title'][:80]}", body)
    if num:
        (folder / "issue.json").write_text(json.dumps({"issue": num}), encoding="utf-8")
    return num
