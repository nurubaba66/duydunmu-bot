"""Görsel yükleme yolunu paylaşmadan test eder: konteyner oluşturur, durumunu yazar, yayınlamaz."""
from pathlib import Path

import requests

from . import config, instagram, render

d = {"headline": "Deneme kartı", "summary": "Bu kart yayınlanmayacak.", "question": "Sizce?", "source": "Test", "category": "TEST"}
p = render.to_jpgs([render.card_html(d)], Path("out"), "probe")[0]
url = instagram.upload_public(p)
print("Geçici adres:", url)
c = instagram._check(requests.post(instagram._api(f"{instagram.ig_user_id()}/media"),
                                   data={"image_url": url, "access_token": config.IG_ACCESS_TOKEN}, timeout=60))
instagram._wait_ready(c["id"])
print("GÖRSEL YOLU ÇALIŞIYOR (yayınlanmadı)")
