# Technical specification — Local AI Assistant

Version: 0.1.0-alpha. Target: Windows 11 first, Linux/macOS adapters later.

## Purpose
Local, privacy-first desktop assistant with two planned modes: **Advisor** (observe and explain) and **Operator** (execute explicit, approved actions). Version 0.1 implements Advisor only.

## Architecture
```
PySide6 Floating UI
  -> Application Controller (Qt worker thread)
     -> Model Adapter: Ollama localhost /api/chat
     -> Screen Adapter: MSS + Pillow -> PNG in RAM
     -> Settings: per-user JSON
     -> Future: OCR and accessibility adapters
     -> Future: opt-in Web tool and SQLite memory
     -> Future: Policy Engine -> Action Executor -> OS-specific adapters
```

## Current behavior
1. Qt UI runs on the main thread; blocking inference runs on QThread.
2. Screenshots are captured on explicit request or during explicitly started screen
   watch. Frames remain in memory; watch results replace a separate summary panel.
3. Model communication is restricted to HTTP loopback.
4. OS actions are not implemented.
5. No persistent chat or screen history.
6. Window opacity is persisted (30–100%); the settings dialog provides a reversible preview.
7. Screen watch always starts off. A single-shot Qt timer schedules the next frame
   5–120 seconds after model completion. Chat and observation share one worker slot.
   No inference queue or overlapping captures are created. Chat during watch uses a
   fresh frame; observation requests use only the system prompt and current frame.
8. Stop, Clear, settings save, errors and window close stop automatic captures.
   Session generations discard late results from a stopped or restarted watch.
   In-flight HTTP requests can finish but cannot re-enable watch. Close waits for
   worker cleanup without leaving background observation enabled.

## Operator security requirements
- Default-deny, task-scoped capabilities and typed action arguments.
- Show planned actions and file diffs before approval.
- Separate confirmation for destructive, external, privileged or sensitive operations.
- Executor-enforced emergency stop, action audit and optional rollback.
- Treat web pages, files and UI text as untrusted data.
- Screen exclusions and redaction for sensitive content.

## Platform adapters
- Windows: UI Automation and native shortcuts.
- Linux: AT-SPI, Wayland portal restrictions.
- macOS: Screen Recording and Accessibility permissions.
- Shared Qt UI, model API, policy and conversation logic.

## Roadmap
- **0.1 Alpha:** floating UI, local chat, explicit screenshot, configuration; Windows hardware testing pending.
- **0.2 Observer:** global shortcut, tray, multiple displays, active window, OCR and exclusions.
- **0.3 Knowledge:** SQLite history, optional search provider and offline fallback.
- **0.4 Operator:** typed action registry, approval UI, emergency stop, audit.
- **0.5 Beta:** packaging, diagnostics and cross-hardware tests.

## Risks
Vision inference may be slow with 8 GB VRAM; capture can expose secrets. Local AI does not guarantee that the separately installed Ollama runtime makes no network connections.
