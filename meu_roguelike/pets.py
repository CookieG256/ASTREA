# pets.py
import pygame
import math

class Pet:
    def __init__(self, tipo, x, y):
        self.tipo = tipo
        self.x = x; self.y = y
        self.velocidade = 4.5
        self.ultimo_ataque = 0
        self.cor = (150, 150, 160) if tipo == "robo" else (255, 120, 0)
        self.tamanho = 10

    def atualizar(self, alvo_x, alvo_y, sala_atual, projeteis_inimigos):
        dist = math.hypot(alvo_x - self.x, alvo_y - self.y)
        if dist > 30:
            self.x += (alvo_x - self.x) / dist * self.velocidade
            self.y += (alvo_y - self.y) / dist * self.velocidade

        if self.tipo == "robo":
            for gema in getattr(sala_atual, 'moedas_no_chao', []):
                gx, gy = gema['rect'].center
                d_gema = math.hypot(self.x - gx, self.y - gy)
                if d_gema < 150:
                    gema['rect'].x += int((self.x - gx) / d_gema * 5)
                    gema['rect'].y += int((self.y - gy) / d_gema * 5)
        elif self.tipo == "fenix":
            tempo_atual = pygame.time.get_ticks()
            if tempo_atual - self.ultimo_ataque > 2500 and len(sala_atual.inimigos) > 0:
                self.ultimo_ataque = tempo_atual
                alvo = min(sala_atual.inimigos, key=lambda e: math.hypot(e['rect'].centerx - self.x, e['rect'].centery - self.y))
                ax, ay = alvo['rect'].center
                ang = math.atan2(ay - self.y, ax - self.x)
                projeteis_inimigos.append({'x': self.x, 'y': self.y, 'vx': math.cos(ang)*6, 'vy': math.sin(ang)*6, 'dano': 15})

    def desenhar(self, tela, assets=None):
        sprite = assets.pegar_sprite(self.tipo, 24, 24) if assets else None
        if sprite:
            tela.blit(sprite, (int(self.x) - 12, int(self.y) - 12))
        else:
            pygame.draw.circle(tela, self.cor, (int(self.x), int(self.y)), self.tamanho)
            pygame.draw.circle(tela, (255, 255, 255), (int(self.x) - 2, int(self.y) - 2), 3)