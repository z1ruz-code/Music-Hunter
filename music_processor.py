import shutil
from pathlib import Path
from typing import Optional, Tuple

from yandex_music import Client
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, APIC, PictureType
from mutagen.mp3 import MP3
import requests


def _get_track_info(track_id: int, client: Client) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[int], Optional[bytes]]:
    try:
        track = client.tracks([track_id])[0]
        if track and track.artists:
            artist = track.artists[0].name
            title = track.title
            album = track.albums[0].title if track.albums else None
            year = track.albums[0].year if track.albums else None
            cover_url = None
            if track.albums and track.albums[0].cover_uri:
                cover_url = track.albums[0].cover_uri.replace('%%', '400x400')
            cover_data = None
            if cover_url:
                try:
                    cover_data = requests.get(cover_url).content
                except Exception:
                    pass
            return artist, title, album, year, cover_data
    except Exception:
        pass
    return None, None, None, None, None


def _write_id3_tags(file_path: Path, title: str, artist: str, album: str, year: int, cover_data: bytes) -> None:
    try:
        audio = MP3(file_path, ID3=ID3)
        if audio.tags is None:
            audio.add_tags()
        audio.tags.add(TIT2(encoding=3, text=title))
        audio.tags.add(TPE1(encoding=3, text=artist))
        if album:
            audio.tags.add(TALB(encoding=3, text=album))
        if year:
            audio.tags.add(TDRC(encoding=3, text=str(year)))
        if cover_data:
            audio.tags.add(APIC(
                encoding=3,
                mime='image/jpeg',
                type=PictureType.COVER_FRONT,
                desc='Cover',
                data=cover_data
            ))
        audio.save(v2_version=3)
    except Exception:
        pass


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
            artist, title, album, year, cover_data = _get_track_info(item.stem, client)
            if artist and title:
                new_name = f"{artist} - {title}.mp3"
                new_target = dst / new_name
                if new_target.exists():
                    print(f"{item.stem} - уже существует (как {new_name})")
                    continue
                shutil.copy2(item, new_target)
                _write_id3_tags(new_target, title, artist, album, year, cover_data)
                print(f"{item.stem} - {artist.lower()} {title.lower()}")
                continue
        shutil.copy2(item, target)
        print(f"{item.stem} - скопировано")