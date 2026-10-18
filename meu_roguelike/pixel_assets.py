# pixel_assets.py
import pygame
import hashlib

def criar_sprite_matriz(matriz, tamanho_pixel=2):
    if not matriz or not matriz[0]:
        return pygame.Surface((16, 16), pygame.SRCALPHA)
    altura = len(matriz)
    largura = len(matriz[0])
    surf = pygame.Surface((largura * tamanho_pixel, altura * tamanho_pixel), pygame.SRCALPHA)
    
    for y in range(altura):
        for x in range(largura):
            cor = matriz[y][x]
            if cor is not None:
                pygame.draw.rect(surf, cor, (x * tamanho_pixel, y * tamanho_pixel, tamanho_pixel, tamanho_pixel))
    return surf

# --- MATRIZES DE PIXEL ART POR ESTADO DE ANIMAÇÃO (16x16) ---

# 1. Jogador Parado
MATRIZ_PLAYER_PARADO = [
    [None, None, None, (50,150,250), (50,150,250), (50,150,250), None, None, None],
    [None, None, (50,150,250), (255,220,177), (255,220,177), (255,220,177), (50,150,250), None, None],
    [None, None, None, (50,50,50), (255,220,177), (50,50,50), None, None, None],
    [None, None, (40,100,200), (40,100,200), (40,100,200), (40,100,200), (40,100,200), None, None],
    [None, (40,100,200), (200,200,200), (40,100,200), (40,100,200), (40,100,200), (200,200,200), (40,100,200), None],
    [None, None, (40,100,200), (40,100,200), (40,100,200), (40,100,200), (40,100,200), None, None],
    [None, None, None, (80,80,90), None, (80,80,90), None, None, None],
    [None, None, None, (80,80,90), None, (80,80,90), None, None, None]
]

# 2. Jogador Atacando (Com Espada Estendida)
MATRIZ_PLAYER_ATACANDO = [
    [None, None, None, (50,150,250), (50,150,250), (50,150,250), None, None, None, None, None],
    [None, None, (50,150,250), (255,220,177), (255,220,177), (255,220,177), (50,150,250), None, None, None, None],
    [None, None, None, (50,50,50), (255,220,177), (50,50,50), None, None, None, None, None],
    [None, None, (40,100,200), (40,100,200), (40,100,200), (40,100,200), (40,100,200), (220,220,240), (220,220,240), (255,255,255), None],
    [None, (40,100,200), (200,200,200), (40,100,200), (40,100,200), (40,100,200), (200,200,200), (40,100,200), None, None, None],
    [None, None, (40,100,200), (40,100,200), (40,100,200), (40,100,200), (40,100,200), None, None, None, None],
    [None, None, None, (80,80,90), None, (80,80,90), None, None, None, None, None],
    [None, None, None, (80,80,90), None, (80,80,90), None, None, None, None, None]
]

# 3. Mob Comum / Nascendo
MATRIZ_MOB_NORMAL = [
    [None, (180,50,50), (180,50,50), (180,50,50), (180,50,50), None],
    [(180,50,50), (255,255,255), (180,50,50), (180,50,50), (255,255,255), (180,50,50)],
    [(180,50,50), (180,50,50), (180,50,50), (180,50,50), (180,50,50), (180,50,50)],
    [None, (180,50,50), (180,50,50), (180,50,50), (180,50,50), None]
]

