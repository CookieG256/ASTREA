# main.py
import pygame
import sys
import math

from config import *
from assets import CarregadorAssets
from particulas import GerenciadorParticulas
from debuffs import GerenciadorStatus
from jogador import Jogador
from inimigos import GerenciadorInimigos
from sala import gerar_andar, desenhar_minimapa, todas_salas_exploradas
from inventario import TelaInventario
from conquistas import GerenciadorConquistas
from index_codex import TelaIndexCodex
from menu_config import MenuConfiguracoes
from menu_inicial import MenuInicial
from save import carregar_dados, salvar_dados

pygame.init()
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Roguelike RPG - Versão Definitiva Completa")
relogio = pygame.time.Clock()

dados_salvos = carregar_dados()
assets = CarregadorAssets()
particulas = GerenciadorParticulas()
status_jogador = GerenciadorStatus()
conquistas_mgr = GerenciadorConquistas(dados_salvos)
index_tela = TelaIndexCodex()
menu_config = MenuConfiguracoes()
menu_inicial = MenuInicial()
inventario_tela = TelaInventario()

up_hp = dados_salvos.get('upgrades_permanentes', {}).get('hp_extra', 0)
up_mana = dados_salvos.get('upgrades_permanentes', {}).get('mana_extra', 0)
player = Jogador(400, 300, bonus_hp=up_hp, bonus_mana=up_mana)
inimigos_mgr = GerenciadorInimigos()

estado_jogo = "MENU_INICIAL"
andar_atual = 1
sala_atual, mapa_salas = gerar_andar()

tempo_ultimo_tiro = 0
projeteis = []
projeteis_inimigos = []

transicao_alpha = 0
em_transicao = False
acao_pos_transicao = None

estatisticas_run = {
    "ouro_coletado": 0,
    "andares_alcancados": 1
}

intro_timer = 0
exibir_intro_andar = False
confirmacao_tipo = None
mensagem_aviso = ""
tempo_aviso = 0

def iniciar_transicao(acao):
    global em_transicao, transicao_alpha, acao_pos_transicao
    em_transicao = True
    transicao_alpha = 0
    acao_pos_transicao = acao

def atualizar_transicao():
    global em_transicao, transicao_alpha, acao_pos_transicao
    if em_transicao:
        transicao_alpha += 15
        if transicao_alpha >= 255:
            transicao_alpha = 255
            if acao_pos_transicao:
                acao_pos_transicao()
                acao_pos_transicao = None
            em_transicao = False

def desenhar_fade(tela):
    global transicao_alpha
    if transicao_alpha > 0:
        s_fade = pygame.Surface((LARGURA, ALTURA))
        s_fade.set_alpha(transicao_alpha)
        s_fade.fill(PRETO)
        tela.blit(s_fade, (0, 0))
        if not em_transicao:
            transicao_alpha = max(0, transicao_alpha - 15)

