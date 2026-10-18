# pets.py
import pygame
import math
from pixel_assets import sprite_pet

class Pet:
    def __init__(self, tipo, x, y):
        self.tipo = tipo
        self.x = x; self.y = y
        self.velocidade = 4.5
        self.ultimo_ataque = 0
        self.cor = {
            "robo": (220, 175, 55),
            "fenix": (255, 120, 0),
            "lobo": (180, 180, 210),
            "tartaruga": (60, 170, 90),
            "corvo": (90, 75, 150),
            "besouro": (65, 150, 105),
            "lince": (215, 175, 95),
            "serpente": (110, 190, 120),
            "dragao": (190, 65, 95),
            "guardiao_astral": (125, 135, 245),
        }.get(tipo, (180, 180, 180))
        self.tamanho = 10

    def atualizar(self, alvo_x, alvo_y, sala_atual, projeteis_jogador):
        dist = math.hypot(alvo_x - self.x, alvo_y - self.y)
        if dist > 30:
            self.x += (alvo_x - self.x) / dist * self.velocidade
            self.y += (alvo_y - self.y) / dist * self.velocidade

        if self.tipo == "fenix":
            tempo_atual = pygame.time.get_ticks()
            if tempo_atual - self.ultimo_ataque > 2500 and len(sala_atual.inimigos) > 0:
                self.ultimo_ataque = tempo_atual
                alvo = min(sala_atual.inimigos, key=lambda e: math.hypot(e['rect'].centerx - self.x, e['rect'].centery - self.y))
                ax, ay = alvo['rect'].center
                ang = math.atan2(ay - self.y, ax - self.x)
                projeteis_jogador.append({
                    'x': self.x, 'y': self.y, 'vx': math.cos(ang) * 6,
                    'vy': math.sin(ang) * 6, 'dano': 15, 'crit': False,
                })

    def desenhar(self, tela):
        sprite = sprite_pet(self.tipo, 24)
        tela.blit(sprite, (int(self.x) - 12, int(self.y) - 12))