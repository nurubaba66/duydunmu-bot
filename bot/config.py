"""Duydun mu? otomasyon ayarları. Gizli anahtarlar GitHub Secrets'tan gelir, burada yazılmaz."""
import os

# --- Gizli anahtarlar (GitHub > Settings > Secrets and variables > Actions) ---
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
IG_ACCESS_TOKEN = os.environ.get("IG_ACCESS_TOKEN", "")
IG_USER_ID = os.environ.get("IG_USER_ID", "")  # boşsa token'dan bulunur
GRAPH_HOST = os.environ.get("GRAPH_HOST", "https://graph.facebook.com")
GRAPH_VERSION = os.environ.get("GRAPH_VERSION", "v23.0")

# Paylaşmadan sadece deneme yap (true ise Instagram'a gönderilmez)
DRY_RUN = os.environ.get("DRY_RUN", "false").lower() == "true"

CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5-5")

# --- Haber kaynakları (RSS). Hepsi yalnızca okunur; metin Claude ile yeniden yazılır. ---
SOURCES = [
    {"name": "AA", "url": "https://www.aa.com.tr/tr/rss/default?cat=guncel", "trusted": True},
    {"name": "AA", "url": "https://www.aa.com.tr/tr/rss/default?cat=ekonomi", "trusted": True},
    {"name": "NTV", "url": "https://www.ntv.com.tr/gundem.rss", "trusted": False},
    {"name": "NTV", "url": "https://www.ntv.com.tr/ekonomi.rss", "trusted": False},
    {"name": "BBC Türkçe", "url": "https://feeds.bbci.co.uk/turkce/rss.xml", "trusted": False},
    {"name": "DW Türkçe", "url": "https://rss.dw.com/rdf/rss-tur-all", "trusted": False},
]

# --- Paylaşım planı (İstanbul saati) ---
POST_SLOTS = [9, 12, 15, 18, 21]      # normal haber saatleri
MAX_BREAKING_PER_DAY = 3               # günlük ekstra son dakika sınırı
MAX_ITEM_AGE_HOURS = 12                # bundan eski haber paylaşılmaz
BREAKING_MAX_AGE_MIN = 45              # son dakika en fazla bu kadar eski olabilir
MIN_SCORE = 6                          # 10 üzerinden, altındakiler paylaşılmaz

HANDLE = "@duydunmu.haber"
HASHTAGS = "#gündem #haber #sondakika #türkiye #duydunmu"
