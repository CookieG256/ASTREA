"""Organize named enemy animation sheets into assets/sprites/inimigos."""

import argparse
import os
import re
import shutil
import unicodedata
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_SOURCE = PROJECT_ROOT / "inimigos"
DEFAULT_DESTINATION = PROJECT_ROOT / "assets" / "sprites" / "inimigos"
ANIMATION_SUFFIX = re.compile(
    r"[_\-\s]+(idle|walk(?:ing)?|movement|movemen|move|attack\d*|death\d*|die|hurt|take[_\-\s]?damage)$",
    re.IGNORECASE,
)


def slug(value):
    normalized = unicodedata.normalize("NFKD", value)
    normalized = normalized.encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"[^a-z0-9]+", "_", normalized).strip("_")


def enemy_name_from_file(filename):
    stem = Path(filename).stem
    match = ANIMATION_SUFFIX.search(stem)
    if not match:
        return None
    name = stem[:match.start()].strip(" _-")
    name = re.sub(r"^(?:enemies|enemy)[_-]+", "", name, flags=re.IGNORECASE)
    return slug(name) or None


def unique_destination(path, reserved):
    candidate = path
    number = 2
    while os.path.exists(candidate) or str(candidate) in reserved:
        candidate = path.with_name(f"{path.stem} ({number}){path.suffix}")
        number += 1
    reserved.add(str(candidate))
    return candidate


def organize(source, destination, apply=False):
    source = Path(source).expanduser().resolve()
    destination = Path(destination).expanduser().resolve()
    if not source.is_dir():
        raise FileNotFoundError(f"Diretório de origem não encontrado: {source}")

    planned_moves = []
    reserved_destinations = set()
    destination_inside_source = source != destination and source in destination.parents
    for current_root, directories, filenames in os.walk(source):
        current_path = Path(current_root).resolve()
        if destination_inside_source:
            directories[:] = [
                name for name in directories
                if os.path.commonpath(
                    (str((current_path / name).resolve()), str(destination))
                ) != str(destination)
            ]
        directories.sort()
        for filename in sorted(filenames):
            if not filename.lower().endswith(".png"):
                continue
            enemy_name = enemy_name_from_file(filename)
            if not enemy_name:
                continue
            source_file = Path(current_root) / filename
            if source == destination:
                relative_parent = source_file.parent.relative_to(source)
                if relative_parent.parts == (enemy_name,):
                    continue
            destination_file = unique_destination(
                destination / enemy_name / filename,
                reserved_destinations,
            )
            planned_moves.append((source_file, destination_file))

    for source_file, destination_file in planned_moves:
        print(f"{'MOVER' if apply else 'SIMULAR'}: {source_file} -> {destination_file}")
        if apply:
            os.makedirs(destination_file.parent, exist_ok=True)
            shutil.move(str(source_file), str(destination_file))

    print(f"{len(planned_moves)} arquivo(s) {'movido(s)' if apply else 'encontrado(s)'}.")
    if not apply:
        print("Simulação apenas. Use --apply para mover os arquivos.")
    return len(planned_moves)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        default=str(DEFAULT_SOURCE),
        help="Pasta extraída dos sprites (padrão: ./inimigos)",
    )
    parser.add_argument(
        "--destination",
        default=str(DEFAULT_DESTINATION),
        help="Pasta de destino organizada",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Executa os movimentos; sem esta opção só mostra a simulação",
    )
    args = parser.parse_args()
    organize(args.source, args.destination, apply=args.apply)


if __name__ == "__main__":
    main()
