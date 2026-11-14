# Duydun mu? otomasyonu

Her 15 dakikada bir haber kaynaklarını tarar, Claude ile en çok etkileşim alacak haberleri seçip yeniden yazar,
Duydun mu? kimliğiyle kart/karusel üretir ve @duydunmu.haber hesabında paylaşır.

- Planlı paylaşımlar: 09, 12 (karusel), 15, 18 (karusel), 21
- Son dakika: yalnızca AA kaynaklı, en fazla 45 dk önceki önemli gelişmeler, günde en fazla 3
- Gerekli secret'lar: `ANTHROPIC_API_KEY`, `IG_ACCESS_TOKEN` (isteğe bağlı: `IG_USER_ID`)
- Deneme: Actions > Duydun mu otomasyon > Run workflow > dry_run = true
- Ayarlar: `bot/config.py`
