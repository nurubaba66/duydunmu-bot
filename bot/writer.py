"""Claude ile haber seçimi ve kart metni yazımı."""
import json
import re

import anthropic

from . import config

STYLE = """Sen "Duydun mu?" adlı anonim Türkçe haber Instagram sayfasının editörüsün.
Kurallar:
- Sadece verilen haber metnindeki bilgileri kullan. Yeni bilgi, rakam, isim, tahmin EKLEME. Emin değilsen yazma.
- Metni kendi cümlelerinle yeniden yaz; kaynağın cümlelerini kopyalama.
- Kısa, net, herkesin anlayacağı Türkçe. Clickbait yok, yalan vaat yok, hakaret yok, taraf tutma yok.
- Suç haberlerinde şüphelileri suçlu gibi yazma; "iddia", "gözaltı", "soruşturma" ifadelerini koru.
- Her paylaşım yorum çekecek tarafsız bir soruyla biter ("Sizce?", "Sen ne düşünüyorsun?" gibi).
- Ölüm, şiddet, intihar, çocuk istismarı haberlerini seçme.
"""


def _client():
    return anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)


def _text(msg) -> str:
    return "".join(getattr(b, "text", "") for b in msg.content if getattr(b, "type", "") == "text")


def _json(text: str, kind: str = "{"):
    pat = r"\[.*\]" if kind == "[" else r"\{.*\}"
    m = re.search(pat, text, re.S)
    try:
        return json.loads(m.group(0)) if m else None
    except json.JSONDecodeError:
        return None


def score_items(items: list[dict]) -> list[dict]:
    """Her habere 0-10 puan verir: Türkiye'yi ilgilendirme, yorum çekme, cebe dokunma."""
    if not items:
        return []
    listing = "\n".join(
        f'{i}. [{it["source"]}, {it["age_min"]} dk önce] {it["title"]} — {it["summary"][:240]}'
        for i, it in enumerate(items[:40])
    )
    msg = _client().messages.create(
        model=config.CLAUDE_MODEL, max_tokens=8000, system=STYLE,
        messages=[{"role": "user", "content": (
            "Aşağıdaki haberleri Instagram'da en çok etkileşim (yorum, kaydetme, paylaşım) alacak şekilde puanla.\n"
            "Kriterler: Türkiye'deki geniş kitleyi doğrudan ilgilendirmesi (maaş, vergi, fiyat, ulaşım, eğitim, sağlık, hava, güvenlik), "
            "tartışma yaratma potansiyeli, yenilik. Hassas/şiddet haberleri ve tek kişilik magazin 0 alsın.\n"
            "Ayrıca gerçekten acil ve önemli bir gelişmeyse breaking=true yap (deprem, büyük karar, resmi açıklama gibi).\n"
            'Sadece JSON dön: [{"i":0,"score":7,"breaking":false,"category":"EKONOMİ"}, ...]\n\n' + listing)}],
    )
    raw = _text(msg)
    scores = _json(raw, "[") or []
    if not scores:
        print("[puanlama okunamadı]", msg.stop_reason, raw[:500])
    for s in scores:
        idx = s.get("i")
        if isinstance(idx, int) and 0 <= idx < len(items):
            items[idx]["score"] = s.get("score", 0)
            items[idx]["breaking"] = bool(s.get("breaking"))
            items[idx]["category"] = (s.get("category") or "GÜNDEM").upper()[:14]
    return sorted([i for i in items if i.get("score")], key=lambda x: -x["score"])


def write_post(item: dict, fmt: str) -> dict:
    """fmt: 'card' | 'breaking' | 'carousel'. Kart metinleri + Instagram açıklaması üretir."""
    spec = {
        "card": '{"headline": "en fazla 9 kelime", "summary": "en fazla 28 kelime, 1-2 cümle", "question": "en fazla 6 kelime soru", "image_query": "habere uygun, insan yüzü içermeyen genel fotoğraf için 2-3 kelimelik İngilizce arama", "caption": "Instagram açıklaması: 2-4 kısa cümle, sonunda soru"}',
        "breaking": '{"headline": "tek cümle, en fazla 12 kelime, sadece kesin bilgi", "summary": "en fazla 18 kelime", "caption": "Instagram açıklaması: 2-3 kısa cümle, gelişmeler takip edilecek notu, sonunda soru"}',
        "carousel": '{"headline": "kapak için merak uyandıran soru veya cümle, en fazla 8 kelime", "subline": "en fazla 6 kelime", "points": ["3 madde, her biri en fazla 18 kelime"], "question": "kapanış sorusu, en fazla 12 kelime", "caption": "Instagram açıklaması: 2-4 kısa cümle, sonunda soru"}',
    }[fmt]
    msg = _client().messages.create(
        model=config.CLAUDE_MODEL, max_tokens=4000, system=STYLE,
        messages=[{"role": "user", "content": (
            f"Kaynak: {item['source']}\nBaşlık: {item['title']}\nMetin: {item['summary']}\n\n"
            f"Bu haber için Instagram içeriği yaz. Sadece şu JSON'u dön:\n{spec}")}],
    )
    data = _json(_text(msg)) or {}
    data["category"] = item.get("category", "GÜNDEM")
    data["source"] = item["source"]
    return data
