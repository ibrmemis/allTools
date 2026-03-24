import customtkinter as ctk

# ─────────────────────────────────────────
#  RENK & TEMA SABİTLERİ
# ─────────────────────────────────────────
BG        = "#191919"
PANEL     = "#202020"
CARD      = "#2b2b2b"
ACCENT    = "#0067c0"
ACCENT2   = "#4cc2ff"
TEXT      = "#ffffff"
SUBTEXT   = "#a0a0a0"
SUCCESS   = "#22c55e"
WARNING   = "#f59e0b"
DANGER    = "#ef4444"
BORDER    = "#333333"

# ─────────────────────────────────────────
#  YAZI TİPLERİ
# ─────────────────────────────────────────
FONT_TITLE  = ("Segoe UI", 22, "bold")
FONT_HEAD   = ("Segoe UI", 13, "bold")
FONT_BODY   = ("Segoe UI", 11)
FONT_SMALL  = ("Segoe UI", 9)
FONT_MONO   = ("Consolas", 10)

def init_theme():
    """Uygulamanın CustomTkinter temasını başlatır."""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