rodando = True
while rodando:
    tempo_atual = pygame.time.get_ticks()
    relogio.tick(60)
    pos_mouse = pygame.mouse.get_pos()
    clicou = False
    evento_tecla = None

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            rodando = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: 
                clicou = True
                if estado_jogo == "MENU_INICIAL":
                    res = menu_inicial.tratar_clique(pos_mouse, CONFIG_JOGO)
                    if res == "INICIAR_RUN":
                        def reset_game():
                            global andar_atual, sala_atual, mapa_salas, estado_jogo, exibir_intro_andar, intro_timer, estatisticas_run, player
                            dados_atuais = carregar_dados()
                            u_hp = dados_atuais.get('upgrades_permanentes', {}).get('hp_extra', 0)
                            u_mana = dados_atuais.get('upgrades_permanentes', {}).get('mana_extra', 0)
                            player = Jogador(400, 300, bonus_hp=u_hp, bonus_mana=u_mana)
                            andar_atual = 1
                            sala_atual, mapa_salas = gerar_andar()
                            estatisticas_run = {"ouro_coletado": 0, "andares_alcancados": 1}
                            estado_jogo = "JOGANDO"
                            exibir_intro_andar = True
                            intro_timer = tempo_atual
                        iniciar_transicao(reset_game)
                    elif res == "IR_INDEX":
                        estado_jogo = "INDEX"
                    elif res == "IR_CONFIG":
                        estado_jogo = "CONFIGURACOES"
                    elif res == "SAIR":
                        rodando = False
                elif estado_jogo == "INDEX":
                    res_idx = index_tela.tratar_clique(pos_mouse) if hasattr(index_tela, 'tratar_clique') else None
                    if res_idx == "VOLTAR_LOBBY":
                        estado_jogo = "MENU_INICIAL"
                elif estado_jogo == "INVENTARIO":
                    inventario_tela.tratar_clique(pos_mouse, player)
                elif estado_jogo == "CONFIGURACOES":
                    res = menu_config.tratar_clique(pos_mouse, CONFIG_JOGO)
                    if res == "VOLTAR":
                        estado_jogo = "JOGANDO" if getattr(player, 'em_run', False) else "MENU_INICIAL"
                elif estado_jogo == "PAUSE":
                    btn_retomar = pygame.Rect(LARGURA//2 - 120, 220, 240, 45)
                    btn_pause_lobby = pygame.Rect(LARGURA//2 - 120, 280, 240, 45)
                    btn_pause_sair = pygame.Rect(LARGURA//2 - 120, 340, 240, 45)
                    
                    if confirmacao_tipo is None:
                        if btn_retomar.collidepoint(pos_mouse):
                            estado_jogo = "JOGANDO"
                        elif btn_pause_lobby.collidepoint(pos_mouse):
                            confirmacao_tipo = "LOBBY"
                        elif btn_pause_sair.collidepoint(pos_mouse):
                            confirmacao_tipo = "SAIR"
                    else:
                        btn_sim = pygame.Rect(LARGURA//2 - 110, 320, 100, 40)
                        btn_nao = pygame.Rect(LARGURA//2 + 10, 320, 100, 40)
                        if btn_sim.collidepoint(pos_mouse):
                            if confirmacao_tipo == "LOBBY":
                                def ir_lobby():
                                    global estado_jogo, confirmacao_tipo
                                    player.em_run = False
                                    confirmacao_tipo = None
                                    estado_jogo = "MENU_INICIAL"
                                iniciar_transicao(ir_lobby)
                            elif confirmacao_tipo == "SAIR":
                                rodando = False
                        elif btn_nao.collidepoint(pos_mouse):
                            confirmacao_tipo = None

                elif estado_jogo in ["GAME_OVER", "VICTORY"]:
                    btn_jogar_novamente = pygame.Rect(LARGURA//2 - 120, 260, 240, 45)
                    btn_voltar_lobby = pygame.Rect(LARGURA//2 - 120, 320, 240, 45)

                    if btn_jogar_novamente.collidepoint(pos_mouse):
                        def jogar_novamente():
                            global andar_atual, sala_atual, mapa_salas, estado_jogo, exibir_intro_andar, intro_timer, estatisticas_run, player
                            dados_atuais = carregar_dados()
                            u_hp = dados_atuais.get('upgrades_permanentes', {}).get('hp_extra', 0)
                            u_mana = dados_atuais.get('upgrades_permanentes', {}).get('mana_extra', 0)
                            player = Jogador(400, 300, bonus_hp=u_hp, bonus_mana=u_mana)
                            andar_atual = 1
                            sala_atual, mapa_salas = gerar_andar()
                            estatisticas_run = {"ouro_coletado": 0, "andares_alcancados": 1}
                            estado_jogo = "JOGANDO"
                            exibir_intro_andar = True
                            intro_timer = pygame.time.get_ticks()
                        iniciar_transicao(jogar_novamente)
                    elif btn_voltar_lobby.collidepoint(pos_mouse):
                        def ir_lobby():
                            global estado_jogo
                            player.em_run = False
                            estado_jogo = "MENU_INICIAL"
                        iniciar_transicao(ir_lobby)

        if event.type == pygame.KEYDOWN:
            evento_tecla = event
            if event.key == pygame.K_e:
                if estado_jogo == "JOGANDO":
                    estado_jogo = "INVENTARIO"
                elif estado_jogo == "INVENTARIO":
                    estado_jogo = "JOGANDO"
            elif event.key == pygame.K_ESCAPE:
                if estado_jogo == "JOGANDO":
                    estado_jogo = "PAUSE"
                    confirmacao_tipo = None
                elif estado_jogo == "PAUSE":
                    if confirmacao_tipo is not None:
                        confirmacao_tipo = None
                    else:
                        estado_jogo = "JOGANDO"
                elif estado_jogo in ["INDEX", "INVENTARIO"]:
                    estado_jogo = "JOGANDO" if getattr(player, 'em_run', False) else "MENU_INICIAL"
            elif event.key == pygame.K_q:
                teclas = pygame.key.get_pressed()
                player.executar_dash(teclas, tempo_atual)
            elif estado_jogo == "JOGANDO":
                # Sistema de Feitiços (H, J, K, L)
                if event.key == pygame.K_h and player.mana >= 10:
                    player.mana -= 10
                    particulas.criar_texto_dano(player.rect.centerx, player.rect.y - 15, "Feitiço Menor [H]", CIANO)
                    for inimigo in sala_atual.inimigos:
                        if math.hypot(inimigo['rect'].centerx - player.rect.centerx, inimigo['rect'].centery - player.rect.centery) < 150:
                            inimigo['hp'] -= 30
                elif event.key == pygame.K_j and player.mana >= 30:
                    player.mana -= 30
                    particulas.criar_texto_dano(player.rect.centerx, player.rect.y - 15, "Feitiço Médio [J]", CIANO)
                    for inimigo in sala_atual.inimigos:
                        if math.hypot(inimigo['rect'].centerx - player.rect.centerx, inimigo['rect'].centery - player.rect.centery) < 200:
                            inimigo['hp'] -= 60
                elif event.key == pygame.K_k and player.mana >= 70:
                    player.mana -= 70
                    particulas.criar_texto_dano(player.rect.centerx, player.rect.y - 15, "Feitiço Forte [K]", CIANO)
                    for inimigo in sala_atual.inimigos:
                        if math.hypot(inimigo['rect'].centerx - player.rect.centerx, inimigo['rect'].centery - player.rect.centery) < 250:
                            inimigo['hp'] -= 120
                elif event.key == pygame.K_l and player.mana >= 150:
                    player.mana -= 150
                    particulas.criar_texto_dano(player.rect.centerx, player.rect.y - 15, "ULTIMATE [L]!", AMARELO)
                    for inimigo in sala_atual.inimigos:
                        inimigo['hp'] -= 300

    atualizar_transicao()

    if estado_jogo == "JOGANDO":
        player.em_run = True
        estatisticas_run["ouro_coletado"] = player.ouro
        estatisticas_run["andares_alcancados"] = andar_atual

        # Regeneração passiva e infinita de Mana
        player.mana = min(player.mana_max, player.mana + 0.05)

        teclas = pygame.key.get_pressed()
        player.mover(teclas, LARGURA, ALTURA, tempo_atual)

        if sala_atual.tipo == "CHEFE" and sala_atual.fase_chefe == 0:
            if evento_tecla:
                if evento_tecla.key == pygame.K_1:
                    if todas_salas_exploradas(mapa_salas):
                        sala_atual.spawnar_boss_direto()
                    else:
                        mensagem_aviso = "Você ainda não tá pronto! Explore todas as salas!"
                        tempo_aviso = tempo_atual
                elif evento_tecla.key == pygame.K_2:
                    sala_atual.limpa = True

        if sala_atual.tipo in ["LOJA", "CASSINO", "SACRIFICIO", "BAU"] and evento_tecla:
            sala_atual.desenhar_conteudo_especial(tela, player, evento_tecla, particulas)

        arma = player.equipado_arma
        if arma and (tempo_atual - tempo_ultimo_tiro > arma.get('cadencia', 400)):
            if CONFIG_JOGO['modo_tiro'] == 'MANUAL' and (clicou or pygame.mouse.get_pressed()[0]):
                tempo_ultimo_tiro = tempo_atual
                if arma.get('tipo_arma') == 'melee':
                    # Ataque Melee direto em alcance curto à frente
                    for inimigo in sala_atual.inimigos:
                        if math.hypot(inimigo['rect'].centerx - player.rect.centerx, inimigo['rect'].centery - player.rect.centery) < 60:
                            inimigo['hp'] -= arma['dano']
                            particulas.criar_explosao(inimigo['rect'].centerx, inimigo['rect'].centery, AMARELO)
                            particulas.criar_texto_dano(inimigo['rect'].centerx, inimigo['rect'].y - 10, f"-{arma['dano']}", VERMELHO)
                else:
                    angulo = math.atan2(pos_mouse[1] - player.rect.centery, pos_mouse[0] - player.rect.centerx)
                    projeteis.append({'x': player.rect.centerx, 'y': player.rect.centery, 'vx': math.cos(angulo) * 8, 'vy': math.sin(angulo) * 8, 'dano': arma['dano']})
            elif CONFIG_JOGO['modo_tiro'] == 'AUTOMATICO' and len(sala_atual.inimigos) > 0:
                inimigo_alvo = min(sala_atual.inimigos, key=lambda e: math.hypot(e['rect'].centerx - player.rect.centerx, e['rect'].centery - player.rect.centery))
                tempo_ultimo_tiro = tempo_atual
                if arma.get('tipo_arma') == 'melee':
                    if math.hypot(inimigo_alvo['rect'].centerx - player.rect.centerx, inimigo_alvo['rect'].centery - player.rect.centery) < 60:
                        inimigo_alvo['hp'] -= arma['dano']
                        particulas.criar_explosao(inimigo_alvo['rect'].centerx, inimigo_alvo['rect'].centery, AMARELO)
                        particulas.criar_texto_dano(inimigo_alvo['rect'].centerx, inimigo_alvo['rect'].y - 10, f"-{arma['dano']}", VERMELHO)
                else:
                    angulo = math.atan2(inimigo_alvo['rect'].centery - player.rect.centery, inimigo_alvo['rect'].centerx - player.rect.centerx)
                    projeteis.append({'x': player.rect.centerx, 'y': player.rect.centery, 'vx': math.cos(angulo) * 8, 'vy': math.sin(angulo) * 8, 'dano': arma['dano']})

        for p in projeteis[:]:
            p['x'] += p['vx']; p['y'] += p['vy']
            p_rect = pygame.Rect(p['x']-4, p['y']-4, 8, 8)
            hit = False
            for inimigo in sala_atual.inimigos:
                if p_rect.colliderect(inimigo['rect']):
                    if inimigo.get('tipo') == 'boss' and tempo_atual < inimigo.get('tempo_imortal_fim', 0):
                        particulas.criar_texto_dano(p['x'], p['y'] - 10, "IMORTAL!", CIANO)
                    else:
                        inimigo['hp'] -= p['dano']
                        particulas.criar_explosao(p['x'], p['y'], AMARELO)
                        particulas.criar_texto_dano(p['x'], p['y'] - 10, f"-{p['dano']}", VERMELHO)
                    hit = True
                    break
            if hit or p['x'] < 60 or p['x'] > LARGURA - 60 or p['y'] < 60 or p['y'] > ALTURA - 60:
                projeteis.remove(p)

        stats_dict = {'hp': player.hp, 'pode_curar': True, 'em_movimento': player.movendo}
        status_jogador.atualizar(stats_dict, tempo_atual)
        player.hp = stats_dict['hp']

        if not sala_atual.limpa and len(sala_atual.inimigos) == 0:
            if sala_atual.tipo == "NORMAL":
                sala_atual.spawnar_proxima_onda()

        inimigos_mgr.atualizar_e_colidir(sala_atual, player, particulas, lambda t: None, projeteis_inimigos)

        if sala_atual.tipo == "CHEFE" and sala_atual.boss_derrotado:
            def proximo_andar():
                global andar_atual, sala_atual, mapa_salas, estado_jogo, exibir_intro_andar, intro_timer
                andar_atual += 1
                if andar_atual > 3:
                    estado_jogo = "VICTORY"
                else:
                    sala_atual, mapa_salas = gerar_andar()
                    player.rect.center = (LARGURA // 2, ALTURA // 2)
                    exibir_intro_andar = True
                    intro_timer = pygame.time.get_ticks()
            iniciar_transicao(proximo_andar)

        for pi in projeteis_inimigos[:]:
            pi['x'] += pi['vx']; pi['y'] += pi['vy']
            pi_rect = pygame.Rect(pi['x']-3, pi['y']-3, 6, 6)
            if pi_rect.colliderect(player.rect):
                if not player.em_dash:
                    player.hp = max(0, player.hp - pi['dano'])
                    particulas.criar_texto_dano(player.rect.centerx, player.rect.y - 15, f"-{pi['dano']}", VERMELHO)
                projeteis_inimigos.remove(pi)
            elif pi['x'] < 60 or pi['x'] > LARGURA - 60 or pi['y'] < 60 or pi['y'] > ALTURA - 60:
                projeteis_inimigos.remove(pi)

        if player.hp <= 0:
            estado_jogo = "GAME_OVER"

        pode_sair = sala_atual.limpa or sala_atual.tipo in ["LOJA", "CASSINO", "SACRIFICIO", "BAU"]
        if pode_sair and not em_transicao:
            prox_sala = None
            if 'NORTE' in sala_atual.vizinhos and player.rect.top <= 80:
                prox_sala = sala_atual.vizinhos['NORTE']; nova_pos = (player.rect.x, ALTURA - 120)
            elif 'SUL' in sala_atual.vizinhos and player.rect.bottom >= ALTURA - 80:
                prox_sala = sala_atual.vizinhos['SUL']; nova_pos = (player.rect.x, 120)
            elif 'OESTE' in sala_atual.vizinhos and player.rect.left <= 80:
                prox_sala = sala_atual.vizinhos['OESTE']; nova_pos = (LARGURA - 120, player.rect.y)
            elif 'LESTE' in sala_atual.vizinhos and player.rect.right >= LARGURA - 80:
                prox_sala = sala_atual.vizinhos['LESTE']; nova_pos = (120, player.rect.y)

            if prox_sala:
                def trocar_sala():
                    global sala_atual
                    sala_atual = prox_sala
                    sala_atual.revelar()
                    player.rect.x, player.rect.y = nova_pos
                iniciar_transicao(trocar_sala)

    # RENDERIZAÇÃO
    tela.fill(PRETO)

    if estado_jogo == "MENU_INICIAL":
        menu_inicial.desenhar(tela, pos_mouse, dados_salvos.get('gemas', 0))

    elif estado_jogo in ["JOGANDO", "INVENTARIO", "PAUSE"]:
        info_b = BIOMAS_ESTETICA.get(andar_atual, BIOMAS_ESTETICA[1])
        pygame.draw.rect(tela, info_b['piso'], (60, 60, LARGURA - 120, ALTURA - 120))
        pygame.draw.rect(tela, info_b['parede'], (60, 60, LARGURA - 120, ALTURA - 120), 8)

        if sala_atual.tipo == "CHEFE" and sala_atual.fase_chefe == 0:
            txt_p1 = FONTE_GRANDE.render("Você quer me enfrentar?", True, VERMELHO)
            txt_p2 = FONTE_SYS.render("[1] SIM (Enfrentar Chefe) | [2] NÃO (Sair/Ignorar)", True, BRANCO)
            tela.blit(txt_p1, (LARGURA//2 - txt_p1.get_width()//2, ALTURA//2 - 50))
            tela.blit(txt_p2, (LARGURA//2 - txt_p2.get_width()//2, ALTURA//2))

            if tempo_atual - tempo_aviso < 3000:
                txt_aviso = FONTE_SYS.render(mensagem_aviso, True, AMARELO)
                tela.blit(txt_aviso, (LARGURA//2 - txt_aviso.get_width()//2, ALTURA//2 + 50))

        if sala_atual.tipo in ["LOJA", "CASSINO", "SACRIFICIO", "BAU"]:
            sala_atual.desenhar_conteudo_especial(tela, player, None, particulas)

        for p in projeteis:
            pygame.draw.circle(tela, AMARELO, (int(p['x']), int(p['y'])), 4)

        for pi in projeteis_inimigos:
            pygame.draw.circle(tela, VERMELHO, (int(pi['x']), int(pi['y'])), 4)

        inimigos_mgr.desenhar_mira_boss(tela, sala_atual)
        sala_atual.desenhar_inimigos_e_moedas(tela, player, particulas)

        player.desenhar(tela)
        particulas.atualizar_e_desenhar(tela, FONTE_SYS)

        for inimigo in sala_atual.inimigos:
            if inimigo.get('tipo') == 'boss':
                largura_barra = 400
                altura_barra = 20
                bx = (LARGURA - largura_barra) // 2
                by = ALTURA - 40
                hp_perc = max(0, inimigo['hp'] / inimigo['hp_max'])
                
                pygame.draw.rect(tela, CINZA, (bx, by, largura_barra, altura_barra), border_radius=4)
                pygame.draw.rect(tela, VERMELHO, (bx, by, int(largura_barra * hp_perc), altura_barra), border_radius=4)
                txt_b = FONTE_SYS.render(f"CHEFE DO ANDAR: {inimigo['hp']} / {inimigo['hp_max']} HP", True, BRANCO)
                tela.blit(txt_b, (bx + largura_barra//2 - txt_b.get_width()//2, by - 22))

        desenhar_minimapa(tela, mapa_salas, sala_atual)

        # BARRAS ESTILO TERRARIA EMBAIXO DO MINIMAPA
        barra_x = LARGURA - 160
        barra_y = 175
        barra_largura = 140
        barra_altura = 12

        hp_perc = max(0, player.hp / player.hp_max)
        pygame.draw.rect(tela, (0, 0, 0), (barra_x - 1, barra_y - 1, barra_largura + 2, barra_altura + 2), 1)
        pygame.draw.rect(tela, (50, 50, 50), (barra_x, barra_y, barra_largura, barra_altura))
        pygame.draw.rect(tela, (50, 220, 100), (barra_x, barra_y, int(barra_largura * hp_perc), barra_altura))
        txt_hp = FONTE_PEQUENA.render(f"HP: {int(player.hp)}/{int(player.hp_max)}", True, BRANCO)
        tela.blit(txt_hp, (barra_x + 5, barra_y - 1))

        mana_y = barra_y + 18
        mana_perc = max(0, player.mana / player.mana_max)
        pygame.draw.rect(tela, (0, 0, 0), (barra_x - 1, mana_y - 1, barra_largura + 2, barra_altura + 2), 1)
        pygame.draw.rect(tela, (50, 50, 50), (barra_x, mana_y, barra_largura, barra_altura))
        pygame.draw.rect(tela, (50, 120, 230), (barra_x, mana_y, int(barra_largura * mana_perc), barra_altura))
        txt_mana = FONTE_PEQUENA.render(f"Mana: {int(player.mana)}/{int(player.mana_max)}", True, BRANCO)
        tela.blit(txt_mana, (barra_x + 5, mana_y - 1))

        mobs_restantes = len(sala_atual.inimigos)
        gemas_atuais = carregar_dados().get('gemas', 0)
        txt_hud = FONTE_SYS.render(f"Andar {andar_atual} [{info_b['nome']}] | {sala_atual.tipo} | Gold: ${player.ouro} | Gemas: {gemas_atuais} | Restantes: {mobs_restantes}", True, BRANCO)
        tela.blit(txt_hud, (20, 20))

        if exibir_intro_andar:
            if tempo_atual - intro_timer < 2000:
                s_intro = pygame.Surface((LARGURA, ALTURA))
                s_intro.set_alpha(200)
                s_intro.fill(PRETO)
                tela.blit(s_intro, (0, 0))
                
                t_andar = FONTE_GRANDE.render(f"Andar {andar_atual}", True, AMARELO)
                t_modo = FONTE_SYS.render(f"Modo: {CONFIG_JOGO['modo_dificuldade']}", True, BRANCO)
                t_bioma = FONTE_SYS.render(f"Bioma: {info_b['nome']}", True, VERDE_CLARO)
                
                tela.blit(t_andar, (LARGURA//2 - t_andar.get_width()//2, ALTURA//2 - 40))
                tela.blit(t_modo, (LARGURA//2 - t_modo.get_width()//2, ALTURA//2 + 10))
                tela.blit(t_bioma, (LARGURA//2 - t_bioma.get_width()//2, ALTURA//2 + 40))
            else:
                exibir_intro_andar = False

        if estado_jogo == "INVENTARIO":
            inventario_tela.desenhar(tela, player, pos_mouse)

        elif estado_jogo == "PAUSE":
            s_pause = pygame.Surface((LARGURA, ALTURA))
            s_pause.set_alpha(200)
            s_pause.fill(PRETO)
            tela.blit(s_pause, (0, 0))

            txt_p = FONTE_GRANDE.render("JOGO PAUSADO", True, AMARELO)
            tela.blit(txt_p, (LARGURA//2 - txt_p.get_width()//2, 120))

            if confirmacao_tipo is None:
                btn_retomar = pygame.Rect(LARGURA//2 - 120, 220, 240, 45)
                btn_pause_lobby = pygame.Rect(LARGURA//2 - 120, 280, 240, 45)
                btn_pause_sair = pygame.Rect(LARGURA//2 - 120, 340, 240, 45)

                for btn, texto, cor_base in [
                    (btn_retomar, "Retomar", VERDE),
                    (btn_pause_lobby, "Voltar ao Lobby", CINZA),
                    (btn_pause_sair, "Sair do Jogo", VERMELHO)
                ]:
                    cor = BRANCO if btn.collidepoint(pos_mouse) else cor_base
                    pygame.draw.rect(tela, cor, btn, border_radius=6)
                    txt = FONTE_SYS.render(texto, True, PRETO if cor == BRANCO else BRANCO)
                    tela.blit(txt, (btn.centerx - txt.get_width()//2, btn.centery - txt.get_height()//2))
            else:
                msg_conf = "Tem certeza que quer voltar ao lobby?" if confirmacao_tipo == "LOBBY" else "Tem certeza que quer sair do jogo?"
                txt_c = FONTE_SYS.render(msg_conf, True, BRANCO)
                tela.blit(txt_c, (LARGURA//2 - txt_c.get_width()//2, 230))

                btn_sim = pygame.Rect(LARGURA//2 - 110, 300, 100, 40)
                btn_nao = pygame.Rect(LARGURA//2 + 10, 300, 100, 40)

                for btn, texto, cor_base in [
                    (btn_sim, "Sim", VERMELHO),
                    (btn_nao, "Não", CINZA)
                ]:
                    cor = BRANCO if btn.collidepoint(pos_mouse) else cor_base
                    pygame.draw.rect(tela, cor, btn, border_radius=6)
                    txt = FONTE_SYS.render(texto, True, PRETO if cor == BRANCO else BRANCO)
                    tela.blit(txt, (btn.centerx - txt.get_width()//2, btn.centery - txt.get_height()//2))

    elif estado_jogo == "CONFIGURACOES":
        menu_config.desenhar(tela, CONFIG_JOGO, pos_mouse)

    elif estado_jogo == "INDEX":
        index_tela.desenhar(tela, dados_salvos.get('index_descobertas', {}), pos_mouse)

    elif estado_jogo == "GAME_OVER":
        tela.fill(PRETO)
        txt_go = FONTE_GRANDE.render("GAME OVER", True, VERMELHO)
        tela.blit(txt_go, (LARGURA//2 - txt_go.get_width()//2, 80))

        txt_est1 = FONTE_SYS.render(f"Ouro Coletado: ${estatisticas_run['ouro_coletado']}", True, BRANCO)
        txt_est2 = FONTE_SYS.render(f"Andares Alcançados: {estatisticas_run['andares_alcancados']}", True, BRANCO)
        tela.blit(txt_est1, (LARGURA//2 - txt_est1.get_width()//2, 160))
        tela.blit(txt_est2, (LARGURA//2 - txt_est2.get_width()//2, 190))

        btn_jogar_novamente = pygame.Rect(LARGURA//2 - 120, 260, 240, 45)
        btn_voltar_lobby = pygame.Rect(LARGURA//2 - 120, 320, 240, 45)

        for btn, texto, cor_base in [
            (btn_jogar_novamente, "Jogar De Novo", VERDE),
            (btn_voltar_lobby, "Voltar Ao Lobby", CINZA)
        ]:
            cor = BRANCO if btn.collidepoint(pos_mouse) else cor_base
            pygame.draw.rect(tela, cor, btn, border_radius=6)
            txt = FONTE_SYS.render(texto, True, PRETO if cor == BRANCO else BRANCO)
            tela.blit(txt, (btn.centerx - txt.get_width()//2, btn.centery - txt.get_height()//2))

    elif estado_jogo == "VICTORY":
        tela.fill(PRETO)
        txt_win = FONTE_GRANDE.render("VITÓRIA!", True, AMARELO)
        tela.blit(txt_win, (LARGURA//2 - txt_win.get_width()//2, 80))

        txt_est1 = FONTE_SYS.render(f"Ouro Coletado: ${estatisticas_run['ouro_coletado']}", True, BRANCO)
        txt_est2 = FONTE_SYS.render(f"Andares Conquistados: {estatisticas_run['andares_alcancados']}", True, BRANCO)
        tela.blit(txt_est1, (LARGURA//2 - txt_est1.get_width()//2, 160))
        tela.blit(txt_est2, (LARGURA//2 - txt_est2.get_width()//2, 190))

        btn_jogar_novamente = pygame.Rect(LARGURA//2 - 120, 260, 240, 45)
        btn_voltar_lobby = pygame.Rect(LARGURA//2 - 120, 320, 240, 45)

        for btn, texto, cor_base in [
            (btn_jogar_novamente, "Jogar De Novo", VERDE),
            (btn_voltar_lobby, "Voltar Ao Lobby", CINZA)
        ]:
            cor = BRANCO if btn.collidepoint(pos_mouse) else cor_base
            pygame.draw.rect(tela, cor, btn, border_radius=6)
            txt = FONTE_SYS.render(texto, True, PRETO if cor == BRANCO else BRANCO)
            tela.blit(txt, (btn.centerx - txt.get_width()//2, btn.centery - txt.get_height()//2))

    desenhar_fade(tela)
    pygame.display.flip()

pygame.quit()
sys.exit()
