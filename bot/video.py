"""Duydun mu? video kurgusu: kurumsal başlık katmanı + animasyonlu "Beğen · Yorum · Paylaş · Takip et" kapanışı.

Kullanım: python -m bot.video giris.mp4 cikis.mp4 "Başlık metni" ["Görüntü: Sosyal medya"]
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright

from . import config

W, H, FPS = 1080, 1920, 30
Y, K = "#FFD43B", "#111111"
FONT_DIR = os.environ.get("FONT_DIR", "")  # yerel font klasörü (yoksa Google Fonts)


def _font_css() -> str:
    if FONT_DIR:
        d = FONT_DIR.rstrip("/") + "/bricolage-grotesque-"
        return "".join(
            f"@font-face{{font-family:B;font-weight:{w};src:url(file://{d}{sub}-{w}-normal.woff2);"
            f"unicode-range:{rng}}}"
            for w in (500, 800) for sub, rng in (("latin", "U+0000-00FF,U+2000-206F"), ("latin-ext", "U+0100-024F")))
    return "@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,800&display=swap');"


ICONS = {
    "Beğen": '<path d="M12 21s-7.5-4.6-9.5-9.2C1 8.4 3.3 5 6.8 5c2 0 3.6 1.1 5.2 3 1.6-1.9 3.2-3 5.2-3 3.5 0 5.8 3.4 4.3 6.8C19.5 16.4 12 21 12 21z"/>',
    "Yorum yap": '<path d="M4 5h16v11H9l-5 4z"/>',
    "Paylaş": '<path d="M21 3 3 10l7 3 3 7z"/><path d="M10 13 21 3"/>',
    "Takip et": '<circle cx="9" cy="8" r="4"/><path d="M2 21c0-4 3-6.5 7-6.5s7 2.5 7 6.5"/><path d="M19 8v6M16 11h6"/>',
}


def _html(body: str, anim_css: str) -> str:
    return f"""<!doctype html><html><head><meta charset=utf-8><style>{_font_css()}
*{{box-sizing:border-box}}body{{margin:0;background:transparent;font-family:B,'Bricolage Grotesque',sans-serif}}
{anim_css}</style></head><body>{body}</body></html>"""


def _render_frames(page, html: str, seconds: float, out: Path, transparent: bool):
    out.mkdir(parents=True, exist_ok=True)
    f = out / "page.html"
    f.write_text(html, encoding="utf-8")
    page.goto(f.as_uri())
    page.evaluate("document.fonts.ready")
    page.wait_for_timeout(300)
    page.evaluate("document.getAnimations().forEach(a=>a.pause())")
    n = int(seconds * FPS)
    for i in range(n):
        t = i * 1000 / FPS
        page.evaluate(f"document.getAnimations().forEach(a=>a.currentTime={t})")
        page.screenshot(path=str(out / f"f{i:04d}.png"), omit_background=transparent)


def overlay_html(title: str, credit: str) -> str:
    css = """
@keyframes pop{0%{transform:scale(.4);opacity:0}70%{transform:scale(1.08);opacity:1}100%{transform:scale(1)}}
@keyframes slide{0%{transform:translateY(-40px);opacity:0}100%{transform:none;opacity:1}}
@keyframes bar{from{width:0}to{width:100%}}
.bub{animation:pop .5s cubic-bezier(.2,.9,.3,1.2) both}
.ttl{animation:slide .45s .2s ease-out both}
.cr{animation:slide .4s .5s ease-out both}"""
    body = f"""<div style="width:{W}px;height:{H}px;position:relative">
 <div style="position:absolute;top:150px;left:60px;right:60px;display:flex;flex-direction:column;gap:22px;align-items:flex-start">
  <div class=bub style="background:{K};color:{Y};font-weight:800;font-size:46px;padding:10px 30px;border-radius:44px 44px 44px 6px;transform-origin:left bottom">Duydun mu?</div>
  <div class=ttl style="background:{Y};color:{K};font-weight:800;font-size:64px;line-height:1.08;letter-spacing:-1.5px;padding:24px 32px;border-radius:24px;box-shadow:0 8px 30px rgba(0,0,0,.25)">{title}</div>
 </div>
 <div class=cr style="position:absolute;bottom:420px;right:40px;background:rgba(17,17,17,.7);color:#fff;font-weight:500;font-size:24px;padding:8px 16px;border-radius:10px">{credit}</div>
</div>"""
    return _html(body, css)


def outro_html() -> str:
    css = """
