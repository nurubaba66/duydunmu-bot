# Duydun mu? otomasyonu

@duydunmu.haber için haber tarama ve paylaşım sistemi.

- **Sürekli radar (loop.yml):** 5 dakikada bir AFAD depremleri, MGM hava uyarıları, 20+ haber kaynağı ve Google Trends taranır.
  - AFAD ≥ 4.5 deprem → haritalı son dakika kartı
  - MGM turuncu/kırmızı uyarı → anında; sarı uyarılar → her sabah 08:00 bülteni (bugün/yarın haritalı)
  - AA/TRT kaynaklı önemli gelişme → son dakika (günde en fazla 4)
  - Planlı paylaşımlar: 09, 12 (karusel), 15, 18 (karusel), 21 (hafif/eğlence ağırlıklı)
  - 10:00 ve 17:00 → Reels video radarı (e-posta)
- **Onay (approve.yml):** Hassas haberler paylaşılmaz, sahibine e-posta gider. Cevap olarak `paylaş` ya da `geç` yazılır.
- **Elle paylaşım (run.yml):** `manual/<klasör>/post.json` ile Reels/karusel/kart.
- Anahtarlar GitHub Secrets'ta: `ANTHROPIC_API_KEY`, `IG_ACCESS_TOKEN`, `IG_USER_ID`.
- İl sınırları: turkey-map-react (MIT), `bot/data_turkiye.LICENSE`.
