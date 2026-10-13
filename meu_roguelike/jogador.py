# jogador.py
import pygame
from config import ROXO, LARGURA, ALTURA

class Jogador:
    def __init__(self, x, y, bonus_hp=0, bonus_mana=0):
        self.rect = pygame.Rect(x, y, 30, 30)
        self.vel_base = 5
        self.hp_max = 200 + bonus_hp
        self.hp = self.hp_max
        self.mana_max = 100 + bonus_mana
        self.mana = self.mana_max
        self.ouro = 0
        self.chance_esquiva = 0.05
        self.movendo = False
        
        self.em_dash = False
        self.tempo_inicio_dash = 0
        self.cooldown_dash = 1000
        self.ultimo_dash = 0
        self.duracao_dash = 200
        self.dir_dash_x = 0
        self.dir_dash_y = 0

        self.buff_velocidade_ativo = False
        
        self.equipado_capacete = None
        self.equipado_peitoral = None
        self.equipado_calca = None
        self.equipado_arma = {'nome': 'Pistola', 'tipo_arma': 'ranged', 'dano': 15, 'cadencia': 400, 'raridade': 'Comum'}

        self.mochila_itens = []
        self.amuletos_equipados = []
        self.ultimo_dano_recebido = 0
        self.em_run = False
        
        # Controle de Ataque Melee
        self.atacando_melee = False
        self.tempo_inicio_melee = 0
        self.duracao_melee = 150
        self.angulo_olhando = 0

    def executar_dash(self, teclas, tempo_atual):
        if tempo_atual - self.ultimo_dash > self.cooldown_dash and not self.em_dash:
            dx, dy = 0, 0
            if teclas[pygame.K_a] or teclas[pygame.K_LEFT]: dx -= 1
            if teclas[pygame.K_d] or teclas[pygame.K_RIGHT]: dx += 1
            if teclas[pygame.K_w] or teclas[pygame.K_UP]: dy -= 1
            if teclas[pygame.K_s] or teclas[pygame.K_DOWN]: dy += 1

            if dx != 0 or dy != 0:
                self.dir_dash_x = dx
                self.dir_dash_y = dy
            else:
                self.dir_dash_x = 0
                self.dir_dash_y = -1

            self.em_dash = True
            self.tempo_inicio_dash = tempo_atual
            self.ultimo_dash = tempo_atual

    def mover(self, teclas, largura, altura, tempo_atual):
        self.movendo = False
        
        if self.em_dash:
            if tempo_atual - self.tempo_inicio_dash > self.duracao_dash:
                self.em_dash = False

        if self.em_dash:
            vel_dash = 15
            self.rect.x += self.dir_dash_x * vel_dash
            self.rect.y += self.dir_dash_y * vel_dash
        else:
            vel_atual = self.vel_base * 1.5 if self.buff_velocidade_ativo else self.vel_base
            if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:
                self.rect.x -= vel_atual
                self.movendo = True
                self.angulo_olhando = 180
            if teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:
                self.rect.x += vel_atual
                self.movendo = True
                self.angulo_olhando = 0
            if teclas[pygame.K_w] or teclas[pygame.K_UP]:
                self.rect.y -= vel_atual
                self.movendo = True
                self.angulo_olhando = 90
            if teclas[pygame.K_s] or teclas[pygame.K_DOWN]:
                self.rect.y += vel_atual
                self.movendo = True
                self.angulo_olhando = 270

        self.rect.clamp_ip(pygame.Rect(80, 80, LARGURA - 160, ALTURA - 160))

    def desenhar(self, tela):
        cor = (220, 120, 255) if self.em_dash else ROXO
        pygame.draw.rect(tela, cor, self.rect)