ESTETICA_BIOMAS = {
    1: {"nome": "Campo Verdejante", "piso": (60, 140, 60), "parede": (40, 90, 40), "mob_cor": (100, 220, 100), "chefe": "Slime Rei Gigante", "chefe_cor": (20, 180, 20)},
    2: {"nome": "Floresta Sombria", "piso": (40, 80, 50), "parede": (20, 50, 30), "mob_cor": (80, 160, 100), "chefe": "Ent Raivoso Ancestral", "chefe_cor": (10, 100, 40)},
    3: {"nome": "Caverna de Cristal", "piso": (80, 110, 140), "parede": (40, 60, 90), "mob_cor": (150, 200, 250), "chefe": "Golem de Cristal", "chefe_cor": (70, 130, 200)},
    4: {"nome": "Deserto Ardente", "piso": (180, 150, 90), "parede": (120, 90, 40), "mob_cor": (220, 180, 100), "chefe": "Escorpião Colossal", "chefe_cor": (200, 130, 20)},
    5: {"nome": "Pântano Venenoso", "piso": (70, 100, 70), "parede": (35, 60, 35), "mob_cor": (120, 200, 120), "chefe": "Hydra das Lodo", "chefe_cor": (50, 150, 50)},
    6: {"nome": "Ruínas Antigas", "piso": (120, 115, 110), "parede": (80, 75, 70), "mob_cor": (170, 165, 160), "chefe": "Cavaleiro Espectral", "chefe_cor": (100, 95, 90)},
    7: {"nome": "Montanha Gélida", "piso": (150, 170, 200), "parede": (90, 110, 140), "mob_cor": (200, 220, 250), "chefe": "Yeti Abominável", "chefe_cor": (100, 140, 220)},
    8: {"nome": "Templo Volcânico", "piso": (130, 50, 40), "parede": (80, 25, 20), "mob_cor": (220, 80, 50), "chefe": "Titã de Magma", "chefe_cor": (250, 40, 10)},
    9: {"nome": "Torre Sombria", "piso": (60, 40, 80), "parede": (35, 20, 50), "mob_cor": (140, 90, 180), "chefe": "Lorde Vampiro Imortal", "chefe_cor": (90, 30, 140)},
    10: {"nome": "Abismo do Dragão", "piso": (40, 20, 20), "parede": (20, 10, 10), "mob_cor": (200, 50, 50), "chefe": "Dragão Negro Ancestral", "chefe_cor": (250, 0, 0)},
    11: {"nome": "Mar de Cinzas", "piso": (90, 65, 65), "parede": (48, 30, 35), "mob_cor": (160, 90, 70), "chefe": "Fênix das Cinzas", "chefe_cor": (245, 120, 45)},
    12: {"nome": "Jardins Celestes", "piso": (90, 125, 160), "parede": (45, 75, 115), "mob_cor": (130, 190, 225), "chefe": "Serafim Caído", "chefe_cor": (230, 210, 130)},
    13: {"nome": "Necrópole Dourada", "piso": (125, 100, 65), "parede": (70, 48, 35), "mob_cor": (190, 160, 80), "chefe": "Rei Mumificado", "chefe_cor": (235, 185, 55)},
    14: {"nome": "Fenda Astral", "piso": (70, 45, 120), "parede": (35, 20, 75), "mob_cor": (155, 105, 215), "chefe": "Devorador Astral", "chefe_cor": (205, 90, 240)},
    15: {"nome": "Coração do Vazio", "piso": (50, 30, 65), "parede": (20, 8, 35), "mob_cor": (125, 70, 155), "chefe": "Núcleo do Vazio", "chefe_cor": (245, 50, 145)}
}

_CACHE_SPRITES = {}


def _stable_seed(value):
    return int.from_bytes(hashlib.sha256(str(value).encode("utf-8")).digest()[:4], "big")


def _pixel(surface, color, x, y, size=1):
    pygame.draw.rect(surface, color, (x, y, size, size))


