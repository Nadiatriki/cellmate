# CellMate — Prisoner AI Companion
### *Locked in. Not locked out.*

> Built for the **Gemma 4 Good Hackathon 2026**
> Powered by **Gemma 4 E2B** · Runs 100% offline · Zero cost · Zero internet required

---

CellMate is an offline AI companion designed for incarcerated individuals — one of the most digitally excluded populations on earth. It runs entirely on-device using Ollama and Gemma 4 E2B, with no internet connection, no cloud, and no ongoing cost.

---

## Features

| Feature | Description |
|---|---|
| ⚖ **Know Your Rights** | Legal information grounded in real documents via RAG — cites sources |
| 🕮 **Learn Something New** | Patient educational tutor, starts from the basics |
| 💭 **Keep Your Head Right** | Mental wellness companion with voice input and text-to-speech |
| 🕊 **Prepare For The Gate** | Reintegration coach — CVs, housing, budgeting, interviews |
| ✉ **Write Home** | Guided letter-writing companion, helps find their own words |

---

## Why Offline?

Most prisons have no internet access. CellMate is designed from the ground up to work without it:

- **No API calls to the cloud** — Ollama runs the model locally
- **No data leaves the device** — conversations stay on-machine
- **No subscription or cost** — free to deploy at any scale
- **No setup per user** — one install, always available

---

## Tech Stack

| Component | Technology |
|---|---|
| LLM | Gemma 4 E2B via [Ollama](https://ollama.com) |
| Embeddings | `nomic-embed-text` via Ollama |
| Vector DB | ChromaDB (persistent, on-disk) |
| PDF Parsing | PyMuPDF (`fitz`) |
| Speech-to-Text | faster-whisper (Whisper tiny, CPU) |
| Text-to-Speech | pyttsx3 (fully offline) |
| UI | Streamlit |
| Languages | English · Français · العربية |

---

## Project Structure

```
CellMate/
├── cellmate.py              # Main Streamlit application
├── index_legal_docs.py      # One-time RAG indexer — run before first launch
├── requirements.txt         # Python dependencies
├── README.md                # This file
├── .gitignore               # Excludes generated files from git
├── legal_docs/              # legal PDFs here 
│   ├── doc1.pdf
│   └── ...
├── chroma_db/               # Auto-created by indexer — not committed to git
├── logo.png                 # CellMate logo
└── fonts/                   # Optional — IBM Plex fonts (not committed to git)
    ├── IBMPlexMono-Regular.ttf
    └── IBMPlexSans-Regular.ttf
```

---

## Setup & Installation

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com/download) installed and running

---

### Step 1 — Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/cellmate.git
cd cellmate
```

---

### Step 2 — Install Python dependencies

```bash
pip install -r requirements.txt
```

> **Note on voice packages:** `faster-whisper` and `pyttsx3` are optional. If you skip them, CellMate runs fine — the voice feature in "Keep Your Head Right" simply won't appear.

---

### Step 3 — Pull the Ollama models

```bash
# The main LLM
ollama pull gemma4:e2b

# The embedding model (for RAG legal search)
ollama pull nomic-embed-text
```

Make sure Ollama is running before starting the app:

```bash
ollama serve
```

---

### Step 4 — Add your legal documents

Add any legal PDF files into the `legal_docs/` folder:

```
legal_docs/
├── Jailhouse Lawyers Handbook 2021.pdf
├── know-your-rights-prisoner.pdf
└── Prisoners Rights ACLU.pdf
```

Then run the indexer **once** (and again any time you add new PDFs):

```bash
python index_legal_docs.py
```

Expected output:

```
✅  nomic-embed-text is ready
📂  Found 3 PDF(s) in legal_docs/

  📄  Indexing: Jailhouse Lawyers Handbook 2021.pdf
       📝  184 pages → 1477 chunks
       ✅  Batch 1: 50 chunks indexed
       ...

🎉  Done. ChromaDB now holds 1623 total chunks.
```

> ⚠️ **Important:** Do not use the app while indexing is running. Both the app and the indexer call Ollama, and they will conflict on a single machine. Wait for the indexer to finish completely before starting Streamlit.

> ℹ️ The indexer is smart — it hashes each file and skips PDFs that haven't changed, so re-running it after adding one new document only processes the new file.

---

### Step 5 — Launch CellMate

```bash
streamlit run cellmate.py
```

Open your browser at `http://localhost:8501`

The sidebar will confirm everything is ready:

```
🟢  Gemma 4 E2B · running
🟢  Legal index ready (1623 chunks)
🟢  All voice packages ready
```

