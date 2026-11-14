"""Duydun mu? otomasyon ayarları. Gizli anahtarlar GitHub Secrets'tan gelir, burada yazılmaz."""
import os

# --- Gizli anahtarlar (GitHub > Settings > Secrets and variables > Actions) ---
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
IG_ACCESS_TOKEN = os.environ.get("IG_ACCESS_TOKEN", "")
IG_USER_ID = os.environ.get("IG_USER_ID", "")  # boşsa token'dan bulunur
# Instagram Login token'ları "IG" ile başlar ve graph.instagram.com'da çalışır
GRAPH_HOST = os.environ.get("GRAPH_HOST") or (
    "https://graph.instagram.com" if IG_ACCESS_TOKEN.startswith("IG") else "https://graph.facebook.com")
GRAPH_VERSION = os.environ.get("GRAPH_VERSION", "v23.0")

# GitHub (onay e-postaları için issue açılır; Actions'ta otomatik gelir)
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO = os.environ.get("GITHUB_REPOSITORY", "nurubaba66/duydunmu-bot")
OWNER_LOGIN = os.environ.get("OWNER_LOGIN", "nurubaba66")

# Paylaşmadan sadece deneme yap (true ise Instagram'a gönderilmez)
DRY_RUN = os.environ.get("DRY_RUN", "false").lower() == "true"

CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5-5")

# --- Haber kaynakları (RSS). Hepsi yalnızca okunur; metin Claude ile yeniden yazılır. ---
# trusted=True: resmi/ajans kaynağı, son dakika olarak onaysız paylaşılabilir
SOURCES = [
    # Ajanslar
    {"name": "AA", "url": "https://www.aa.com.tr/tr/rss/default?cat=guncel", "trusted": True},
    {"name": "AA", "url": "https://www.aa.com.tr/tr/rss/default?cat=ekonomi", "trusted": True},
    {"name": "AA", "url": "https://www.aa.com.tr/tr/rss/default?cat=spor", "trusted": True},
    {"name": "TRT Haber", "url": "https://www.trthaber.com/sondakika_articles.rss", "trusted": True},
    {"name": "TRT Haber", "url": "https://www.trthaber.com/manset_articles.rss", "trusted": True},
    # Farklı çizgilerden gazete ve siteler
    {"name": "NTV", "url": "https://www.ntv.com.tr/gundem.rss", "trusted": False},
    {"name": "NTV", "url": "https://www.ntv.com.tr/turkiye.rss", "trusted": False},
    {"name": "NTV", "url": "https://www.ntv.com.tr/ekonomi.rss", "trusted": False},
    {"name": "NTV", "url": "https://www.ntv.com.tr/yasam.rss", "trusted": False},
    {"name": "Habertürk", "url": "https://www.haberturk.com/rss/manset.xml", "trusted": False},
    {"name": "Habertürk", "url": "https://www.haberturk.com/rss", "trusted": False},
    {"name": "Hürriyet", "url": "https://www.hurriyet.com.tr/rss/gundem", "trusted": False},
    {"name": "Hürriyet", "url": "https://www.hurriyet.com.tr/rss/magazin", "trusted": False},
    {"name": "Milliyet", "url": "https://www.milliyet.com.tr/rss/rssnew/gundemrss.xml", "trusted": False},
    {"name": "Milliyet", "url": "https://www.milliyet.com.tr/rss/rssnew/magazinrss.xml", "trusted": False},
    {"name": "Sabah", "url": "https://www.sabah.com.tr/rss/gundem.xml", "trusted": False},
    {"name": "Sözcü", "url": "https://www.sozcu.com.tr/feeds-rss-category-gundem", "trusted": False},
    {"name": "Cumhuriyet", "url": "https://www.cumhuriyet.com.tr/rss/son_dakika.xml", "trusted": False},
    {"name": "BBC Türkçe", "url": "https://feeds.bbci.co.uk/turkce/rss.xml", "trusted": False},
    {"name": "DW Türkçe", "url": "https://rss.dw.com/rdf/rss-tur-all", "trusted": False},
]
# Türkiye'de o an en çok aranan konular (viral olay ve video radarı için)
TRENDS_URL = "https://trends.google.com/trending/rss?geo=TR"

# --- Resmi veri kaynakları ---
AFAD_URL = "https://deprem.afad.gov.tr/apiv2/event/filter"
QUAKE_MIN_MAG = 4.5          # bu büyüklük ve üstü otomatik son dakika
QUAKE_MAX_AGE_MIN = 40
MGM_URL = "https://servis.mgm.gov.tr/web/meteoalarm/{day}"   # day: today | tomorrow
MGM_BULLETIN_HOUR = 8         # her sabah hava uyarı bülteni (uyarı varsa)

# --- Paylaşım planı (İstanbul saati) ---
POST_SLOTS = [9, 12, 15, 18, 21]      # normal haber saatleri
CAROUSEL_SLOTS = [12, 18]
LIGHT_SLOTS = [21]                    # akşam: ilginç/magazin/spor ağırlıklı
RADAR_HOURS = []                      # video radarı e-postası (kapalı: sahibi istemedi)
REEL_SLOTS = [13, 20]                 # otomatik haber Reels'i (animasyonlu, efektli)
MAX_BREAKING_PER_DAY = 4              # günlük ekstra son dakika sınırı (deprem hariç)
MAX_ITEM_AGE_HOURS = 12
BREAKING_MAX_AGE_MIN = 45
MIN_SCORE = 6
LOOP_MINUTES = 5                      # sürekli çalışmada kontrol aralığı
LOOP_MAX_MINUTES = 330                # tek çalışmanın süresi (sonra kendini yeniden başlatır)

CATEGORIES = ["GÜNDEM", "HAYAT", "EKONOMİ", "ASAYİŞ", "HAVA", "DEPREM", "EĞİTİM", "SAĞLIK",
              "ULAŞIM", "SPOR", "MAGAZİN", "İLGİNÇ", "DÜNYA", "SİYASET", "TEKNOLOJİ"]
LIGHT_CATEGORIES = {"MAGAZİN", "İLGİNÇ", "SPOR", "TEKNOLOJİ"}

HANDLE = "@duydunmu.haber"
HASHTAGS = "#gündem #haber #sondakika #türkiye #duydunmu"
