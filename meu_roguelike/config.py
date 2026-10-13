# config.py
import pygame

LARGURA = 900
ALTURA = 600

PRETO = (15, 15, 20)
BRANCO = (240, 240, 240)
CINZA = (50, 50, 60)
CINZA_CLARO = (140, 140, 150)
VERMELHO = (230, 50, 50)
VERDE = (50, 220, 100)
AZUL = (50, 120, 230)
AMARELO = (240, 200, 50)
ROXO = (160, 60, 240)
CIANO = (0, 255, 255)
VERDE_CLARO = (150, 255, 150)

RARIDADE_CORES = {
    "Comum": (150, 150, 150),
    "Épico": (160, 60, 240),
    "Lendário": (240, 200, 50),
    "Mítico": (230, 50, 50)
}

pygame.font.init()
FONTE_SYS = pygame.font.SysFont("arial", 16, bold=True)
FONTE_PEQUENA = pygame.font.SysFont("arial", 12, bold=True)
FONTE_GRANDE = pygame.font.SysFont("arial", 32, bold=True)

BIOMAS_ESTETICA = {
    1: {"nome": "Campo Verdejante", "piso": (40, 90, 40), "parede": (20, 60, 20)},
    2: {"nome": "Floresta Sombria", "piso": (30, 60, 40), "parede": (15, 40, 25)},
    3: {"nome": "Caverna de Cristal", "piso": (50, 70, 100), "parede": (30, 45, 75)},
    4: {"nome": "Deserto Ardente", "piso": (160, 130, 70), "parede": (110, 85, 40)},
    5: {"nome": "Pântano Venenoso", "piso": (50, 80, 50), "parede": (25, 45, 25)},
    6: {"nome": "Ruínas Antigas", "piso": (90, 85, 80), "parede": (60, 55, 50)},
    7: {"nome": "Montanha Gélida", "piso": (120, 140, 170), "parede": (70, 90, 120)},
    8: {"nome": "Templo Volcânico", "piso": (100, 35, 30), "parede": (60, 20, 15)},
    9: {"nome": "Torre Sombria", "piso": (45, 30, 60), "parede": (25, 15, 40)},
    10: {"nome": "Abismo do Dragão", "piso": (30, 15, 15), "parede": (15, 5, 5)}
}

CONFIG_JOGO = {
    'modo_tiro': 'AUTOMATICO', 
    'volume_sfx': 80,
    'volume_musica': 50,
    'modo_dificuldade': 'CASUAL'
}