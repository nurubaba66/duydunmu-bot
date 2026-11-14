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


def carousel_html(d: dict, photo: bytes | None = None) -> list[str]:
    head = f"<!doctype html><html lang=tr><head><meta charset=utf-8>{FONT}{BASE}</head><body>"
    hl = d.get("headline", "")
    if photo:
        b64 = base64.b64encode(photo).decode()
        s1 = head + f"""<div class=c style="background:{Y}">
 <div style="position:relative;height:760px;overflow:hidden">
  <img src="data:image/jpeg;base64,{b64}" style="width:1080px;height:760px;object-fit:cover;display:block">
  <div class=bub style="position:absolute;top:48px;left:56px;font-size:48px">Duydun mu?</div>
  <div style="position:absolute;top:60px;right:56px;background:rgba(17,17,17,.75);color:#fff;font-size:26px;font-weight:800;padding:8px 16px;border-radius:10px">1/3</div>
  <div style="position:absolute;bottom:18px;right:24px;background:rgba(17,17,17,.72);color:#fff;font-size:19px;padding:6px 14px;border-radius:8px">Temsili fotoğraf</div>
 </div>
 <div style="flex:1;padding:44px 64px 52px;display:flex;flex-direction:column;gap:18px">
  <div style="font-size:28px;font-weight:800;letter-spacing:3px">{e(d.get('category'))}</div>
  <div class=h style="font-size:{fit(hl,92,76,36)}px">{e(hl)}</div>
  <div style="margin-top:auto;display:flex;justify-content:space-between;align-items:center">
   <div style="font-size:34px;font-weight:500">{e(d.get('subline'))}</div>
   <div style="background:{K};color:#fff;font-size:32px;font-weight:800;padding:20px 34px;border-radius:48px;white-space:nowrap">Kaydır →</div></div>
 </div>
</div></body></html>"""
    else:
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


# ---------------------------------------------------------------- haritalı şablonlar
from . import maps  # noqa: E402

LEVEL_COLOR = {"yellow": "#FFD43B", "orange": "#FF8A1F", "red": "#E5262B"}


def quake_html(q: dict, stamp: str) -> str:
    col = {q["plate"]: "#E5262B"} if q.get("plate") else {}
    depth = f"{float(q['depth']):.1f} km" if q.get("depth") not in (None, "") else "-"
    return f"""<!doctype html><html lang=tr><head><meta charset=utf-8>{FONT}{BASE}</head><body>
<div class=c style="background:{Y}">
 <div style="background:{K};color:{Y};padding:52px 64px 40px;display:flex;flex-direction:column;gap:24px">
  <div style="display:flex;justify-content:space-between;align-items:center">
   <div class=bub style="background:{Y};color:{K};font-size:44px">Duydun mu?</div><div style="font-size:26px;color:#e5e5e5">{config.HANDLE}</div></div>
  <div style="display:flex;align-items:center;gap:22px"><div style="width:32px;height:32px;border-radius:16px;background:#E5262B"></div>
   <div style="font-size:104px;font-weight:800;letter-spacing:-2px;line-height:1">DEPREM</div></div>
 </div>
 <div style="height:24px;background:repeating-linear-gradient(-45deg,{K} 0 24px,{Y} 24px 48px)"></div>
 <div style="flex:1;padding:44px 64px 56px;display:flex;flex-direction:column;gap:26px">
  <div class=h style="font-size:84px">{e(q['location'])}</div>
  <div style="display:flex;gap:22px">
   <div style="background:{K};color:{Y};border-radius:24px;padding:18px 30px"><div style="font-size:24px;color:#ddd">Büyüklük</div><div style="font-size:84px;font-weight:800;line-height:1">{q['mag']:.1f}</div></div>
   <div style="background:#fff;border-radius:24px;padding:18px 30px"><div style="font-size:24px">Derinlik</div><div style="font-size:52px;font-weight:800;line-height:1.2">{e(depth)}</div></div>
   <div style="background:#fff;border-radius:24px;padding:18px 30px"><div style="font-size:24px">Saat</div><div style="font-size:52px;font-weight:800;line-height:1.2">{q['time_local']}</div></div>
  </div>
  <div style="flex:1;display:flex;align-items:center;justify-content:center">{maps.svg(col, 950, 330, base="#F5E7A8")}</div>
  <div style="display:flex;justify-content:space-between;border-top:4px solid {K};padding-top:22px">
   <div style="font-size:30px;font-weight:800">{e(stamp)}</div><div style="font-size:28px">Kaynak: AFAD</div></div>
 </div>
</div>{maps.FIT_JS}</body></html>"""


