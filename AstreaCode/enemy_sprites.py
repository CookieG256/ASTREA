"""Discover and load enemy animation sprite sheets from the sprite library."""

import os
import re
import unicodedata
from pathlib import Path

import pygame


_PROJECT_ROOT = Path(__file__).resolve().parent
_DEFAULT_SPRITE_ROOT = _PROJECT_ROOT / "assets" / "sprites"
_ANIMATION_SUFFIX = re.compile(
    r"[_\-\s]+(idle|walk(?:ing)?|movement|movemen|move|attack\d*|death\d*|die|hurt|take[_\-\s]?damage)$",
    re.IGNORECASE,
)
_STATE_NAMES = {
    "idle": "idle",
    "walk": "walk",
    "walking": "walk",
    "movement": "walk",
    "movemen": "walk",
    "move": "walk",
    "death": "death",
    "die": "death",
    "hurt": "hurt",
    "take_damage": "hurt",
}
_TYPE_SPRITE_CANDIDATES = {
    "melee": ("orc", "soldier"),
    "tank": ("blood-monster-a", "orc"),
    "ranged": ("skeleton1", "skeleton"),
    "support": ("vampire", "priest1"),
    "mage": ("vampire", "skeleton2"),
    "summoner": ("demon-a", "vampire"),
    "assassin": ("skeleton2", "orc"),
    "bomber": ("blood-monster-a", "demon-a"),
    "trapper": ("skeleton2", "vampire"),
    "duelist": ("soldier", "skeleton1"),
}


def _slug(value):
    normalized = unicodedata.normalize("NFKD", str(value or ""))
    normalized = normalized.encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")


def _parse_animation_path(path):
    stem = re.sub(r"\s+\(\d+\)$", "", path.stem)
    match = _ANIMATION_SUFFIX.search(stem)
    if not match:
        return None

    enemy_name = stem[:match.start()].strip(" _-")
    enemy_name = re.sub(r"^(?:enemies|enemy)[_-]+", "", enemy_name, flags=re.IGNORECASE)
    enemy_key = _slug(enemy_name)
    animation_name = match.group(1).lower().replace("-", "_").replace(" ", "_")
    state = _STATE_NAMES.get(animation_name)
    if animation_name.startswith("attack"):
        state = "attack"
    elif animation_name.startswith("death"):
        state = "death"
    return (enemy_key, state) if enemy_key and state else None


def _split_sprite_sheet(sheet):
    width, height = sheet.get_size()
    if width > height and width % height == 0:
        frame_width, frame_height = height, height
        frame_count = width // frame_width
        return tuple(
            sheet.subsurface((index * frame_width, 0, frame_width, frame_height)).copy()
            for index in range(frame_count)
        )
    if height > width and height % width == 0:
        frame_width, frame_height = width, width
        frame_count = height // frame_height
        return tuple(
            sheet.subsurface((0, index * frame_height, frame_width, frame_height)).copy()
            for index in range(frame_count)
        )
    return (sheet.copy(),)


class EnemySpriteLibrary:
    """Indexes animation sheets recursively and loads only requested enemies."""

    def __init__(self, sprite_root=None):
        self.sprite_root = Path(sprite_root or _DEFAULT_SPRITE_ROOT).resolve()
        self._paths = {}
        self._frames = {}
        self._scan()

    def _scan(self):
        if not self.sprite_root.is_dir():
            return

        for current_root, directories, filenames in os.walk(self.sprite_root):
            directories.sort()
            for filename in sorted(filenames):
                if not filename.lower().endswith(".png"):
                    continue
                path = Path(current_root) / filename
                parsed = _parse_animation_path(path)
                if parsed:
                    self._paths.setdefault(parsed, []).append(path)

    def _load(self, enemy_key, state):
        cache_key = (enemy_key, state)
        if cache_key in self._frames:
            return self._frames[cache_key]

        frames = []
        for path in self._paths.get(cache_key, ()):
            sheet = pygame.image.load(str(path))
            if pygame.display.get_surface():
                sheet = sheet.convert_alpha()
            frames.extend(_split_sprite_sheet(sheet))
        self._frames[cache_key] = tuple(frames)
        return self._frames[cache_key]

    def animation(self, enemy_name, state="idle", enemy_type=None):
        requested_state = state if state in ("idle", "walk", "attack", "hurt", "death") else "idle"
        enemy_keys = []
        for name in (enemy_name, *_TYPE_SPRITE_CANDIDATES.get(_slug(enemy_type), ())):
            key = _slug(name)
            if key and key not in enemy_keys:
                enemy_keys.append(key)

        state_fallbacks = {
            "attack": ("attack", "walk", "idle"),
            "walk": ("walk", "idle"),
            "hurt": ("hurt", "idle"),
            "death": ("death", "idle"),
            "idle": ("idle", "walk"),
        }
        for enemy_key in enemy_keys:
            for animation_state in state_fallbacks[requested_state]:
                frames = self._load(enemy_key, animation_state)
                if frames:
                    return frames
        return ()

    def load_all(self):
        """Return {enemy: {animation: tuple[Surface, ...]}} for discovered sheets."""
        animations = {}
        for enemy_key, state in sorted(self._paths):
            frames = self._load(enemy_key, state)
            if frames:
                animations.setdefault(enemy_key, {})[state] = frames
        return animations


_DEFAULT_LIBRARY = None


def carregar_animacoes_inimigos(sprite_root=None):
    """Load all recognized enemy animations into a dictionary."""
    global _DEFAULT_LIBRARY
    root = Path(sprite_root or _DEFAULT_SPRITE_ROOT).resolve()
    if _DEFAULT_LIBRARY is None or _DEFAULT_LIBRARY.sprite_root != root:
        _DEFAULT_LIBRARY = EnemySpriteLibrary(root)
    return _DEFAULT_LIBRARY.load_all()


def obter_frames_inimigo(enemy_name, state="idle", enemy_type=None):
    """Get the frames for one enemy animation, loading them on first use."""
    global _DEFAULT_LIBRARY
    if _DEFAULT_LIBRARY is None:
        _DEFAULT_LIBRARY = EnemySpriteLibrary()
    return _DEFAULT_LIBRARY.animation(enemy_name, state, enemy_type)
