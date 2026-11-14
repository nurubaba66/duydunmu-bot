"""Duydun mu? kurumsal kimliğine göre kartları HTML'den 1080x1350 JPG'ye çevirir."""
import base64
import html
from pathlib import Path

from playwright.sync_api import sync_playwright

from . import config

Y, K, CREAM = "#FFD43B", "#111111", "#FFFBEA"
FONT = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,800&display=swap">'
BASE = f"""<style>body{{margin:0}}*{{box-sizing:border-box}}
.c{{width:1080px;height:1350px;font-family:'Bricolage Grotesque',sans-serif;color:{K};display:flex;flex-direction:column;overflow:hidden}}
.bub{{background:{K};color:{Y};font-weight:800;padding:12px 30px;border-radius:44px 44px 44px 6px;line-height:1.1;display:inline-block}}
.cat{{font-size:30px;font-weight:800;letter-spacing:3px;border-bottom:4px solid {K};align-self:flex-start;padding-bottom:6px}}
.h{{font-weight:800;letter-spacing:-2px;line-height:1.02}}
</style>"""


def e(s) -> str:
    return html.escape(str(s or ""))


def fit(text: str, big: int, small: int, limit: int) -> int:
    return big if len(text or "") <= limit else small


def card_html(d: dict, photo: bytes | None = None, credit: str = "") -> str:
    hl = d.get("headline", "")
    if photo:
        b64 = base64.b64encode(photo).decode()
        return f"""<!doctype html><html lang=tr><head><meta charset=utf-8>{FONT}{BASE}</head><body>
<div class=c style="background:{Y}">
 <div style="position:relative;height:760px;overflow:hidden">
  <img src="data:image/jpeg;base64,{b64}" style="width:1080px;height:760px;object-fit:cover;display:block">
  <div class=bub style="position:absolute;top:48px;left:56px;font-size:44px">Duydun mu?</div>
  <div style="position:absolute;bottom:18px;right:24px;background:rgba(17,17,17,.72);color:#fff;font-size:19px;padding:6px 14px;border-radius:8px">Temsili fotoğraf</div>
 </div>
 <div style="flex:1;padding:44px 64px 52px;display:flex;flex-direction:column;gap:20px">
  <div style="font-size:28px;font-weight:800;letter-spacing:3px">{e(d.get('category'))}</div>
  <div class=h style="font-size:{fit(hl,84,68,42)}px">{e(hl)}</div>
  <div style="font-size:32px;font-weight:500;line-height:1.35">{e(d.get('summary'))}</div>
  <div style="margin-top:auto;display:flex;justify-content:space-between;align-items:center;border-top:4px solid {K};padding-top:18px">
   <div style="font-size:34px;font-weight:800">{e(d.get('question') or 'Sizce?')}</div>
   <div style="font-size:23px;font-weight:500">Kaynak: {e(d.get('source'))}</div>
  </div>
 </div>
</div></body></html>"""
    return f"""<!doctype html><html lang=tr><head><meta charset=utf-8>{FONT}{BASE}</head><body>
<div class=c style="background:{Y};padding:72px;gap:44px">
 <div style="display:flex;justify-content:space-between;align-items:center">
  <div class=bub style="font-size:58px">Duydun mu?</div><div style="font-size:28px;font-weight:500">{config.HANDLE}</div></div>
 <div class=cat>{e(d.get('category'))}</div>
 <div class=h style="font-size:{fit(hl,112,92,40)}px;flex:1;display:flex;align-items:center">{e(hl)}</div>
 <div style="font-size:38px;font-weight:500;line-height:1.4">{e(d.get('summary'))}</div>
 <div style="background:{K};color:#fff;border-radius:28px;padding:32px 40px;display:flex;justify-content:space-between;align-items:center;gap:24px">
  <div style="font-size:40px;font-weight:800">{e(d.get('question') or 'Sen ne düşünüyorsun?')}</div>
  <div style="font-size:26px;color:{Y};white-space:nowrap">Kaynak: {e(d.get('source'))}</div></div>
</div></body></html>"""