@keyframes pop{0%{transform:scale(.3);opacity:0}65%{transform:scale(1.12);opacity:1}100%{transform:scale(1)}}
@keyframes up{0%{transform:translateY(60px);opacity:0}100%{transform:none;opacity:1}}
@keyframes heart{0%,100%{transform:scale(1)}40%{transform:scale(1.35)}}
@keyframes fill{to{fill:#E5262B;stroke:#E5262B}}
@keyframes tap{0%{transform:scale(1)}50%{transform:scale(.92)}100%{transform:scale(1)}}
@keyframes followed{to{background:#111;color:#FFD43B}}
@keyframes cursor{0%{opacity:0;transform:translate(120px,140px)}30%{opacity:1}60%{transform:translate(0,0)}70%{transform:translate(0,0) scale(.85)}80%{transform:translate(0,0) scale(1)}100%{opacity:1;transform:translate(0,0)}}
.logo{animation:pop .55s cubic-bezier(.2,.9,.3,1.2) both}
.it{animation:up .45s ease-out both}
.it svg{fill:none;stroke:#111;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
.h1 path{animation:fill .2s 1.55s forwards}.h1 svg{animation:heart .5s 1.5s}
.btn{animation:up .45s 1.7s ease-out both, tap .25s 2.55s, followed .1s 2.6s forwards}
.cur{animation:cursor 1s 1.9s both}"""
    items = "".join(
        f"""<div class="it {'h1' if i == 0 else ''}" style="animation-delay:{0.55 + i * 0.18:.2f}s;display:flex;flex-direction:column;align-items:center;gap:16px">
<div style="width:150px;height:150px;border-radius:75px;background:#fff;display:flex;align-items:center;justify-content:center;box-shadow:0 10px 30px rgba(0,0,0,.12)">
<svg width="72" height="72" viewBox="0 0 24 24">{svg}</svg></div>
<div style="font-weight:800;font-size:34px;color:{K}">{name}</div></div>"""
        for i, (name, svg) in enumerate(ICONS.items()))
    body = f"""<div style="width:{W}px;height:{H}px;background:{Y};display:flex;flex-direction:column;align-items:center;justify-content:center;gap:90px;position:relative">
 <div class=logo style="background:{K};color:{Y};font-weight:800;font-size:120px;padding:26px 70px;border-radius:110px 110px 110px 14px;line-height:1.05">Duydun mu?</div>
 <div style="display:grid;grid-template-columns:repeat(4,200px);gap:20px;justify-items:center">{items}</div>
 <div style="position:relative">
  <div class=btn style="background:#fff;color:{K};font-weight:800;font-size:52px;padding:26px 64px;border-radius:60px;border:5px solid {K}">{config.HANDLE}</div>
  <svg class=cur width="70" height="70" viewBox="0 0 24 24" style="position:absolute;right:30px;bottom:-40px"><path d="M5 3l14 8-6 2 4 7-3 1-4-7-5 4z" fill="#fff" stroke="#111" stroke-width="1.5"/></svg>
 </div>
 <div class=it style="animation-delay:2.0s;font-weight:500;font-size:40px;color:{K}">Gündemi kaçırmamak için takip et</div>
</div>"""
    return _html(body, css)


def build(src: str, dst: str, title: str, credit: str = "Görüntü: Sosyal medya", outro_sec: float = 3.5):
    tmp = Path(tempfile.mkdtemp())
    try:
        with sync_playwright() as p:
            br = p.chromium.launch()
            pg = br.new_page(viewport={"width": W, "height": H})
            _render_frames(pg, overlay_html(title, credit), 1.0, tmp / "ov", transparent=True)
            _render_frames(pg, outro_html(), outro_sec, tmp / "out", transparent=False)
            br.close()
        last = sorted((tmp / "ov").glob("f*.png"))[-1]
        # Ana video + animasyonlu katman (ilk 1 sn animasyon, sonra sabit)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src,
                        "-framerate", str(FPS), "-i", str(tmp / "ov" / "f%04d.png"), "-loop", "1", "-i", str(last),
                        "-filter_complex",
                        f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},setsar=1[b];"
                        "[b][1:v]overlay=0:0:eof_action=pass[t];[t][2:v]overlay=0:0:enable='gte(t,1)':shortest=1[v]",
                        "-map", "[v]", "-map", "0:a?", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                        "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar", "44100", "-ac", "2", str(tmp / "main.mp4")], check=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", str(tmp / "out" / "f%04d.png"),
                        "-f", "lavfi", "-t", str(outro_sec), "-i", "anullsrc=r=44100:cl=stereo",
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-shortest", str(tmp / "outro.mp4")], check=True)
        has_audio = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index",
                                    "-of", "csv=p=0", str(tmp / "main.mp4")], capture_output=True, text=True).stdout.strip()
        if not has_audio:
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp / "main.mp4"), "-f", "lavfi", "-i",
                            "anullsrc=r=44100:cl=stereo", "-c:v", "copy", "-c:a", "aac", "-shortest",
                            str(tmp / "main2.mp4")], check=True)
            shutil.move(tmp / "main2.mp4", tmp / "main.mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp / "main.mp4"), "-i", str(tmp / "outro.mp4"),
                        "-filter_complex", "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]", "-map", "[v]", "-map", "[a]",
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-movflags", "+faststart", dst], check=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return dst


if __name__ == "__main__":
    build(*sys.argv[1:])
