# inimigos.py
import pygame
import math
import random
from config import LARGURA, ALTURA, VERMELHO, AMARELO, BRANCO, CINZA, VERDE, CIANO, CONFIG_JOGO
from save import carregar_dados, salvar_dados

class GerenciadorInimigos:
    def __init__(self):
        self.cooldown_dash_boss = 3500
        self.ultimo_dash_boss = 0
        self.boss_em_preparacao = False
        self.tempo_inicio_preparacao = 0
        self.boss_em_dash = False
        self.tempo_inicio_dash = 0
        self.boss_em_aoe = False
        self.tempo_inicio_aoe = 0
        self.dir_dash_x = 0; self.dir_dash_y = 0
        self.pos_alvo_aoe = (0, 0)

    def atualizar_e_colidir(self, sala, player, particulas, notificacao_func, projeteis_inimigos):
        tempo_atual = pygame.time.get_ticks()

        for inimigo in sala.inimigos[:]:
            if 'rect' not in inimigo:
                continue
            
            r = inimigo['rect']
            r.clamp_ip(pygame.Rect(80, 80, LARGURA - 160, ALTURA - 160))

            tipo = inimigo.get('tipo', 'perto')
            px, py = player.rect.center
            ix, iy = r.center
            dist = math.hypot(px - ix, py - iy)

            if tipo == 'boss':
                hp_atual = inimigo['hp']
                hp_max = inimigo['hp_max']

                if not inimigo.get('rage_ativado', False) and hp_atual <= hp_max // 3:
                    inimigo['rage_ativado'] = True
                    inimigo['hp'] = min(hp_max, hp_atual + 200)
                    inimigo['tempo_imortal_fim'] = tempo_atual + 5000
                    particulas.criar_texto_dano(r.centerx, r.y - 25, "MODO FÚRIA! +200 HP & IMORTAL (5s)!", AMARELO)

                em_furia = inimigo.get('rage_ativado', False) or (hp_atual <= 600)
                vel_boss = 4.5 if em_furia else 2.5
                cd_dash = 2000 if em_furia else 3500

                if self.boss_em_aoe:
                    if tempo_atual - self.tempo_inicio_aoe >= 1000:
                        self.boss_em_aoe = False
                        bx, by = self.pos_alvo_aoe
                        if math.hypot(px - bx, py - iy) <= 130 and not player.em_dash:
                            dano = 35 if em_furia else 25
                            player.hp = max(0, player.hp - dano)
                            particulas.criar_texto_dano(player.rect.centerx, player.rect.y - 15, f"-{dano} IMPACTO!", VERMELHO)
                    continue

                if self.boss_em_dash:
                    if tempo_atual - self.tempo_inicio_dash > 300:
                        self.boss_em_dash = False
                        self.boss_em_aoe = True
                        self.tempo_inicio_aoe = tempo_atual
                        bx, by = r.center
                        self.pos_alvo_aoe = (max(150, min(LARGURA - 150, bx)), max(150, min(ALTURA - 150, by)))
                    else:
                        r.x += int(self.dir_dash_x * 18)
                        r.y += int(self.dir_dash_y * 18)
                        r.clamp_ip(pygame.Rect(80, 80, LARGURA - 160, ALTURA - 160))
                    continue

                if self.boss_em_preparacao:
                    if tempo_atual - self.tempo_inicio_preparacao > 600:
                        self.boss_em_preparacao = False
                        self.boss_em_dash = True
                        self.tempo_inicio_dash = tempo_atual
                    continue

                if dist > 0:
                    r.x += int((px - ix) / dist * vel_boss)
                    r.y += int((py - iy) / dist * vel_boss)

                if tempo_atual - self.ultimo_dash_boss > cd_dash:
                    self.ultimo_dash_boss = tempo_atual
                    self.boss_em_preparacao = True
                    self.tempo_inicio_preparacao = tempo_atual
                    if dist > 0:
                        self.dir_dash_x = (px - ix) / dist
                        self.dir_dash_y = (py - iy) / dist

            elif tipo == 'mimico':
                if dist < 120:
                    if dist > 0:
                        r.x += int((px - ix) / dist * 3.5)
                        r.y += int((py - iy) / dist * 3.5)
            else:
                if tipo == 'perto' and dist > 0:
                    r.x += int((px - ix) / dist * 3)
                    r.y += int((py - iy) / dist * 3)
                elif tipo == 'tank' and dist > 0:
                    r.x += int((px - ix) / dist * 1.8)
                    r.y += int((py - iy) / dist * 1.8)
                elif tipo == 'longe':
                    if dist > 220 and dist > 0:
                        r.x += int((px - ix) / dist * 2.2)
                        r.y += int((py - iy) / dist * 2.2)
                    ultimo_tiro = inimigo.get('ultimo_tiro', 0)
                    if tempo_atual - ultimo_tiro > 2000:
                        inimigo['ultimo_tiro'] = tempo_atual
                        if dist > 0:
                            vx = (px - ix) / dist * 6
                            vy = (py - iy) / dist * 6
                            projeteis_inimigos.append({'x': ix, 'y': iy, 'vx': vx, 'vy': vy, 'dano': 10})
                elif tipo == 'curandeiro':
                    aliados = [e for e in sala.inimigos if e.get('tipo') != 'curandeiro' and e != inimigo]
                    if aliados:
                        dx_player = ix - px
                        dy_player = iy - py
                        dist_p = math.hypot(dx_player, dy_player)
                        if dist_p > 0:
                            r.x += int((dx_player / dist_p) * 2.2)
                            r.y += int((dy_player / dist_p) * 2.2)

                        ultima_cura = inimigo.get('ultima_cura', 0)
                        if tempo_atual - ultima_cura > 3000:
                            inimigo['ultima_cura'] = tempo_atual
                            alvo_aliado = min(aliados, key=lambda a: math.hypot(a['rect'].centerx - ix, a['rect'].centery - iy))
                            if alvo_aliado['hp'] < alvo_aliado['hp_max']:
                                cura_val = 25
                                alvo_aliado['hp'] = min(alvo_aliado['hp_max'], alvo_aliado['hp'] + cura_val)
                                particulas.criar_texto_dano(alvo_aliado['rect'].centerx, alvo_aliado['rect'].y - 10, f"+{cura_val} HP", VERDE)
                    else:
                        if dist > 0 and dist < 300:
                            r.x += int((ix - px) / dist * 2)
                            r.y += int((iy - py) / dist * 2)

            if r.colliderect(player.rect) and not player.em_dash:
                if tempo_atual - getattr(player, 'ultimo_dano_recebido', 0) > 800:
                    player.ultimo_dano_recebido = tempo_atual
                    dano_t = 20 if tipo == 'mimico' else 15
                    player.hp = max(0, player.hp - dano_t)
                    particulas.criar_texto_dano(player.rect.centerx, player.rect.y - 15, f"-{dano_t}", VERMELHO)

            if inimigo['hp'] <= 0:
                if tipo == 'boss':
                    sala.moedas_no_chao.append({'rect': pygame.Rect(r.centerx, r.centery, 16, 16), 'tipo': 'gema_ciano', 'valor': 10})
                    sala.boss_derrotado = True
                else:
                    mult_drop = 1.5 if CONFIG_JOGO.get('modo_dificuldade') == 'DIFICIL' else 1.0
                    ouro_drop = int(random.randint(3, 7) * mult_drop)
                    sala.moedas_no_chao.append({'rect': pygame.Rect(r.centerx, r.centery, 12, 12), 'tipo': 'ouro', 'valor': ouro_drop})
                    if random.random() < 0.4:
                        sala.orbes_cura.append({'rect': pygame.Rect(r.centerx + 10, r.centery, 14, 14), 'cura': 20})
                
                particulas.criar_explosao(r.centerx, r.centery, VERMELHO)
                sala.inimigos.remove(inimigo)

    def desenhar_mira_boss(self, tela, sala):
        for inimigo in sala.inimigos:
            if inimigo.get('tipo') == 'boss':
                r = inimigo['rect']
                if self.boss_em_preparacao:
                    pygame.draw.line(tela, (255, 100, 100), (r.centerx, r.centery), (r.centerx + int(self.dir_dash_x * 150), r.centery + int(self.dir_dash_y * 150)), 3)
        
        if self.boss_em_aoe:
            bx, by = self.pos_alvo_aoe
            pygame.draw.circle(tela, (255, 50, 50), (bx, by), 130, 3)
            pygame.draw.circle(tela, (255, 0, 0, 80), (bx, by), 130, 0)