def breaking_html(d: dict, stamp: str) -> str:
    hl = d.get("headline", "")
    return f"""<!doctype html><html lang=tr><head><meta charset=utf-8>{FONT}{BASE}</head><body>
<div class=c style="background:{Y}">
 <div style="background:{K};color:{Y};padding:56px 72px 48px;display:flex;flex-direction:column;gap:28px">
  <div style="display:flex;justify-content:space-between;align-items:center">
   <div class=bub style="background:{Y};color:{K};font-size:44px">Duydun mu?</div><div style="font-size:26px;color:#e5e5e5">{config.HANDLE}</div></div>
  <div style="display:flex;align-items:center;gap:24px"><div style="width:34px;height:34px;border-radius:17px;background:#E5262B"></div>
   <div style="font-size:120px;font-weight:800;letter-spacing:-2px;line-height:1">SON DAKİKA</div></div>
 </div>
 <div style="height:24px;background:repeating-linear-gradient(-45deg,{K} 0 24px,{Y} 24px 48px)"></div>
 <div style="flex:1;padding:56px 72px 72px;display:flex;flex-direction:column;gap:40px">
  <div class=h style="font-size:{fit(hl,96,80,60)}px;flex:1;display:flex;align-items:center">{e(hl)}</div>
  <div style="font-size:36px;font-weight:500;line-height:1.4">{e(d.get('summary'))}</div>
  <div style="display:flex;justify-content:space-between;border-top:4px solid {K};padding-top:28px">
   <div style="font-size:30px;font-weight:800">{e(stamp)}</div><div style="font-size:28px">Kaynak: {e(d.get('source'))}</div></div>
 </div>
</div></body></html>"""


def carousel_html(d: dict) -> list[str]:
    head = f"<!doctype html><html lang=tr><head><meta charset=utf-8>{FONT}{BASE}</head><body>"
    hl = d.get("headline", "")
    s1 = head + f"""<div class=c style="background:{Y};padding:72px;gap:44px">
 <div style="display:flex;justify-content:space-between;align-items:center"><div class=bub style="font-size:58px">Duydun mu?</div><div style="font-size:28px;font-weight:800">1/3</div></div>
 <div class=cat>{e(d.get('category'))}</div>
 <div class=h style="font-size:{fit(hl,132,108,34)}px;letter-spacing:-3px;line-height:1;flex:1;display:flex;align-items:center">{e(hl)}</div>
 <div style="display:flex;justify-content:space-between;align-items:center"><div style="font-size:34px;font-weight:500">{e(d.get('subline'))}</div>
  <div style="background:{K};color:#fff;font-size:34px;font-weight:800;padding:22px 36px;border-radius:48px">Kaydır →</div></div>
</div></body></html>"""
    pts = "".join(
        f"""<div style="display:flex;gap:32px;align-items:flex-start"><div style="flex:none;width:76px;height:76px;border-radius:38px;background:{Y};font-size:40px;font-weight:800;display:flex;align-items:center;justify-content:center">{i+1}</div>
<div style="font-size:42px;font-weight:500;line-height:1.35">{e(p)}</div></div>""" for i, p in enumerate((d.get("points") or [])[:3]))
    s2 = head + f"""<div class=c style="background:{CREAM};padding:72px;gap:48px">
 <div style="display:flex;justify-content:space-between;align-items:center"><div class=bub style="background:{Y};color:{K};font-size:36px">Duydun mu?</div><div style="font-size:28px;font-weight:800">2/3</div></div>
 <div class=h style="font-size:72px;letter-spacing:-1px">Kısaca neler oluyor?</div>
 <div style="flex:1;display:flex;flex-direction:column;justify-content:center;gap:44px">{pts}</div>
 <div style="font-size:26px;color:#57534E;border-top:3px solid {K};padding-top:24px">Kaynak: {e(d.get('source'))}</div>
</div></body></html>"""
    s3 = head + f"""<div class=c style="background:{K};color:#fff;padding:72px;gap:48px">
 <div style="display:flex;justify-content:space-between;align-items:center"><div class=bub style="background:{Y};color:{K};font-size:36px">Duydun mu?</div><div style="font-size:28px;font-weight:800">3/3</div></div>
 <div style="flex:1;display:flex;flex-direction:column;justify-content:center;gap:40px">
  <div class=h style="font-size:132px;letter-spacing:-3px;line-height:1;color:{Y}">Sen ne düşünüyorsun?</div>
  <div style="font-size:48px;font-weight:500;line-height:1.3">{e(d.get('question'))}</div></div>
 <div style="border-top:3px solid #3F3F46;padding-top:36px;display:flex;flex-direction:column;gap:20px">
  <div style="font-size:38px;font-weight:800">Yorumlara yaz, arkadaşını etiketle.</div>
  <div style="font-size:32px;color:#D4D4D8">Gündemi kaçırmamak için takip et: <b style="color:{Y}">{config.HANDLE}</b></div></div>
</div></body></html>"""
    return [s1, s2, s3]


def to_jpgs(pages: list[str], out_dir: Path, stem: str) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    with sync_playwright() as p:
        br = p.chromium.launch()
        pg = br.new_page(viewport={"width": 1080, "height": 1350})
        for i, h in enumerate(pages):
            pg.set_content(h, wait_until="networkidle")
            pg.evaluate("document.fonts.ready")
            path = out_dir / f"{stem}_{i+1}.jpg"
            pg.screenshot(path=str(path), type="jpeg", quality=92, clip={"x": 0, "y": 0, "width": 1080, "height": 1350})
            paths.append(path)
        br.close()
    return paths
