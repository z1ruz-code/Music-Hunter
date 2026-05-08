from pathlib import Path
from yandex_music import Client

from banner import print_banner
from cache_manager import load_cache_path, save_cache_path, find_yandex_music_cache
from music_processor import copy_with_rename

def main() -> None:
    print_banner()

    project_dir = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()
    music_folder = project_dir / "music"

    cache = load_cache_path()
    if cache:
        print(f"Используем путь из конфига: {cache}")
    else:
        print("Поиск кеша Яндекс.Музыки...")
        cache = find_yandex_music_cache()
        if cache is None:
            print("Не удалось найти кеш. Убедитесь, что песни скачаны.")
            return
        save_cache_path(cache)
        print(f"Найден кеш: {cache}")
        print("Путь сохранён в конфиг")

    print()

    try:
        client = Client().init()
    except Exception:
        print("Не удалось инициализировать клиент Яндекс.Музыки. Файлы будут скопированы без переименования.")
        client = None

    copy_with_rename(cache, music_folder, client)

if __name__ == "__main__":
    main()