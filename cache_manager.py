import json
from pathlib import Path
from typing import Optional

CONFIG_FILE = "music_cache_path.json"

def load_cache_path() -> Optional[Path]:
    path = Path(CONFIG_FILE)
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        cache_path = Path(data["yandex_music_cache"])
        if cache_path.exists():
            return cache_path
    except (json.JSONDecodeError, KeyError, OSError):
        pass
    return None

def save_cache_path(cache_path: Path) -> None:
    data = {"yandex_music_cache": str(cache_path.resolve())}
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def find_yandex_music_cache() -> Optional[Path]:
    base = Path.home() / "AppData" / "Local" / "Packages"
    if not base.is_dir():
        return None
    try:
        yandex_dir = next(
            (p for p in base.iterdir() if p.is_dir() and "yandex" in p.name.lower() and "music" in p.name.lower()),
            None
        )
    except PermissionError:
        return None
    if yandex_dir is None:
        return None
    music_cache = yandex_dir / "LocalState" / "Music"
    if not music_cache.is_dir():
        return None
    try:
        songs_dir = next((sub for sub in music_cache.iterdir() if sub.is_dir()), None)
    except PermissionError:
        return None
    return songs_dir