def sprite_inimigo(bioma_id, tipo, tamanho):
    chave = ("enemy", bioma_id, tipo, tamanho)
    if chave in _CACHE_SPRITES:
        return _CACHE_SPRITES[chave]

    paleta = ESTETICA_BIOMAS.get(bioma_id, ESTETICA_BIOMAS[1])
    base = paleta["chefe_cor"] if tipo == "boss" else (139, 82, 38) if tipo == "mimico" else paleta["mob_cor"]
    sombra = tuple(max(0, int(c * 0.55)) for c in base)
    luz = tuple(min(255, int(c * 1.3)) for c in base)
    original = pygame.Surface((16, 16), pygame.SRCALPHA)
    seed = _stable_seed(f"{bioma_id}:{tipo}")

    if tipo in ("tank", "boss", "mimico"):
        for y in range(5, 14):
            for x in range(3, 13):
                if tipo == "boss" or y < 12 or x in (3, 12):
                    _pixel(original, base if (x + y) % 3 else sombra, x, y)
    elif tipo in ("mage", "summoner"):
        for y in range(3, 14):
            largura = max(1, (y - 2) // 2)
            for x in range(8 - largura, 8 + largura):
                _pixel(original, base if (x + y) % 3 else sombra, x, y)
        _pixel(original, luz, 7, 2, 3)
    elif tipo == "support":
        for y in range(5, 14):
            for x in range(4, 12):
                if (x + y) % 5:
                    _pixel(original, base, x, y)
        _pixel(original, luz, 7, 1, 3)
    else:
        for y in range(6, 13):
            for x in range(3, 13):
                if (x * 2 + y + seed) % 4:
                    _pixel(original, base if (x + y) % 3 else sombra, x, y)

    for x in (5, 10):
        _pixel(original, (255, 245, 220), x, 7)
    for offset in range(3):
        x = 2 + ((seed >> (offset * 4)) % 12)
        y = 4 + ((seed >> (offset * 5 + 3)) % 9)
        _pixel(original, luz, x, y)

    original = pygame.transform.scale(original, (24, 24))
    sprite = pygame.transform.scale(original, (max(1, tamanho[0]), max(1, tamanho[1])))
    _CACHE_SPRITES[chave] = sprite
    return sprite


def sprite_item(item, tamanho=32):
    nome = item.get("nome", "item")
    tipo = item.get("tipo_arma", "amulet" if "valor" in item else "melee")
    chave = ("item", nome, tipo, tamanho)
    if chave in _CACHE_SPRITES:
        return _CACHE_SPRITES[chave]

    original = pygame.Surface((16, 16), pygame.SRCALPHA)
    seed = _stable_seed(nome)
    cor = {
        "melee": (205, 215, 230),
        "ranged": (160, 205, 130),
        "mage": (185, 125, 255),
    }.get(tipo, (255, 195, 90))
    sombra = tuple(max(0, c - 75) for c in cor)

    if tipo == "melee":
        for i in range(8):
            _pixel(original, cor if i % 2 else (245, 245, 255), 3 + i, 11 - i)
        for i in range(4):
            _pixel(original, sombra, 2 + i, 12 + i)
        for x in range(5, 9):
            _pixel(original, (235, 180, 80), x, 10)
    elif tipo == "ranged":
        for i in range(8):
            _pixel(original, cor, 3 + i // 2, 3 + i)
            _pixel(original, cor, 13 - i // 2, 3 + i)
        for i in range(8):
            _pixel(original, (245, 235, 210), 5 + i, 11 - i)
        _pixel(original, sombra, 12, 4, 2)
    elif tipo == "mage":
        for i in range(11):
            _pixel(original, (225, 190, 120), 4 + i, 13 - i)
        for x, y in ((11, 2), (12, 3), (10, 3), (11, 4)):
            _pixel(original, cor, x, y)
    else:
        for y in range(4, 12):
            for x in range(4, 12):
                if abs(x - 7.5) + abs(y - 7.5) < 5:
                    _pixel(original, cor, x, y)

    for bit in range(3):
        if (seed >> (bit * 3)) & 1:
            _pixel(original, (255, 255, 255), 2 + bit * 5, 2 + bit * 4)
    original = pygame.transform.scale(original, (24, 24))
    sprite = pygame.transform.scale(original, (min(32, max(1, tamanho)),) * 2)
    _CACHE_SPRITES[chave] = sprite
    return sprite


def sprite_pet(tipo, tamanho=24):
    chave = ("pet", tipo, tamanho)
    if chave in _CACHE_SPRITES:
        return _CACHE_SPRITES[chave]
    cores = {
        "robo": (220, 175, 55), "fenix": (255, 125, 35),
        "lobo": (190, 195, 220), "tartaruga": (70, 175, 95),
        "corvo": (115, 90, 175),
        "besouro": (65, 150, 105), "lince": (215, 175, 95),
        "serpente": (110, 190, 120), "dragao": (190, 65, 95),
        "guardiao_astral": (125, 135, 245),
    }
    cor = cores.get(tipo, (180, 180, 180))
    sombra = tuple(max(0, c - 65) for c in cor)
    original = pygame.Surface((12, 12), pygame.SRCALPHA)
    for y in range(3, 10):
        for x in range(2, 10):
            if tipo == "fenix":
                dentro = abs(x - 5.5) + abs(y - 6) < 6
            elif tipo == "tartaruga":
                dentro = 3 <= x <= 8 and 3 <= y <= 8
            elif tipo == "corvo":
                dentro = 2 <= y <= 8 and (x + y) % 3 != 0
            elif tipo == "besouro":
                dentro = 3 <= x <= 8 and (y <= 8 or x in (3, 8))
            elif tipo == "lince":
                dentro = 3 <= y <= 8 and (2 <= x <= 4 or 7 <= x <= 9)
            elif tipo == "serpente":
                dentro = abs(x - (5 if y % 2 else 6)) <= 2
            else:
                dentro = True
            if dentro:
                _pixel(original, cor if (x + y) % 3 else sombra, x, y)
    if tipo == "lobo":
        _pixel(original, cor, 2, 2, 2)
        _pixel(original, cor, 8, 2, 2)
    elif tipo == "lince":
        _pixel(original, cor, 2, 1, 2)
        _pixel(original, cor, 8, 1, 2)
        _pixel(original, (255, 245, 190), 4, 5)
        _pixel(original, (255, 245, 190), 7, 5)
    elif tipo == "serpente":
        _pixel(original, (255, 235, 150), 5, 4)
    elif tipo == "tartaruga":
        _pixel(original, (235, 205, 100), 4, 4, 3)
    elif tipo == "robo":
        _pixel(original, (255, 235, 150), 4, 5)
        _pixel(original, (255, 235, 150), 7, 5)
    elif tipo == "besouro":
        _pixel(original, (210, 230, 120), 5, 4, 2)
    else:
        _pixel(original, (255, 235, 150), 5, 4, 2)
    sprite = pygame.transform.scale(original, (tamanho, tamanho))
    _CACHE_SPRITES[chave] = sprite
    return sprite


def borda_raridade(tela, rect, raridade):
    from config import RARIDADE_CORES

    pygame.draw.rect(tela, RARIDADE_CORES.get(raridade, (240, 240, 240)), rect, 2)