---

## How RAG Works in the Legal Feature

When a user asks a question in **Know Your Rights**:

1. The query is embedded with `nomic-embed-text`
2. ChromaDB retrieves the top 4 most relevant chunks from your legal PDFs
3. The chunks are injected into Gemma's system prompt as grounded context
4. The answer is shown with a citation line beneath it:

```
📄 Source: Jailhouse Lawyers Handbook 2021 p.47 · Prisoners Rights ACLU p.3
```

If no relevant chunks are found above the relevance threshold, the model answers from general knowledge and says so clearly.

---

## Voice Feature (Keep Your Head Right)

The mental wellness feature has always-on voice support — no toggle needed:

- **Mic bar** appears directly above the chat input whenever you open this feature
- Click mic → speak → click again to stop
- Transcription via faster-whisper (Whisper tiny, runs fully on CPU)
- CellMate's response is read aloud automatically via pyttsx3
- Works in English, French, and Arabic

---

## Languages

CellMate is fully translated — UI, prompts, disclaimers, and placeholders:

| Language | Code | Direction |
|---|---|---|
| English | `en` | LTR |
| Français | `fr` | LTR |
| العربية | `ar` | RTL |

To add a new language, add entries to `LANGUAGES` and `UI` in `cellmate.py`.

---

## Adding More Legal Documents Later

1. Drop new PDFs into `legal_docs/`
2. **Stop the Streamlit app first**
3. Run `python index_legal_docs.py` — only new files are processed
4. Restart the app

> **Windows note:** Always stop the app before re-indexing. Streamlit holds ChromaDB file handles open. If `rmdir` is blocked, run `taskkill /F /IM python.exe` first.

---

## Troubleshooting

**`⚠ Legal index missing`** shown in sidebar
→ The indexer hasn't been run yet, or ran while the app was open.
→ Stop the app, run `python index_legal_docs.py`, wait for it to finish, then restart.

**`Response timed out`** while indexer is running
→ Expected — don't use the app during indexing. Both share Ollama on one machine.

**Indexer finishes but chunk count is 0**
→ Stop the app, delete `chroma_db/`, re-run the indexer.
→ Windows: `taskkill /F /IM python.exe` then `rmdir /s /q chroma_db`

**Voice mic doesn't appear**
→ Install: `pip install faster-whisper pyttsx3 audio-recorder-streamlit`
→ Mic only appears in the "Keep Your Head Right" feature.

**Arabic text displays left-to-right**
→ Select العربية from the language dropdown. RTL styling is applied per message via CSS.

---

## What's Not in This Repo

For legal and privacy reasons, the following are excluded from git:

- `chroma_db/` — generated locally by the indexer
- `fonts/` — download IBM Plex from [Google Fonts](https://fonts.google.com/specimen/IBM+Plex+Mono)

---

## .gitignore

```gitignore
# Generated by indexer — rebuild locally
chroma_db/

# Legal PDFs — add your own
legal_docs/

# Optional local assets
logo.png
fonts/

# Python
__pycache__/
*.pyc
.env

# Streamlit
.streamlit/secrets.toml
```

---

## Pushing to GitHub — Full Steps

```bash
# 1. Initialize git in your project folder
git init

# 2. Create .gitignore (copy from above), then stage it first
git add .gitignore
git commit -m "Add .gitignore"

# 3. Stage your project files
git add cellmate.py index_legal_docs.py requirements.txt README.md
git commit -m "feat: CellMate v2.1 — offline prisoner AI companion"

# 4. Create a new empty repo on github.com, then connect it
git remote add origin https://github.com/YOUR_USERNAME/cellmate.git
git branch -M main
git push -u origin main
```

> Make sure `chroma_db/` and `legal_docs/` are in `.gitignore` **before** your first `git add .` — once files are tracked by git, `.gitignore` won't remove them automatically.

---

## License

MIT — free to use, modify, and deploy.

---

## Built With

- [Ollama](https://ollama.com) — local LLM runtime
- [Gemma 4](https://ai.google.dev/gemma) — Google's open model, built for edge deployment
- [Streamlit](https://streamlit.io) — UI framework
- [ChromaDB](https://www.trychroma.com) — local vector database
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) — offline speech recognition
- [PyMuPDF](https://pymupdf.readthedocs.io) — PDF text extraction

---

*CellMate was built for the Gemma 4 Good Hackathon 2026 with one goal: give people behind bars the same access to information and support that everyone else takes for granted.*
