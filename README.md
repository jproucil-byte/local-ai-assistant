# Local AI Assistant — v0.1.0 Alpha

Privacy-first, local desktop AI advisor. Cross-platform Python/PySide6 foundation; Windows-first testing.

## Features
- Floating, always-on-top dark chat window
- Ollama local chat (no cloud API)
- Explicit screenshot capture of the primary display, attached to the next message
- Local model and endpoint settings
- Window opacity from 30% to 100%, with a preview in Settings
- Optional screen watch with Start/Stop and a separate latest-analysis panel
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

### Daily use on Windows

After setup, double-click `Start-Assistant.cmd`. It starts the local Ollama
service if needed, then opens the assistant without a separate Python console.
The configured model must already be downloaded (`ollama pull gemma3:4b`).

Write your question and click **Send**. For screen analysis, click **Capture
screen**, then send a question about the captured screen. Use the gear button
to change the model or local endpoint. Answers follow the language of your question.
After capture, the green **Remove screenshot** button indicates that one snapshot
is attached. Click it to remove the attachment. Sending a message consumes the
attachment; capture again to share an updated screen.
The local endpoint (`http://127.0.0.1:11434`) is the address of the Ollama service
on this computer, and normally does not need to be changed.

### Window opacity and screen watch

In Settings, use **Window opacity** to preview and save transparency (30–100%).
Closing Settings without saving restores the previous opacity. The whole window,
including text, becomes translucent; 100% restores normal readability.

Click **Start screen watch** to repeatedly capture and analyze the primary display.
The button turns green and changes to **Stop screen watch**. The latest summary
appears in a separate panel with a completion time in the status above it.
Settings controls the pause after each completed analysis (5–120 seconds, default
15 seconds). Actual refresh time is inference time plus this pause, not a video feed.
There is only one model request at a time, so slow requests never build up a queue.
Sending a chat question while watch is enabled attaches a fresh screen snapshot.

**Stop screen watch** immediately prevents further automatic captures. An already
submitted analysis may finish locally, but its result is discarded. Watch is always
off when the app starts; saving settings, clearing chat, or closing the window stops
it. Capture or inference errors also stop watch. If you close during an active model
request, the window hides and exits when that request finishes (up to its timeout).
The whole primary display is captured, including this app if visible. Other displays
are not included, and no exclusion or redaction is implemented yet.

See [model suggestions](docs/MODEL_RECOMMENDATIONS.md) for alternative local vision
models. Settings lists suggestions, not installed models. Download a model with
`ollama pull <model>` before selecting it; you can also type a custom model name.

## Privacy
Screenshots are captured when clicking **Capture screen**, while an explicitly
started screen watch is running, or when sending a question during screen watch.
They are held in memory and sent to the configured loopback Ollama endpoint.
Automatic analyses replace the latest summary instead of filling chat history.
No screenshot or chat transcript is intentionally written to disk by this app.
Settings are stored per-user; screen watch is never enabled automatically on restart.

## Limitations
First display only. No persistent chat history, global hotkey, tray icon, autonomous
web browsing, or action engine yet. Screen watch uses periodic still images. UI
logic is tested with simulated captures; real display and transparency behavior
can vary by desktop environment.

## Tests
```bash
python -m unittest discover -s tests -v
```

See [technical specification](docs/TECHNICAL_SPECIFICATION.md).
