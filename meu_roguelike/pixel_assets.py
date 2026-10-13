# pixel_assets.py
import pygame
import os

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
    10: {"nome": "Abismo do Dragão", "piso": (40, 20, 20), "parede": (20, 10, 10), "mob_cor": (200, 50, 50), "chefe": "Dragão Negro Ancestral", "chefe_cor": (250, 0, 0)}
}