def mgm_pages(today: dict, tomorrow: dict, d_today: str, d_tomorrow: str) -> list[str]:
    from . import mgm
    head = f"<!doctype html><html lang=tr><head><meta charset=utf-8>{FONT}{BASE}</head><body>"

    def cols(s):
        return {p: LEVEL_COLOR[lvl] for p, lvl in s["plates"].items()}

    worst = mgm.max_level(today) or mgm.max_level(tomorrow) or "yellow"
    badge = mgm.LEVEL_TR[worst] + " KOD"
    n_today, n_tom = len(today["plates"]), len(tomorrow["plates"])
    prio = ["wind", "thunderstorm", "rain", "snow", "avalanche", "cold", "hot", "ice", "fog", "dust", "snowmelt", "agricultural"]
    ev = sorted(today["events"] | tomorrow["events"], key=lambda x: prio.index(x) if x in prio else 99)
    ev_txt = " ve ".join(mgm.EVENT_TR.get(x, x) for x in ev[:2]) or "olumsuz hava"
    rows = []
    if n_today:
        rows.append(f'<div style="display:flex;align-items:center;gap:24px"><div style="width:250px;font-weight:800;font-size:34px">BUGÜN<br><span style="font-size:26px;font-weight:500;color:#ccc">{d_today} · {n_today} il</span></div>{maps.svg(cols(today), 640, 280)}</div>')
    if n_tom:
        rows.append(f'<div style="display:flex;align-items:center;gap:24px"><div style="width:250px;font-weight:800;font-size:34px">YARIN<br><span style="font-size:26px;font-weight:500;color:#ccc">{d_tomorrow} · {n_tom} il</span></div>{maps.svg(cols(tomorrow), 640, 280)}</div>')
    total = len(set(today["plates"]) | set(tomorrow["plates"]))
    n = 2 + (1 if n_today else 0) + (1 if n_tom else 0)
    cover = head + f"""<div class=c style="background:{K};color:#fff;padding:64px;gap:30px">
 <div style="display:flex;justify-content:space-between;align-items:center"><div class=bub style="background:{Y};color:{K};font-size:52px">Duydun mu?</div><div style="font-size:28px;font-weight:800">1/{n}</div></div>
 <div style="display:flex"><div style="background:{LEVEL_COLOR[worst]};color:{K};font-weight:800;font-size:30px;padding:8px 20px;border-radius:10px">{badge}</div></div>
 <div class=h style="font-size:96px;color:{Y}">{total} ilde {e(ev_txt)} uyarısı</div>
 <div style="flex:1;display:flex;flex-direction:column;justify-content:center;gap:26px">{''.join(rows)}</div>
 <div style="display:flex;justify-content:space-between;align-items:center"><div style="font-size:22px;color:#bbb">Kaynak: Meteoroloji Genel Müdürlüğü · Harita temsilidir</div>
  <div style="background:{Y};color:{K};font-size:32px;font-weight:800;padding:18px 32px;border-radius:44px">Kaydır →</div></div>
</div>{maps.FIT_JS}</body></html>"""
    pages = [cover]

    def day(i, title, s):
        lines = []
        for lvl in mgm.LEVELS:
            ps = [p for p, l in s["plates"].items() if l == lvl]
            if ps:
                lines.append(f"{mgm.LEVEL_TR[lvl].title()} kod: " + ", ".join(mgm.names(ps)) + ".")
        spans = sorted({(a["begin"], a["end"]) for a in s["alerts"]})[:2]
        for b, en in spans:
            if mgm.fmt_time(b):
                lines.append(f"Uyarı süresi: {mgm.fmt_time(b)} – {mgm.fmt_time(en)}")
        txt = next(iter(s["texts"].values()), "")
        if txt:
            lines.append(txt.split(". ")[0].rstrip(".") + ".")
        li = "".join(f'<div style="display:flex;gap:22px;align-items:flex-start"><div style="flex:none;width:18px;height:18px;margin-top:14px;border-radius:9px;background:{K}"></div><div style="font-size:{34 if len(t) < 160 else 30}px;line-height:1.35">{e(t)}</div></div>' for t in lines)
        return head + f"""<div class=c style="background:{CREAM};padding:64px;gap:28px">
 <div style="display:flex;justify-content:space-between;align-items:center"><div class=bub style="font-size:36px">Duydun mu?</div><div style="font-size:28px;font-weight:800">{i}/{n}</div></div>
 <div class=h style="font-size:72px">{title}</div>
 <div style="display:flex;justify-content:center">{maps.svg(cols(s), 950, 330, base="#D6D1C2")}</div>
 <div style="display:flex;flex-direction:column;gap:20px;flex:1;justify-content:center">{li}</div>
 <div style="font-size:24px;color:#57534E;border-top:3px solid {K};padding-top:20px">Kaynak: Meteoroloji Genel Müdürlüğü (MeteoUyarı)</div>
</div>{maps.FIT_JS}</body></html>"""
    i = 2
    if n_today:
        pages.append(day(i, f"BUGÜN · {d_today}", today)); i += 1
    if n_tom:
        pages.append(day(i, f"YARIN · {d_tomorrow}", tomorrow)); i += 1
    last = carousel_html({"question": "Senin olduğun yerde hava nasıl? Yorumlara yaz.", "points": [],
                          "category": "", "headline": "", "subline": "", "source": "MGM"})[2]
    pages.append(last.replace(">3/3<", f">{n}/{n}<"))
    return pages
