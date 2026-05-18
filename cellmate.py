"""
CellMate v2.1 — Prisoner AI Companion — Built to Rebuild Lives
Gemma 4 Good Hackathon 2026
"""

# ─── STANDARD IMPORTS ──────────────────────────────────────
import hashlib
import os
import base64
import tempfile
import streamlit as st
import streamlit.components.v1 as components
import requests


# ─── OPTIONAL RAG IMPORTS ──────────────────────────────────
try:
    import chromadb
    import fitz  # pymupdf
    RAG_OK = True
except ImportError:
    RAG_OK = False

# ─── OPTIONAL VOICE IMPORTS ────────────────────────────────
try:
    from faster_whisper import WhisperModel
    WHISPER_OK = True
except ImportError:
    WHISPER_OK = False

try:
    import pyttsx3
    TTS_OK = True
except ImportError:
    TTS_OK = False

try:
    from audio_recorder_streamlit import audio_recorder
    RECORDER_OK = True
except ImportError:
    RECORDER_OK = False


# ─── LOGO HELPER ───────────────────────────────────────────
def get_logo_b64(path: str = "logo.png") -> str | None:
    if os.path.exists(path):
        with open(path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        ext  = path.rsplit(".", 1)[-1].lower()
        mime = {"png": "image/png", "jpg": "image/jpeg",
                "jpeg": "image/jpeg", "svg": "image/svg+xml"}.get(ext, "image/png")
        return f"data:{mime};base64,{data}"
    return None


# ═══════════════════════════════════════════════════════════
# SECTION 1 — LANGUAGE CONFIGURATION
# ═══════════════════════════════════════════════════════════

LANGUAGES = {
    "English":   {"code": "en",  "dir": "ltr",
                  "prompt": "Always respond in clear, simple English."},

    "Français":  {"code": "fr",  "dir": "ltr",
                  "prompt": "Réponds toujours en français simple et clair."},

    "العربية":   {"code": "ar",  "dir": "rtl",
                  "prompt": "أجب دائماً باللغة العربية البسيطة والواضحة."},
}

# ═══════════════════════════════════════════════════════════
# SECTION 1b — FULL UI TRANSLATIONS
# ═══════════════════════════════════════════════════════════

UI = {
    "English": {
        "lang_label":       "Language",
        "features_label":   "FEATURES",
        "status_label":     "SYSTEM STATUS",
        "voice_label":      "Voice Features",
        "tagline":          "Locked in. Not locked out.",
        "logo_hint":        "← Add cellmate_logo.png to use your logo",
        "footer":           "Gemma 4 Good Hackathon · 2026<br>Powered by Gemma 4 E2B + Ollama<br>100% offline · 100% private · free",
        "clear":            "Clear ↺",
        "speak":            "🔊  Read aloud",
        "thinking":         "CellMate is thinking...",
        "transcribing":     "Transcribing audio...",
        "gen_audio":        "Generating audio...",
        "audio_fail":       "Audio generation failed. Check pyttsx3.",
        "voice_unavail":    "Voice packages not installed. See README for setup.",
        "active_feature":   "Active feature",
        "no_internet":      "📡  No internet required",
        "ollama_ok":        "🟢  Gemma 4 E2B · running",
        "ollama_err":       "🔴  Ollama not running",
        "run_cmd":          "Run: ollama run gemma4:e2b",
        "timeout_err":      "Response timed out. Is Ollama running?",
        "record_hint":      "Click the mic, speak, then click again to stop",
        "audio_ready":      "Transcribed — sending…",
        "welcome_sub":      "CellMate: Locked in. Not locked out.",
        "welcome_h1":       "The Companion Built to Rebuild Lives.",
        "welcome_body":     "CellMate gives prisoners access to education, mental health support, legal information and reintegration guidance — running fully offline on Gemma 4 E2B. No internet. No cost. Always available.",
        "card_model":       "Model",
        "card_model_body":  "Gemma 4 E2B — Google's edge model, built for local deployment on limited hardware.",
        "card_who":         "Who It's For",
        "card_who_body":    "Incarcerated individuals worldwide — the most digitally excluded population on earth.",
        "card_conn":        "Connectivity",
        "card_conn_body":   "Zero internet required. Runs entirely on your device via Ollama. Private by design.",
        "card_start":       "How To Start",
        "card_start_body":  "Choose a feature from the sidebar on the left. Your conversation stays on this device only.",
        "feat_rights":      "Know Your Rights",
        "feat_learn":       "Learn Something New",
        "feat_head":        "Keep Your Head Right",
        "feat_gate":        "Prepare For The Gate",
        "feat_letter":      "Write Home",
        "disc_rights":      "⚠ General information only — not legal advice. Consult a lawyer for your specific situation.",
        "disc_learn":       "🕮  Every skill you build now opens a door later.",
        "disc_head":        "❤︎  Not professional therapy. If in crisis, speak to prison staff immediately.",
        "disc_gate":        "🌱  Preparation starts today. Every step now is a step toward your future.",
        "disc_letter":      "💌  This is your space to find your words. Take your time.",
        "ph_rights":        "What are my rights during a search? Can I appeal my sentence?",
        "ph_learn":         "Teach me basic math. How does the internet work?",
        "ph_head":          "I'm feeling anxious. How do I deal with loneliness?",
        "ph_gate":          "Help me write a CV with a 3 year gap. What do I do first when I get out?",
        "ph_letter":        "Tell me who you want to write to...",
        "letter_banner":    "✉  CellMate will not write the letter for you immediately. It will help you find your own words — one question at a time.",
        "chat_footer":      "CellMate · Gemma 4 E2B via Ollama · 100% offline · Gemma 4 Good Hackathon 2026",
        "voice_all_ready":  "🟢  All voice packages ready",
        "voice_missing":    "Missing:",
        # RAG
        "rag_searching":    "Searching legal documents",
        "rag_no_db":        "⚠ Legal document index not found. Run index_legal_docs.py first.",
        "rag_no_results":   "No relevant documents found — answering from general knowledge.",
        "rag_source":       "📄 Source",
        "rag_page":         "p.",
        "rag_ready":        "🟢  Legal index ready",
        "rag_not_ready":    "⚠  Legal index missing — run index_legal_docs.py",
    },

    "Français": {
        "lang_label":       "Langue",
        "features_label":   "FONCTIONNALITÉS",
        "status_label":     "ÉTAT DU SYSTÈME",
        "voice_label":      "Fonctions Vocales",
        "tagline":          "Enfermé. Pas exclu.",
        "logo_hint":        "← Ajoutez cellmate_logo.png pour votre logo",
        "footer":           "Gemma 4 Good Hackathon · 2026<br>Propulsé par Gemma 4 E2B + Ollama<br>100% hors ligne · 100% privé · gratuit",
        "clear":            "Effacer ↺",
        "speak":            "🔊  Lire à voix haute",
        "thinking":         "CellMate réfléchit...",
        "transcribing":     "Transcription en cours...",
        "gen_audio":        "Génération audio...",
        "audio_fail":       "Échec audio. Vérifiez pyttsx3.",
        "voice_unavail":    "Paquets vocaux non installés. Voir README.",
        "active_feature":   "Fonction active",
        "no_internet":      "📡  Pas d'internet requis",
        "ollama_ok":        "🟢  Gemma 4 E2B · actif",
        "ollama_err":       "🔴  Ollama inactif",
        "run_cmd":          "Lancer : ollama run gemma4:e2b",
        "timeout_err":      "Délai dépassé. Ollama est-il actif ?",
        "record_hint":      "🗣  Cliquez, parlez, re-cliquez pour arrêter",
        "audio_ready":      " Transcrit — envoi…",
        "welcome_sub":      "CellMate — Enfermé. Pas exclu.",
        "welcome_h1":       "Le compagnon conçu pour reconstruire des vies.",
        "welcome_body":     "CellMate donne aux détenus accès à des informations juridiques, à l'éducation, au soutien en santé mentale et à la réinsertion — entièrement hors ligne avec Gemma 4 E2B. Sans internet. Sans frais. Toujours disponible.",
        "card_model":       "Modèle",
        "card_model_body":  "Gemma 4 E2B — modèle edge de Google, conçu pour un matériel limité.",
        "card_who":         "Pour qui",
        "card_who_body":    "Les personnes incarcérées dans le monde — la population la plus exclue numériquement.",
        "card_conn":        "Connectivité",
        "card_conn_body":   "Aucune connexion requise. Fonctionne sur votre appareil via Ollama. Privé par conception.",
        "card_start":       "Comment commencer",
        "card_start_body":  "Choisissez une fonction dans le panneau de gauche. Votre conversation reste sur cet appareil.",
        "feat_rights":      "Connaître vos Droits",
        "feat_learn":       "Apprendre Quelque Chose",
        "feat_head":        "Garder la Tête Droite",
        "feat_gate":        "Préparer la Sortie",
        "feat_letter":      "Écrire à la Maison",
        "disc_rights":      "⚠  Information générale uniquement — pas un conseil juridique. Consultez un avocat.",
        "disc_learn":       "🕮  Chaque compétence acquise aujourd'hui ouvre une porte demain.",
        "disc_head":        "❤︎   Pas de thérapie professionnelle. En crise, parlez au personnel pénitentiaire.",
        "disc_gate":        "🌱  La préparation commence aujourd'hui. Chaque pas vous rapproche de votre avenir.",
        "disc_letter":      "💌  Cet espace est le vôtre pour trouver vos mots. Prenez votre temps.",
        "ph_rights":        "Quels sont mes droits lors d'une fouille ? Puis-je faire appel ?",
        "ph_learn":         "Apprends-moi les maths de base. Comment fonctionne internet ?",
        "ph_head":          "Je me sens anxieux. Comment gérer la solitude ?",
        "ph_gate":          "Aide-moi à faire un CV avec 3 ans de vide. Que faire en premier à la sortie ?",
        "ph_letter":        "Dis-moi à qui tu veux écrire...",
        "letter_banner":    "✉  CellMate n'écrira pas la lettre immédiatement. Il vous aidera à trouver vos propres mots — une question à la fois.",
        "chat_footer":      "CellMate · Gemma 4 E2B via Ollama · 100% hors ligne · Gemma 4 Good Hackathon 2026",
        "voice_all_ready":  "🟢  Tous les paquets vocaux sont prêts",
        "voice_missing":    "Manquants :",
        # RAG
        "rag_searching":    "Recherche dans les documents juridiques",
        "rag_no_db":        "⚠ Index juridique introuvable. Lancez index_legal_docs.py d'abord.",
        "rag_no_results":   "Aucun document pertinent — réponse depuis les connaissances générales.",
        "rag_source":       "📄 Source",
        "rag_page":         "p.",
        "rag_ready":        "🟢  Index juridique prêt",
        "rag_not_ready":    "⚠  Index manquant — lancez index_legal_docs.py",
    },

    "العربية": {
        "lang_label":       "اللغة",
        "features_label":   "الميزات",
        "status_label":     "حالة النظام",
        "voice_label":      "ميزات الصوت",
        "tagline":          "خلف القضبان. لكن لست معزولاً.",
        "logo_hint":        "← أضف cellmate_logo.png لاستخدام شعارك",
        "footer":           "هاكاثون Gemma 4 Good · 2026<br>مدعوم بـ Gemma 4 E2B + Ollama<br>100% بدون إنترنت · 100% خاص · مجاني",
        "clear":            "مسح ↺",
        "speak":            "🔊  قراءة بصوت عالٍ",
        "thinking":         "CellMate يفكر...",
        "transcribing":     "جارٍ النسخ...",
        "gen_audio":        "جارٍ توليد الصوت...",
        "audio_fail":       "فشل توليد الصوت. تحقق من pyttsx3.",
        "voice_unavail":    "حزم الصوت غير مثبتة. راجع README.",
        "active_feature":   "الميزة النشطة",
        "no_internet":      "📡  لا يلزم إنترنت",
        "ollama_ok":        "🟢  Gemma 4 E2B · يعمل",
        "ollama_err":       "🔴  Ollama لا يعمل",
        "run_cmd":          "شغّل: ollama run gemma4:e2b",
        "timeout_err":      "انتهت المهلة. هل Ollama يعمل؟",
        "record_hint":      "انقر، تحدث، ثم انقر للإيقاف",
        "audio_ready":      "تمت الترجمة — جارٍ الإرسال…",
        "welcome_sub":      "CellMate — نظام دعم الذكاء الاصطناعي للسجناء",
        "welcome_h1":       "الرفيق المصمم لإعادة بناء الحياة",
        "welcome_body":     "يمنح CellMate السجناء الوصول إلى المعلومات القانونية والتعليم ودعم الصحة النفسية والتوجيه لإعادة الاندماج — يعمل بالكامل دون إنترنت على Gemma 4 E2B. بدون إنترنت. بدون تكلفة. متاح دائماً.",
        "card_model":       "النموذج",
        "card_model_body":  "Gemma 4 E2B — نموذج Google للحواف، مصمم للأجهزة المحدودة.",
        "card_who":         "لمن هو",
        "card_who_body":    "المعتقلون حول العالم — الفئة الأكثر إقصاءً رقمياً على الأرض.",
        "card_conn":        "الاتصال",
        "card_conn_body":   "لا إنترنت مطلوب. يعمل على جهازك عبر Ollama. خصوصية بالتصميم.",
        "card_start":       "كيف تبدأ",
        "card_start_body":  "اختر ميزة من الشريط الجانبي. تبقى محادثتك على هذا الجهاز فقط.",
        "feat_rights":      "اعرف حقوقك",
        "feat_learn":       "تعلّم شيئاً جديداً",
        "feat_head":        "حافظ على صحتك النفسية",
        "feat_gate":        "استعد للخروج",
        "feat_letter":      "اكتب رسالة للمنزل",
        "disc_rights":      "⚠  معلومات عامة فقط — ليست استشارة قانونية. استشر محامياً.",
        "disc_learn":       "🕮  كل مهارة تتعلمها الآن تفتح باباً لاحقاً.",
        "disc_head":        "❤︎   ليست علاجاً نفسياً. في الأزمات، تحدث مع موظفي السجن.",
        "disc_gate":        "🌱  التحضير يبدأ اليوم. كل خطوة الآن هي خطوة نحو مستقبلك.",
        "disc_letter":      "💌  هذا مكانك لإيجاد كلماتك. خذ وقتك.",
        "ph_rights":        "ما حقوقي أثناء التفتيش؟ هل يمكنني الاستئناف؟",
        "ph_learn":         "علّمني الرياضيات الأساسية. كيف يعمل الإنترنت؟",
        "ph_head":          "أشعر بالقلق. كيف أتعامل مع الوحدة؟",
        "ph_gate":          "ساعدني في كتابة سيرة ذاتية بفجوة 3 سنوات. ماذا أفعل أولاً عند خروجي؟",
        "ph_letter":        "أخبرني لمن تريد الكتابة...",
        "letter_banner":    "✉  لن يكتب CellMate الرسالة فوراً. سيساعدك في إيجاد كلماتك الخاصة — سؤالاً واحداً في كل مرة.",
        "chat_footer":      "CellMate · Gemma 4 E2B عبر Ollama · 100% بدون إنترنت · هاكاثون Gemma 4 Good 2026",
        "voice_all_ready":  "🟢  جميع حزم الصوت جاهزة",
        "voice_missing":    "مفقود:",
        # RAG
        "rag_searching":    "البحث في الوثائق القانونية",
        "rag_no_db":        "⚠ فهرس الوثائق القانونية غير موجود. شغّل index_legal_docs.py أولاً.",
        "rag_no_results":   "لم يُعثر على وثائق ذات صلة — الإجابة من المعرفة العامة.",
        "rag_source":       "📄 المصدر",
        "rag_page":         "ص.",
        "rag_ready":        "🟢  الفهرس القانوني جاهز",
        "rag_not_ready":    "⚠  الفهرس مفقود — شغّل index_legal_docs.py",
    },
}


def t(key: str) -> str:
    """Translate a UI key for the active language. Falls back to English."""
    lang = st.session_state.get("language", "English")
    return UI.get(lang, UI["English"]).get(key, UI["English"].get(key, key))


# ═══════════════════════════════════════════════════════════
# SECTION 2 — VOICE HELPERS
# ═══════════════════════════════════════════════════════════

@st.cache_resource(show_spinner=False)
def load_whisper_model():
    if not WHISPER_OK:
        return None
    try:
        return WhisperModel("tiny", device="cpu", compute_type="int8")
    except Exception:
        return None


def transcribe_audio(audio_bytes: bytes, lang_code: str) -> str | None:
    model = load_whisper_model()
    if not model:
        return None
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(audio_bytes)
        tmp = f.name
    try:
        segments, _ = model.transcribe(tmp, language=lang_code)
        return " ".join(s.text.strip() for s in segments).strip()
    except Exception as e:
        st.error(f"Transcription error: {e}")
        return None
    finally:
        os.unlink(tmp)


def speak_text(text: str, is_therapy: bool = False) -> bytes | None:
    """
    Text → WAV bytes via pyttsx3 (fully offline).
    Therapy mode: slower rate + prefers calmer voice.
    Returns None on failure.
    """
    if not TTS_OK:
        return None
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty("voices")
        if is_therapy and voices:
            calm_kw = ["female", "zira", "hazel", "susan",
                       "victoria", "fiona", "samantha", "karen"]
            for v in voices:
                if any(k in v.name.lower() for k in calm_kw):
                    engine.setProperty("voice", v.id)
                    break
        engine.setProperty("rate",   125 if is_therapy else 165)
        engine.setProperty("volume", 1.0)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            tmp = f.name
        engine.save_to_file(text, tmp)
        engine.runAndWait()
        engine.stop()
        with open(tmp, "rb") as f:
            data = f.read()
        os.unlink(tmp)
        return data
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════
# SECTION 4 — PAGE CONFIG & CSS
# ═══════════════════════════════════════════════════════════

st.set_page_config(
    page_title="CellMate",
    page_icon="logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@font-face {
    font-family: 'IBM Plex Mono';
    src: url('fonts/IBMPlexMono-Regular.ttf') format('truetype');
}

@font-face {
    font-family: 'IBM Plex Sans';
    src: url('fonts/IBMPlexSans-Regular.ttf') format('truetype');
}

.stApp { background-color:#0e0b14 !important; font-family:'IBM Plex Sans',sans-serif; }
#MainMenu { visibility:hidden; }
footer    { visibility:hidden; }

[data-testid="stSidebar"]        { background-color:#13101a !important; border-right:1px solid #2a1f3d !important; }
[data-testid="stSidebarContent"] { background-color:#13101a !important; padding:0 !important; }
[data-testid="stMainBlockContainer"] { background-color:#0e0b14 !important; }

p, span, label, div, h1, h2, h3, h4 { color:#e8e0f0 !important; }

[data-testid="stSelectbox"] label { color:#6a5a8a !important; font-family:'IBM Plex Mono',monospace !important; font-size:0.75rem !important; letter-spacing:0.08em !important; text-transform:uppercase !important; }
[data-testid="stSelectbox"] > div > div { background-color:#1a1525 !important; border:1px solid #3a2d52 !important; border-radius:4px !important; color:#e8e0f0 !important; }

[data-testid="stChatMessageContent"] { background-color:#1a1525 !important; border:1px solid #2a1f3d !important; border-radius:4px !important; color:#e8e0f0 !important; }
[data-testid="stChatInput"]          { background-color:#13101a !important; border-top:1px solid #2a1f3d !important; }
[data-testid="stChatInput"] textarea { background-color:#1a1525 !important; border:1px solid #3a2d52 !important; color:#e8e0f0 !important; border-radius:4px !important; font-family:'IBM Plex Sans',sans-serif !important; }
[data-testid="stChatInput"] textarea:focus { border-color:#9b59b6 !important; box-shadow:0 0 0 1px #9b59b6 !important; }
[data-testid="stChatInput"] button   { background:linear-gradient(135deg,#d4844a,#9b59b6) !important; color:#fff !important; border-radius:4px !important; border:none !important; }

[data-testid="stButton"] > button       { background-color:transparent !important; border:1px solid #3a2d52 !important; color:#6a5a8a !important; font-family:'IBM Plex Mono',monospace !important; font-size:0.75rem !important; border-radius:4px !important; transition:all 0.2s !important; }
[data-testid="stButton"] > button:hover { border-color:#c8729a !important; color:#c8729a !important; }

hr { border-color:#2a1f3d !important; }
[data-testid="stSpinner"] p { color:#c8729a !important; }
[data-testid="stSuccess"] { background-color:#0d1a12 !important; border:1px solid #1a3d25 !important; color:#3fb950 !important; }
[data-testid="stError"]   { background-color:#1a0d10 !important; border:1px solid #3d1a20 !important; color:#f85149 !important; }
[data-testid="stInfo"]    { background-color:#0e0b1a !important; border:1px solid #2a1f3d !important; color:#9b59b6 !important; }
[data-testid="stWarning"] { background-color:#1a1000 !important; border:1px solid #3d2800 !important; color:#d4844a !important; }

audio { filter:invert(0.85) hue-rotate(240deg); width:100%; margin-top:0.4rem; border-radius:4px; }

::-webkit-scrollbar       { width:4px; }
::-webkit-scrollbar-track { background:#13101a; }
::-webkit-scrollbar-thumb { background:#3a2d52; border-radius:4px; }
::-webkit-scrollbar-thumb:hover { background:#9b59b6; }

.rtl-content { direction:rtl !important; text-align:right !important; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# SECTION 5 — FEATURES
# ═══════════════════════════════════════════════════════════

FEATURES_META = {

    "learn": {
        "icon": "🕮", "name": "feat_learn", "disc": "disc_learn", "ph": "ph_learn",
        "letter": False, "therapy": False,
        "system": """You are CellMate, a patient educational tutor for prisoners.
        Start from the basics. Break things into small steps. Use real examples.
        Be warm and encouraging. Never make them feel unintelligent.""",
    },

    "head": {
        "icon": "💭", "name": "feat_head", "disc": "disc_head", "ph": "ph_head",
        "letter": False, "therapy": True,
        "system": """You are CellMate, a mental wellness companion for someone in prison.
        Be calm, warm, and non-judgmental. Acknowledge feelings before giving advice.
        Offer practical coping strategies. Never diagnose.
        For serious concerns always recommend speaking to prison staff or a counselor.
        When the user is speaking by voice, respond in short, gentle sentences
        — as if you are speaking calmly back to them in person.""",
    },

    "rights": {
        "icon": "⚖", "name": "feat_rights", "disc": "disc_rights", "ph": "ph_rights",
        "letter": False, "therapy": False,
        "system": """You are CellMate, a legal information assistant built for prisoners.
        Explain legal rights clearly and simply in plain language.
        Always say you are not a lawyer — they should consult one for their specific case.
        Use numbered lists for steps. Be calm and reassuring.""",
    },

    "letter": {
        "icon": "✉︎", "name": "feat_letter", "disc": "disc_letter", "ph": "ph_letter",
        "letter": True, "therapy": False,
        "system": """You are CellMate, a compassionate letter-writing companion for prisoners.
        NEVER write a complete letter immediately. Guide them through their feelings first.
        Step 1 — Ask who they are writing to and why.
        Step 2 — Ask one feeling-focused question at a time.
        Step 3 — Reflect their words back warmly before continuing.
        Step 4 — Only after 3 or 4 exchanges, offer to shape their words into a letter.
        Step 5 — Write a draft that sounds like THEM. Raw, human, and real.
        This letter may be the most important thing they write all year.""",
    },

    "gate": {
        "icon": "🕊", "name": "feat_gate", "disc": "disc_gate", "ph": "ph_gate",
        "letter": False, "therapy": False,
        "system": """You are CellMate, a reintegration coach for prisoners preparing for release.
        Be practical and realistic. Help with CVs, interviews, housing, budgeting.
        Give step-by-step actionable advice. Acknowledge reintegration is genuinely hard.""",
    },

}

FEATURE_KEYS = list(FEATURES_META.keys())


def build_messages(active_key: str, history: list) -> list:
    lang        = st.session_state.get("language", "English")
    prompt      = LANGUAGES[lang]["prompt"]
    base        = FEATURES_META[active_key]["system"]
    full_system = f"{base}\n\nIMPORTANT — LANGUAGE RULE (non-negotiable): {prompt}"
    return [{"role": "system", "content": full_system}] + history


# ═══════════════════════════════════════════════════════════
# SECTION 3 — RAG ENGINE (Legal feature only)
# ═══════════════════════════════════════════════════════════

CHROMA_DIR      = "chroma_db"
COLLECTION_NAME = "legal_docs"
EMBED_MODEL     = "nomic-embed-text"
RAG_TOP_K       = 4   # number of chunks to retrieve


@st.cache_resource(show_spinner=False)
def load_rag_collection():
    """
    Load the persisted ChromaDB collection once at startup.
    Returns None if the DB doesn't exist or RAG deps are missing.
    """
    if not RAG_OK:
        return None
    if not os.path.isdir(CHROMA_DIR):
        return None
    try:
        client = chromadb.PersistentClient(path=CHROMA_DIR)
        col    = client.get_collection(COLLECTION_NAME)
        return col if col.count() > 0 else None
    except Exception:
        return None


def get_query_embedding(query: str) -> list[float] | None:
    """Embed the user query via Ollama nomic-embed-text."""
    try:
        resp = requests.post(
            "http://localhost:11434/api/embeddings",
            json={"model": EMBED_MODEL, "prompt": query},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()["embedding"]
    except Exception:
        return None


def retrieve_legal_context(query: str, collection) -> tuple[str, list[dict]]:
    """
    Embed query, search ChromaDB, return:
      - context string to inject into the system prompt
      - list of source metadata dicts for citation display
    """
    embedding = get_query_embedding(query)
    if not embedding:
        return "", []

    results = collection.query(
        query_embeddings=[embedding],
        n_results=RAG_TOP_K,
        include=["documents", "metadatas", "distances"],
    )

    docs      = results["documents"][0]
    metas     = results["metadatas"][0]
    distances = results["distances"][0]

    # Filter out low-relevance chunks (cosine distance > 0.55)
    filtered = [
        (doc, meta)
        for doc, meta, dist in zip(docs, metas, distances)
        if dist < 0.55
    ]

    if not filtered:
        return "", []

    context_parts = []
    sources       = []
    seen_sources  = set()

    for doc, meta in filtered:
        source = meta.get("source", "unknown")
        page   = meta.get("page", "?")
        context_parts.append(f"[{source}, p.{page}]\n{doc}")

        source_key = f"{source}_p{page}"
        if source_key not in seen_sources:
            seen_sources.add(source_key)
            sources.append({"file": source, "page": page})

    context = "\n\n---\n\n".join(context_parts)
    return context, sources


def build_messages_with_rag(active_key: str, history: list, context: str) -> list:
    """
    Same as build_messages but injects retrieved legal context
    into the system prompt for the rights feature.
    """
    lang       = st.session_state.get("language", "English")
    prompt     = LANGUAGES[lang]["prompt"]
    base       = FEATURES_META[active_key]["system"]

    if context:
        rag_block = (
            "\n\n━━━ RETRIEVED LEGAL CONTEXT ━━━\n"
            "The following excerpts are from official legal documents. "
            "Use them to ground your answer. Always mention the source when you cite a fact.\n\n"
            f"{context}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        )
    else:
        rag_block = ""

    full_system = (
        f"{base}{rag_block}"
        f"\n\nIMPORTANT — LANGUAGE RULE (non-negotiable): {prompt}"
    )
    return [{"role": "system", "content": full_system}] + history


# ═══════════════════════════════════════════════════════════
# SECTION 6 — SESSION STATE
# ═══════════════════════════════════════════════════════════

defaults = {
    "active":          None,
    "messages":        {k: [] for k in FEATURE_KEYS},
    "language":        "English",
    "last_audio_hash": None,
    "tts_audio":       None,
    "tts_autoplay":    False,
    "pending_voice":   None,
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ═══════════════════════════════════════════════════════════
# SECTION 7 — SIDEBAR
# ═══════════════════════════════════════════════════════════

LOGO_URI = get_logo_b64("logo.png")

with st.sidebar:

    # ── Logo / wordmark ──────────────────────────────────────
    if LOGO_URI:
        home_html = f"""
            <div style='padding:1.5rem 1rem 1rem; display:flex; align-items:center;
                        gap:0.75rem; cursor:pointer;' title="Go to home">
                <img src="{LOGO_URI}" style='width:40px; height:40px; object-fit:contain;' />
                <div>
                    <div style='font-family:"IBM Plex Sans",sans-serif;
                                font-size:1.15rem; font-weight:600;
                                background:linear-gradient(135deg,#d4844a,#9b59b6,#c8729a);
                                -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                                background-clip:text; letter-spacing:-0.01em;'>
                        CellMate
                    </div>
                    <div style='font-family:"IBM Plex Mono",monospace;
                                font-size:0.6rem; color:#4a3a5a; margin-top:2px;
                                letter-spacing:0.1em; text-transform:uppercase;'>
                        {t("tagline")}
                    </div>
                </div>
            </div>
        """
    else:
        home_html = f"""
            <div style='padding:1.5rem 1rem 1rem; cursor:pointer;' title="Go to home">
                <div style='font-family:"IBM Plex Sans",sans-serif;
                            font-size:1.3rem; font-weight:600;
                            background:linear-gradient(135deg,#d4844a,#9b59b6,#c8729a);
                            -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                            background-clip:text; letter-spacing:-0.02em;'>
                    💎 CellMate
                </div>
                <div style='font-family:"IBM Plex Mono",monospace;
                            font-size:0.65rem; color:#4a3a5a; margin-top:4px;
                            letter-spacing:0.1em; text-transform:uppercase;'>
                    {t("tagline")}
                </div>
                <div style='font-family:"IBM Plex Mono",monospace;
                            font-size:0.58rem; color:#3a2d52; margin-top:3px;'>
                    {t("logo_hint")}
                </div>
            </div>
        """

    if st.button(
        "💎 CellMate" if not LOGO_URI else "⌂ Home",
        key="home_btn",
        use_container_width=True,
        type="secondary",
    ):
        st.session_state.active          = None
        st.session_state.tts_audio       = None
        st.session_state.tts_autoplay    = False
        st.session_state.pending_voice   = None
        st.session_state.last_audio_hash = None
        st.rerun()

    st.markdown(home_html, unsafe_allow_html=True)
    st.divider()

    # ── Language selector ────────────────────────────────────
    lang_options = list(LANGUAGES.keys())
    lang_labels  = [f"{LANGUAGES[l]['code']}  {l}" for l in lang_options]
    current_idx  = lang_options.index(st.session_state.language)

    st.markdown(f"""
        <div style='padding:0.4rem 0 0.2rem; font-family:"IBM Plex Mono",monospace;
                    font-size:0.65rem; color:#4a3a5a; letter-spacing:0.1em;
                    text-transform:uppercase;'>
            {t("lang_label")}
        </div>
    """, unsafe_allow_html=True)

    selected_label = st.selectbox(
        label="lang_sel",
        options=lang_labels,
        index=current_idx,
        label_visibility="collapsed",
        key="lang_selectbox",
    )
    selected_lang = lang_options[lang_labels.index(selected_label)]
    if selected_lang != st.session_state.language:
        st.session_state.language      = selected_lang
        st.session_state.pending_voice = None
        st.rerun()

    st.divider()

    # ── Feature navigation ───────────────────────────────────
    st.markdown(f"""
        <div style='padding:0.5rem 0 0.25rem; font-family:"IBM Plex Mono",monospace;
                    font-size:0.65rem; color:#4a3a5a; letter-spacing:0.1em;
                    text-transform:uppercase;'>
            {t("features_label")}
        </div>
    """, unsafe_allow_html=True)

    for key in FEATURE_KEYS:
        meta      = FEATURES_META[key]
        feat_name = t(meta["name"])
        is_active = st.session_state.active == key
        label     = f"**{meta['icon']}  {feat_name}**" if is_active else f"{meta['icon']}  {feat_name}"

        if st.button(label, key=f"nav_{key}", use_container_width=True, type="secondary"):
            st.session_state.active          = key
            st.session_state.tts_audio       = None
            st.session_state.tts_autoplay    = False
            st.session_state.pending_voice   = None
            st.session_state.last_audio_hash = None
            st.rerun()

        if is_active:
            st.markdown("""
                <style>
                div[data-testid="stButton"]:last-of-type > button {
                    border-left:3px solid #c8729a !important;
                    color:#c8729a !important;
                    background:linear-gradient(90deg,rgba(155,89,182,0.1),transparent) !important;
                }
                </style>
            """, unsafe_allow_html=True)

    # ── Voice status (shown only on head feature) ────────────
    if st.session_state.active == "head" and (RECORDER_OK and WHISPER_OK):
        st.markdown(f"""
            <div style='font-family:"IBM Plex Mono",monospace;
                        font-size:0.65rem; color:#2a5a3a; padding:0.25rem 0;'>
                🎙 {t("voice_all_ready")}
            </div>
        """, unsafe_allow_html=True)
    elif st.session_state.active == "head":
        missing = []
        if not WHISPER_OK:  missing.append("faster-whisper")
        if not RECORDER_OK: missing.append("audio-recorder-streamlit")
        st.markdown(f"""
            <div style='font-family:"IBM Plex Mono",monospace;
                        font-size:0.65rem; color:#4a3a5a; padding:0.25rem 0; line-height:1.6;'>
                {t("voice_missing")} {', '.join(missing)}
            </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ── System status ────────────────────────────────────────
    st.markdown(f"""
        <div style='padding:0.25rem 0; font-family:"IBM Plex Mono",monospace;
                    font-size:0.65rem; color:#4a3a5a; letter-spacing:0.1em;
                    text-transform:uppercase;'>
            {t("status_label")}
        </div>
    """, unsafe_allow_html=True)

    try:
        requests.get("http://localhost:11434", timeout=2)
        st.success(t("ollama_ok"))
        st.info(t("no_internet"))
    except Exception:
        st.error(t("ollama_err"))
        st.markdown(f"""
            <div style='font-family:"IBM Plex Mono",monospace;
                        font-size:0.72rem; color:#4a3a5a; margin-top:4px;'>
                {t("run_cmd")}
            </div>
        """, unsafe_allow_html=True)

    # ── RAG index status ─────────────────────────────────────
    rag_col = load_rag_collection()
    if rag_col is not None:
        st.markdown(f"""
            <div style='font-family:"IBM Plex Mono",monospace;
                        font-size:0.65rem; color:#2a5a3a; margin-top:4px;'>
                {t("rag_ready")} ({rag_col.count()} chunks)
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div style='font-family:"IBM Plex Mono",monospace;
                        font-size:0.65rem; color:#5a4a20; margin-top:4px;'>
                {t("rag_not_ready")}
            </div>
        """, unsafe_allow_html=True)

    st.divider()

    st.markdown(f"""
        <div style='font-family:"IBM Plex Mono",monospace;
                    font-size:0.65rem; color:#3a2d52; line-height:2;'>
            {t("footer")}
        </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# SECTION 8 — MAIN AREA
# ═══════════════════════════════════════════════════════════

is_rtl    = LANGUAGES[st.session_state.language]["dir"] == "rtl"
lang_code = LANGUAGES[st.session_state.language]["code"]
rtl_class = "rtl-content" if is_rtl else ""


# ── Welcome screen ─────────────────────────────────────────
if st.session_state.active is None:

    if LOGO_URI:
        st.markdown(f"""
            <div style='padding:0rem 0 0rem;'>
                <img src="{LOGO_URI}" style='width:100px; height:100px; object-fit:contain;' />
            </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
        <div class="{rtl_class}" style='max-width:800px; padding:{"1rem" if LOGO_URI else "3rem"} 0 2rem;'>
            <div style='font-family:"IBM Plex Mono",monospace; font-size:0.68rem;
                        color:#4a3a5a; letter-spacing:0.12em; text-transform:uppercase;
                        margin-bottom:0.75rem;'>
                {t("welcome_sub")}
            </div>
            <h1 style='font-family:"IBM Plex Sans",sans-serif; font-size:2.25rem;
                       font-weight:600;
                       background:linear-gradient(135deg,#d4844a,#9b59b6,#c8729a);
                       -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                       background-clip:text;
                       margin:0 0 1rem; letter-spacing:-0.02em; line-height:1.25;'>
                {t("welcome_h1")}
            </h1>
            <p style='font-size:0.95rem; color:#5a4a72; line-height:1.8;
                      max-width:800px; margin:0 0 2rem;'>
                {t("welcome_body")}
            </p>
        </div>
    """, unsafe_allow_html=True)

    def info_card(title, body):
        return (
            f"<div style='background:#13101a; border:1px solid #2a1f3d;"
            f" border-radius:4px; padding:1.25rem; margin-bottom:8px;'>"
            f"<div style='font-family:\"IBM Plex Mono\",monospace; font-size:0.65rem;"
            f" color:#4a3a5a; letter-spacing:0.1em; text-transform:uppercase;"
            f" margin-bottom:0.5rem;'>{title}</div>"
            f"<div style='font-size:0.88rem; color:#6a5a8a; line-height:1.6;'>{body}</div>"
            f"</div>"
        )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(info_card(t("card_model"), t("card_model_body")), unsafe_allow_html=True)
        st.markdown(info_card(t("card_who"),   t("card_who_body")),   unsafe_allow_html=True)
    with col2:
        st.markdown(info_card(t("card_conn"),  t("card_conn_body")),  unsafe_allow_html=True)
        st.markdown(info_card(t("card_start"), t("card_start_body")), unsafe_allow_html=True)


# ── Chat view ──────────────────────────────────────────────
else:
    active_key = st.session_state.active
    meta       = FEATURES_META[active_key]
    history    = st.session_state.messages[active_key]
    is_therapy = meta.get("therapy", False)
    # Voice is always-on for the head feature (no toggle needed)
    use_voice  = (active_key == "head") and RECORDER_OK and WHISPER_OK

    # ── Header ──────────────────────────────────────────────
    col_title, col_clear = st.columns([5, 1])

    with col_title:
        st.markdown(f"""
            <div class="{rtl_class}" style='padding:1.5rem 0 0.75rem;'>
                <div style='font-family:"IBM Plex Mono",monospace; font-size:0.65rem;
                            color:#4a3a5a; letter-spacing:0.1em; text-transform:uppercase;
                            margin-bottom:0.35rem;'>
                    {meta['icon']}  {t("active_feature")}
                </div>
                <h2 style='font-family:"IBM Plex Sans",sans-serif; font-size:1.4rem;
                           font-weight:600;
                           background:linear-gradient(135deg,#d4844a,#9b59b6,#c8729a);
                           -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                           background-clip:text; margin:0; letter-spacing:-0.02em;'>
                    {t(meta["name"])}
                </h2>
            </div>
        """, unsafe_allow_html=True)

    with col_clear:
        st.markdown("<div style='padding-top:1.75rem;'>", unsafe_allow_html=True)
        if history:
            if st.button(t("clear"), key="clear_btn"):
                st.session_state.messages[active_key] = []
                st.session_state.tts_audio             = None
                st.session_state.tts_autoplay          = False
                st.session_state.pending_voice         = None
                st.session_state.last_audio_hash       = None
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Disclaimer ──────────────────────────────────────────
    st.markdown(f"""
        <div class="{rtl_class}" style='background:#13101a; border:1px solid #2a1f3d;
                    border-left:3px solid #3a2d52; border-radius:4px;
                    padding:0.6rem 1rem; font-family:"IBM Plex Mono",monospace;
                    font-size:0.75rem; color:#5a4a72; margin-bottom:0.75rem;'>
            {t(meta["disc"])}
        </div>
    """, unsafe_allow_html=True)

    # ── Letter banner ────────────────────────────────────────
    if meta["letter"]:
        st.markdown(f"""
            <div style='background:#1a1025; border:1px solid #4a2060;
                        border-left:3px solid #9b59b6; border-radius:4px;
                        padding:0.75rem 1rem; margin-bottom:0.75rem;
                        font-family:"IBM Plex Mono",monospace;
                        font-size:0.75rem; color:#9b59b6;'>
                {t("letter_banner")}
            </div>
        """, unsafe_allow_html=True)

    # ── Chat history ─────────────────────────────────────────
    assistant_avatar = LOGO_URI if LOGO_URI else "💭"
    for msg in history:
        with st.chat_message(
            msg["role"],
            avatar=assistant_avatar if msg["role"] == "assistant" else None,
        ):
            st.markdown(
                f'<div class="{rtl_class}">{msg["content"]}</div>',
                unsafe_allow_html=True,
            )

    # ════════════════════════════════════════════════════════
    # INPUT AREA — mic row (head only) + chat input
    # The mic sits in a styled bar flush above st.chat_input
    # so they read as one unified input zone.
    # ════════════════════════════════════════════════════════

    if use_voice:
        # ── Mic bar: styled to blend with the chat input bar ─
        st.markdown(f"""
            <div style='
                background:#13101a;
                border-top:1px solid #2a1f3d;
                border-left:1px solid #2a1f3d;
                border-right:1px solid #2a1f3d;
                border-radius:4px 4px 0 0;
                padding:0.45rem 0.9rem;
                display:flex;
                align-items:center;
                gap:0.6rem;
                margin-bottom:-2px;
            '>
                <span style='font-family:"IBM Plex Mono",monospace;
                             font-size:0.68rem; color:#4a3a5a; letter-spacing:0.05em;'>
                    {t("record_hint")}
                </span>
            </div>
        """, unsafe_allow_html=True)

        # Place the recorder widget in a tight column so it
        # doesn't stretch across the full width
        mic_col, _ = st.columns([1, 11])
        with mic_col:
            audio_bytes = audio_recorder(
                text="",
                recording_color="#c8729a",
                neutral_color="#4a3a5a",
                icon_size="lg",
                key="mic_recorder",
            )

        if audio_bytes:
            audio_hash = hashlib.md5(audio_bytes).hexdigest()
            if audio_hash != st.session_state.last_audio_hash:
                st.session_state.last_audio_hash = audio_hash
                with st.spinner(t("transcribing")):
                    result = transcribe_audio(audio_bytes, lang_code)
                if result and result.strip():
                    st.session_state.pending_voice = result.strip()
                    st.success(f"✅ {result.strip()}")

    elif active_key == "head":
        # Whisper/recorder not installed — show a small warning
        st.warning(t("voice_unavail"))

    # ── Chat text input (always shown) ───────────────────────
    user_input = st.chat_input(
        t(meta["ph"]),
        key=f"chat_input_{active_key}",
    )

    # Text typed by the user takes priority; otherwise use voice transcription
    final_input = user_input or st.session_state.pending_voice

    # ════════════════════════════════════════════════════════
    # SEND MESSAGE TO LLM
    # ════════════════════════════════════════════════════════
    if final_input and final_input.strip():
        final_input = final_input.strip()
        st.session_state.pending_voice = None

        # Add user message to history
        st.session_state.messages[active_key].append(
            {"role": "user", "content": final_input}
        )

        # Display user message immediately
        with st.chat_message("user"):
            st.markdown(
                f'<div class="{rtl_class}">{final_input}</div>',
                unsafe_allow_html=True,
            )

        # ── RAG retrieval (rights feature only) ──────────────
        rag_context = ""
        rag_sources = []

        if active_key == "rights":
            rag_col = load_rag_collection()
            if rag_col is None:
                st.warning(t("rag_no_db"))
            else:
                # List the PDF files being searched
                all_meta   = rag_col.get(include=["metadatas"])["metadatas"]
                file_names = sorted({m["source"] for m in all_meta})

                with st.spinner(f'{t("rag_searching")}…'):
                    # Show which files we're searching
                    files_display = " · ".join(
                        f.replace(".pdf", "") for f in file_names
                    )
                    st.markdown(f"""
                        <div style='font-family:"IBM Plex Mono",monospace;
                                    font-size:0.68rem; color:#4a3a5a;
                                    margin-bottom:0.3rem; padding:0.3rem 0;'>
                            🔍 {t("rag_searching")}: <span style='color:#6a5a8a;'>{files_display}</span>
                        </div>
                    """, unsafe_allow_html=True)

                    rag_context, rag_sources = retrieve_legal_context(
                        final_input, rag_col
                    )

                if not rag_sources:
                    st.markdown(f"""
                        <div style='font-family:"IBM Plex Mono",monospace;
                                    font-size:0.68rem; color:#5a4a20; margin-bottom:0.3rem;'>
                            {t("rag_no_results")}
                        </div>
                    """, unsafe_allow_html=True)

        # ── Build messages (with or without RAG context) ──────
        if active_key == "rights" and rag_context:
            api_messages = build_messages_with_rag(
                active_key,
                st.session_state.messages[active_key],
                rag_context,
            )
        else:
            api_messages = build_messages(
                active_key,
                st.session_state.messages[active_key],
            )

        # ── Call Ollama ───────────────────────────────────────
        with st.chat_message("assistant", avatar=LOGO_URI if LOGO_URI else "💎"):
            with st.spinner(t("thinking")):
                try:
                    resp = requests.post(
                        "http://localhost:11434/api/chat",
                        json={
                            "model":    "gemma4:e2b",
                            "messages": api_messages,
                            "stream":   False,
                            "options":  {"num_ctx": 4096, "temperature": 0.5},
                        },
                        timeout=180,
                    )

                    data = resp.json()

                    if "error" in data:
                        st.error(f"❌ Ollama Error: {data['error']}")
                        st.info("Make sure you ran: `ollama run gemma4:e2b`")
                    else:
                        answer = data.get("message", {}).get("content", "")

                        if not answer:
                            st.error("❌ Empty response from model")
                        else:
                            # Clean thinking tags
                            if "<think>" in answer:
                                answer = answer.split("</think>")[-1].strip()
                            elif "<|channel>thought" in answer:
                                answer = answer.split("<|end|>")[-1].strip()

                            st.markdown(
                                f'<div class="{rtl_class}">{answer}</div>',
                                unsafe_allow_html=True,
                            )

                            # ── Source citations (rights + RAG) ──
                            if active_key == "rights" and rag_sources:
                                source_items = "  ·  ".join(
                                    f'{t("rag_source")}: <span style="color:#9b59b6;">'
                                    f'{src["file"].replace(".pdf","")}</span> '
                                    f'{t("rag_page")}{src["page"]}'
                                    for src in rag_sources
                                )
                                st.markdown(f"""
                                    <div style='
                                        margin-top:0.6rem;
                                        padding:0.35rem 0.75rem;
                                        border-left:2px solid #3a2d52;
                                        font-family:"IBM Plex Mono",monospace;
                                        font-size:0.68rem;
                                        color:#5a4a72;
                                        line-height:1.7;
                                    '>
                                        {source_items}
                                    </div>
                                """, unsafe_allow_html=True)

                            st.session_state.messages[active_key].append(
                                {"role": "assistant", "content": answer}
                            )

                            # Text-to-Speech — head feature only
                            if is_therapy and TTS_OK:
                                with st.spinner(t("gen_audio")):
                                    audio_data = speak_text(answer, is_therapy=True)
                                if audio_data:
                                    st.session_state.tts_audio    = audio_data
                                    st.session_state.tts_autoplay = True
                                else:
                                    st.warning(t("audio_fail"))

                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to Ollama. Is it running?")
                except requests.exceptions.Timeout:
                    st.error(t("timeout_err"))
                except Exception as e:
                    st.error(f"Error: {str(e)}")

    # ════════════════════════════════════════════════════════
    # TTS PLAYER — shown after head feature responses
    # ════════════════════════════════════════════════════════
    if TTS_OK and st.session_state.tts_audio:
        st.markdown("""
            <div style='height:1px; background:#2a1f3d; margin:0.75rem 0;'></div>
        """, unsafe_allow_html=True)

        st.audio(
            st.session_state.tts_audio,
            format="audio/wav",
            autoplay=st.session_state.tts_autoplay,
        )
        st.session_state.tts_autoplay = False