# Local AI Assistant — v0.1.0 Alpha

Privacy-first, local desktop AI advisor. Cross-platform Python/PySide6 foundation; Windows-first testing.

## Features
- Floating, always-on-top dark chat window
- Ollama local chat (no cloud API)
- Explicit screenshot capture of the primary display, attached to the next message
- Local model and endpoint settings
- Read-only advisor mode: **no computer control, no autonomous browsing**

## Requirements
- Python 3.11 or 3.12
- Ollama installed and running locally
- A vision-capable model, e.g. `gemma3:4b`

## Setup (Windows PowerShell)
```powershell
git clone https://github.com/jproucil-byte/local-ai-assistant.git
cd local-ai-assistant
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
ollama pull gemma3:4b
python -m local_ai_assistant.main
```

On Linux/macOS use `python3 -m venv .venv` and `source .venv/bin/activate`.

## Privacy
Screenshots are captured only when clicking **Capture screen**, held in memory, and sent to the configured loopback Ollama endpoint on the next message. No screenshot or chat transcript is intentionally written to disk by this app. Settings are stored per-user.

## Limitations
First display only. No persistent chat history, global hotkey, tray icon, autonomous web browsing, or action engine yet. GUI has not been tested on real Windows hardware.

## Tests
```bash
python -m unittest discover -s tests -v
```

See [technical specification](docs/TECHNICAL_SPECIFICATION.md).
