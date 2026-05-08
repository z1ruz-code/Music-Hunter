import shutil
from pathlib import Path
from typing import Optional, Tuple

from yandex_music import Client

def _get_track_info(track_id: int, client: Client) -> Tuple[Optional[str], Optional[str]]:
    try:
        track = client.tracks([track_id])[0]
        if track and track.artists:
            artist = track.artists[0].name
            title = track.title
            return artist, title
    except Exception:
        pass
    return None, None

def copy_with_rename(src: Path, dst: Path, client: Optional[Client]) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        if not (item.is_file() and item.suffix.lower() == '.mp3'):
            continue

        target = dst / item.name
        if target.exists():
            print(f"{item.stem} - существует")
            continue

        if client is not None:
            artist, title = _get_track_info(item.stem, client)
            if artist and title:
                new_name = f"{artist} - {title}.mp3"
                new_target = dst / new_name
                if new_target.exists():
                    print(f"{item.stem} - уже существует (как {new_name})")
                    continue
                shutil.copy2(item, new_target)
                print(f"{item.stem} - {artist.lower()} {title.lower()}")
                continue

        shutil.copy2(item, target)
        print(f"{item.stem} - скопировано")