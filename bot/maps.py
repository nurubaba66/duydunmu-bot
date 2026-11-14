"""Türkiye il haritası (açık lisanslı il sınırları, MIT: data_turkiye.LICENSE)."""
import json
from pathlib import Path

_DATA = json.loads((Path(__file__).parent / "data_turkiye.json").read_text(encoding="utf-8"))
_TR = str.maketrans("çğıöşüâîûÇĞİÖŞÜ", "cgiosuaiuCGIOSU")


def norm(s: str) -> str:
    return (s or "").strip().lower().replace("i̇", "i").translate(_TR).replace(" ", "")


BY_PLATE = {c["plate"]: c for c in _DATA}
BY_NAME = {norm(c["name"]): c for c in _DATA}


def province(name: str) -> dict | None:
    return BY_NAME.get(norm(name))


def svg(colors: dict[int, str], w: int, h: int, base: str = "#3A3A3A", stroke: str = "#111") -> str:
    """colors: plaka -> renk. Viewbox sayfada FIT_JS ile otomatik ayarlanır."""
    paths = "".join(f'<path d="{c["path"]}" fill="{colors.get(c["plate"], base)}" stroke="{stroke}" stroke-width="1.2"/>'
                    for c in _DATA)
    return f'<svg class="map" width="{w}" height="{h}">{paths}</svg>'


FIT_JS = ("<script>document.querySelectorAll('svg.map').forEach(s=>{const b=s.getBBox();"
          "s.setAttribute('viewBox',[b.x-4,b.y-4,b.width+8,b.height+8].join(' '))})</script>")
