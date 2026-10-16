from dataclasses import dataclass, asdict
from pathlib import Path
import json
import os
import sys

def config_path() -> Path:
    if sys.platform == 'win32':
        base = Path(os.environ.get('APPDATA', Path.home() / 'AppData' / 'Roaming'))
    elif sys.platform == 'darwin':
        base = Path.home() / 'Library' / 'Application Support'
    else:
        base = Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config'))
    return base / 'LocalAIAssistant' / 'settings.json'

@dataclass
class Settings:
    model: str = 'gemma3:4b'
    endpoint: str = 'http://127.0.0.1:11434'
    always_on_top: bool = True
    opacity: int = 100
    watch_interval: int = 15

    def __post_init__(self):
        for name, low, high, default in (('opacity', 30, 100, 100),
                                          ('watch_interval', 5, 120, 15)):
            value = getattr(self, name)
            if type(value) is not int:
                value = default
            setattr(self, name, max(low, min(high, value)))

    @classmethod
    def load(cls):
        try:
            data = json.loads(config_path().read_text(encoding='utf-8'))
            return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
        except (OSError, ValueError, TypeError):
            return cls()

    def save(self):
        path = config_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(self), indent=2), encoding='utf-8')
