# main.py
import random
import pygame
import sys
import math
import time

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
from tooltip import desenhar_tooltip
from save import carregar_dados, salvar_dados
from idiomas import t

pygame.init()
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("RogueLike RPG")
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

player = Jogador(400, 300)
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

tempo_inicio_run = 0
estatisticas_run = {
    "mobs_mortos": 0,
    "gemas_coletadas": 0,
    "tempo_segundos": 0,
    "andar_morte": 1
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
    lang = CONFIG_JOGO.get('idioma', 'PT')

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
                            global andar_atual, sala_atual, mapa_salas, estado_jogo, exibir_intro_andar, intro_timer, estatisticas_run, player, tempo_inicio_run
                            player = Jogador(400, 300)
                            andar_atual = 1
                            tempo_inicio_run = time.time()
                            sala_atual, mapa_salas = gerar_andar()
                            estatisticas_run = {"mobs_mortos": 0, "gemas_coletadas": 0, "tempo_segundos": 0, "andar_morte": 1}
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
                    acao_index = index_tela.tratar_evento(event, pos_mouse)
                    if acao_index == "VOLTAR_LOBBY":
                        estado_jogo = "MENU"
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
                    btn_jogar_novamente = pygame.Rect(LARGURA//2 - 120, 480, 240, 45)
                    if btn_jogar_novamente.collidepoint(pos_mouse):
                        def jogar_novamente():
                            global andar_atual, sala_atual, mapa_salas, estado_jogo, exibir_intro_andar, intro_timer, estatisticas_run, player, tempo_inicio_run
                            player = Jogador(400, 300)
                            andar_atual = 1
                            tempo_inicio_run = time.time()
                            sala_atual, mapa_salas = gerar_andar()
                            estatisticas_run = {"mobs_mortos": 0, "gemas_coletadas": 0, "tempo_segundos": 0, "andar_morte": 1}
                            estado_jogo = "JOGANDO"
                            exibir_intro_andar = True
                            intro_timer = pygame.time.get_ticks()
                        iniciar_transicao(jogar_novamente)

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
                    particulas.criar_texto_dano(player.rect.centerx, player.rect.y - 15, "Feitiço Fraco (-10)", CIANO)
                    for inimigo in sala_atual.inimigos:
                        if math.hypot(inimigo['rect'].centerx - player.rect.centerx, inimigo['rect'].centery - player.rect.centery) < 150:
                            inimigo['hp'] -= 30
                elif event.key == pygame.K_j and player.mana >= 30:
                    player.mana -= 30
                    particulas.criar_texto_dano(player.rect.centerx, player.rect.y - 15, "Feitiço Médio (-30)", CIANO)
                    for inimigo in sala_atual.inimigos:
                        if math.hypot(inimigo['rect'].centerx - player.rect.centerx, inimigo['rect'].centery - player.rect.centery) < 200:
                            inimigo['hp'] -= 60
                elif event.key == pygame.K_k and player.mana >= 70:
                    player.mana -= 70
                    particulas.criar_texto_dano(player.rect.centerx, player.rect.y - 15, "Feitiço Forte (-70)", CIANO)
                    for inimigo in sala_atual.inimigos:
                        if math.hypot(inimigo['rect'].centerx - player.rect.centerx, inimigo['rect'].centery - player.rect.centery) < 250:
                            inimigo['hp'] -= 120
                elif event.key == pygame.K_l and player.mana >= 150:
                    player.mana -= 150
                    particulas.criar_texto_dano(player.rect.centerx, player.rect.y - 15, "ULTIMATE  (-150)!", AMARELO)
                    for inimigo in sala_atual.inimigos:
                        inimigo['hp'] -= 300

    atualizar_transicao()

    if estado_jogo == "JOGANDO":
        player.em_run = True
        estatisticas_run["tempo_segundos"] = int(time.time() - tempo_inicio_run)
        player.mana = min(player.mana_max, player.mana + 0.05)

        teclas = pygame.key.get_pressed()
        player.mover(teclas, LARGURA, ALTURA, tempo_atual)

        if sala_atual.tipo == "CHEFE" and sala_atual.fase_chefe == 0:
            if evento_tecla:
                if evento_tecla.key == pygame.K_1:
                    if todas_salas_exploradas(mapa_salas):
                        sala_atual.spawnar_boss_direto()
                    else:
                        mensagem_aviso = "Explore todas as salas primeiro!"
                        tempo_aviso = tempo_atual
                elif evento_tecla.key == pygame.K_2:
                    sala_atual.limpa = True

        if sala_atual.tipo in ["LOJA", "CASSINO", "SACRIFICIO", "TESOURO"] and evento_tecla:
            sala_atual.desenhar_conteudo_especial(tela, player, evento_tecla, particulas)

        arma = player.equipado_arma
        if arma and (tempo_atual - tempo_ultimo_tiro > arma.get('cadencia', 400)):
            if (CONFIG_JOGO['modo_tiro'] == 'MANUAL' and (clicou or pygame.mouse.get_pressed()[0])) or (CONFIG_JOGO['modo_tiro'] == 'AUTOMATICO' and len(sala_atual.inimigos) > 0):
                tempo_ultimo_tiro = tempo_atual
                dano_b = arma['dano'] * (1.0 + player.bonus_dano_percent)
                eh_crit = random.random() < player.chance_crit
                if eh_crit:
                    dano_b *= player.mult_crit
                dano_final = int(dano_b)

                if arma.get('tipo_arma') == 'melee':
                    for inimigo in sala_atual.inimigos:
                        if math.hypot(inimigo['rect'].centerx - player.rect.centerx, inimigo['rect'].centery - player.rect.centery) < 65:
                            inimigo['hp'] -= dano_final
                            particulas.criar_explosao(inimigo['rect'].centerx, inimigo['rect'].centery, AMARELO)
                            particulas.criar_texto_dano(inimigo['rect'].centerx, inimigo['rect'].y - 10, f"-{dano_final}!" if eh_crit else f"-{dano_final}", VERMELHO if eh_crit else BRANCO, eh_crit)
                else:
                    if CONFIG_JOGO['modo_tiro'] == 'MANUAL':
                        ang = math.atan2(pos_mouse[1] - player.rect.centery, pos_mouse[0] - player.rect.centerx)
                    else:
                        alvo = min(sala_atual.inimigos, key=lambda e: math.hypot(e['rect'].centerx - player.rect.centerx, e['rect'].centery - player.rect.centery))
                        ang = math.atan2(alvo['rect'].centery - player.rect.centery, alvo['rect'].centerx - player.rect.centerx)
                    projeteis.append({'x': player.rect.centerx, 'y': player.rect.centery, 'vx': math.cos(ang) * 8, 'vy': math.sin(ang) * 8, 'dano': dano_final, 'crit': eh_crit})

        for p in projeteis[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p_rect = pygame.Rect(p['x']-4, p['y']-4, 8, 8)
            hit = False
            for inimigo in sala_atual.inimigos:
                if p_rect.colliderect(inimigo['rect']):
                    if inimigo.get('tipo') == 'boss' and tempo_atual < inimigo.get('tempo_imortal_fim', 0):
                        particulas.criar_texto_dano(p['x'], p['y'] - 10, "IMORTAL!", CIANO)
                    else:
                        inimigo['hp'] -= p['dano']
                        particulas.criar_explosao(p['x'], p['y'], AMARELO)
                        particulas.criar_texto_dano(p['x'], p['y'] - 10, f"-{p['dano']}", VERMELHO if p['crit'] else BRANCO)
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

        inimigos_mgr.atualizar_e_colidir(sala_atual, player, particulas, estatisticas_run, projeteis_inimigos)

        if sala_atual.tipo == "CHEFE" and sala_atual.boss_derrotado:
            def proximo_andar():
                global andar_atual, sala_atual, mapa_salas, estado_jogo, exibir_intro_andar, intro_timer
                andar_atual += 1
                if andar_atual > 3:
                    dados = carregar_dados()
                    dados['vitórias_totais'] = dados.get('vitórias_totais', 0) + 1
                    salvar_dados(dados)
                    estado_jogo = "VICTORY"
                else:
                    sala_atual, mapa_salas = gerar_andar()
                    player.rect.center = (LARGURA // 2, ALTURA // 2)
                    exibir_intro_andar = True
                    intro_timer = pygame.time.get_ticks()
            iniciar_transicao(proximo_andar)

        for pi in projeteis_inimigos[:]:
            pi['x'] += pi['vx']
            pi['y'] += pi['vy']
            pi_rect = pygame.Rect(pi['x']-3, pi['y']-3, 6, 6)
            if pi_rect.colliderect(player.rect):
                if not player.em_dash and not player.imortal:
                    dano_f = max(1, int(pi['dano'] * (1.0 - player.defesa_percent)))
                    player.hp = max(0, player.hp - dano_f)
                    particulas.criar_texto_dano(player.rect.centerx, player.rect.y - 15, f"-{dano_f}", VERMELHO)
                projeteis_inimigos.remove(pi)
            elif pi['x'] < 60 or pi['x'] > LARGURA - 60 or pi['y'] < 60 or pi['y'] > ALTURA - 60:
                projeteis_inimigos.remove(pi)

        if player.hp <= 0:
            tem_fenix = any(a.get('nome') == 'Anel da Fênix' for a in player.amuletos_equipados + player.mochila_itens)
            if tem_fenix:
                player.hp = player.hp_max
                player.tempo_imortal_fim = tempo_atual + 10000
                particulas.criar_texto_dano(player.rect.centerx, player.rect.y - 30, "FÊNIX RENASCIDA!", LARANJA, True)
                for list_item in [player.amuletos_equipados, player.mochila_itens]:
                    for it in list_item:
                        if it.get('nome') == 'Anel da Fênix':
                            list_item.remove(it)
                            break
            else:
                estatisticas_run['andar_morte'] = andar_atual
                estado_jogo = "GAME_OVER"

        pode_s = sala_atual.limpa or sala_atual.tipo in ["LOJA", "CASSINO", "SACRIFICIO", "RECOMPENSA"]
        if pode_s and not em_transicao:
            prox_s = None
            if 'NORTE' in sala_atual.vizinhos and player.rect.top <= 80:
                prox_s = sala_atual.vizinhos['NORTE']; n_pos = (player.rect.x, ALTURA - 120)
            elif 'SUL' in sala_atual.vizinhos and player.rect.bottom >= ALTURA - 80:
                prox_s = sala_atual.vizinhos['SUL']; n_pos = (player.rect.x, 120)
            elif 'OESTE' in sala_atual.vizinhos and player.rect.left <= 80:
                prox_s = sala_atual.vizinhos['OESTE']; n_pos = (LARGURA - 120, player.rect.y)
            elif 'LESTE' in sala_atual.vizinhos and player.rect.right >= LARGURA - 80:
                prox_s = sala_atual.vizinhos['LESTE']; n_pos = (120, player.rect.y)

            if prox_s:
                def trocar_sala():
                    global sala_atual
                    sala_atual = prox_s
                    sala_atual.revelar()
                    player.rect.x, player.rect.y = n_pos
                iniciar_transicao(trocar_sala)

    # RENDERIZAÇÃO
    tela.fill(PRETO)

    if estado_jogo == "MENU_INICIAL":
        menu_inicial.desenhar(tela, pos_mouse, carregar_dados().get('gemas', 0), CONFIG_JOGO)

    elif estado_jogo in ["JOGANDO", "INVENTARIO", "PAUSE"]:
        info_b = BIOMAS_ESTETICA.get(andar_atual, BIOMAS_ESTETICA[1])
        pygame.draw.rect(tela, info_b['piso'], (60, 60, LARGURA - 120, ALTURA - 120))
        pygame.draw.rect(tela, info_b['parede'], (60, 60, LARGURA - 120, ALTURA - 120), 8)

        if sala_atual.tipo == "CHEFE" and sala_atual.fase_chefe == 0:
            txt_p1 = FONTE_GRANDE.render("Quer enfrentar o chefe?", True, VERMELHO)
            txt_p2 = FONTE_SYS.render("[1] SIM (Entrar) | [2] NÃO (Ignorar)", True, BRANCO)
            tela.blit(txt_p1, (LARGURA//2 - txt_p1.get_width()//2, ALTURA//2 - 50))
            tela.blit(txt_p2, (LARGURA//2 - txt_p2.get_width()//2, ALTURA//2))

            if tempo_atual - tempo_aviso < 3000:
                txt_aviso = FONTE_SYS.render(mensagem_aviso, True, AMARELO)
                tela.blit(txt_aviso, (LARGURA//2 - txt_aviso.get_width()//2, ALTURA//2 + 50))

        if sala_atual.tipo in ["LOJA", "CASSINO", "SACRIFICIO", "RECOMPENSA"]:
            sala_atual.desenhar_conteudo_especial(tela, player, None, particulas)

        for p in projeteis:
            pygame.draw.circle(tela, AMARELO, (int(p['x']), int(p['y'])), 4)

        for pi in projeteis_inimigos:
            pygame.draw.circle(tela, VERMELHO, (int(pi['x']), int(pi['y'])), 4)

        inimigos_mgr.desenhar_mira_boss(tela, sala_atual)
        sala_atual.desenhar_inimigos_e_moedas(tela, player, particulas, estatisticas_run)

        player.desenhar(tela)
        particulas.atualizar_e_desenhar(tela, FONTE_SYS)

        for inimigo in sala_atual.inimigos:
            if inimigo.get('tipo') == 'boss':
                largura_barra = 400
                altura_barra = 20
                bx_b = (LARGURA - largura_barra) // 2
                by_b = ALTURA - 40
                hp_perc = max(0, inimigo['hp'] / inimigo['hp_max'])
                
                pygame.draw.rect(tela, CINZA, (bx_b, by_b, largura_barra, altura_barra), border_radius=4)
                pygame.draw.rect(tela, VERMELHO, (bx_b, by_b, int(largura_barra * hp_perc), altura_barra), border_radius=4)
                txt_b = FONTE_SYS.render(f"CHEFE: {inimigo['hp']} / {inimigo['hp_max']} HP", True, BRANCO)
                tela.blit(txt_b, (bx_b + largura_barra//2 - txt_b.get_width()//2, by_b - 22))

        desenhar_minimapa(tela, mapa_salas, sala_atual)

        # Barras de Status
        bx = LARGURA - 160
        by = 175
        pygame.draw.rect(tela, PRETO, (bx - 1, by - 1, 142, 14), 1)
        pygame.draw.rect(tela, VERDE, (bx, by, int(140 * max(0, player.hp/player.hp_max)), 12))
        txt_hp = FONTE_PEQUENA.render(f"HP: {int(player.hp)}/{int(player.hp_max)}", True, BRANCO)
        tela.blit(txt_hp, (bx + 5, by - 1))

        my = by + 18
        pygame.draw.rect(tela, PRETO, (bx - 1, my - 1, 142, 14), 1)
        pygame.draw.rect(tela, AZUL, (bx, my, int(140 * max(0, player.mana/player.mana_max)), 12))
        txt_mana = FONTE_PEQUENA.render(f"Mana: {int(player.mana)}/{int(player.mana_max)}", True, BRANCO)
        tela.blit(txt_mana, (bx + 5, my - 1))

        # Dificuldade abaixo do mapa
        cor_dif = VERMELHO_ESCURO if CONFIG_JOGO['modo_dificuldade'] == 'HARDCORE' else (AMARELO if CONFIG_JOGO['modo_dificuldade'] == 'DIFICIL' else VERDE)
        txt_dif = FONTE_PEQUENA.render(f"{t('modo', lang)}: {CONFIG_JOGO['modo_dificuldade']}", True, cor_dif)
        tela.blit(txt_dif, (bx, my + 18))

        # HUD Topo
        txt_hud = FONTE_SYS.render(f"{t('andar', lang)} {andar_atual} | {t('ouro', lang)}: ${player.ouro} | {t('gemas', lang)}: {carregar_dados().get('gemas', 0)}", True, BRANCO)
        tela.blit(txt_hud, (20, 20))

        if exibir_intro_andar:
            if tempo_atual - intro_timer < 2000:
                s_intro = pygame.Surface((LARGURA, ALTURA))
                s_intro.set_alpha(200)
                s_intro.fill(PRETO)
                tela.blit(s_intro, (0, 0))
                
                t_andar = FONTE_GRANDE.render(f"{t('andar', lang)} {andar_atual}", True, AMARELO)
                t_bioma = FONTE_SYS.render(f"Bioma: {info_b['nome']}", True, VERDE_CLARO)
                
                tela.blit(t_andar, (LARGURA//2 - t_andar.get_width()//2, ALTURA//2 - 30))
                tela.blit(t_bioma, (LARGURA//2 - t_bioma.get_width()//2, ALTURA//2 + 10))
            else:
                exibir_intro_andar = False

        if estado_jogo == "INVENTARIO":
            inventario_tela.desenhar(tela, player, pos_mouse)
            # Tooltip para itens no inventário
            for slot in inventario_tela.slots_inventario:
                if slot['rect'].collidepoint(pos_mouse) and slot['item']:
                    desenhar_tooltip(tela, slot['item'], pos_mouse)

        elif estado_jogo == "PAUSE":
            s_pause = pygame.Surface((LARGURA, ALTURA))
            s_pause.set_alpha(200)
            s_pause.fill(PRETO)
            tela.blit(s_pause, (0, 0))

            txt_p = FONTE_GRANDE.render(t("pausa", lang), True, AMARELO)
            tela.blit(txt_p, (LARGURA//2 - txt_p.get_width()//2, 120))

            if confirmacao_tipo is None:
                btn_retomar = pygame.Rect(LARGURA//2 - 120, 220, 240, 45)
                btn_pause_lobby = pygame.Rect(LARGURA//2 - 120, 280, 240, 45)
                btn_pause_sair = pygame.Rect(LARGURA//2 - 120, 340, 240, 45)

                for btn, chave_txt, cor_base in [
                    (btn_retomar, "retomar", VERDE),
                    (btn_pause_lobby, "voltar_lobby", CINZA),
                    (btn_pause_sair, "sair", VERMELHO)
                ]:
                    cor = BRANCO if btn.collidepoint(pos_mouse) else cor_base
                    pygame.draw.rect(tela, cor, btn, border_radius=6)
                    txt = FONTE_SYS.render(t(chave_txt, lang), True, PRETO if cor == BRANCO else BRANCO)
                    tela.blit(txt, (btn.centerx - txt.get_width()//2, btn.centery - txt.get_height()//2))
            else:
                msg_conf = t("confirm_lobby", lang) if confirmacao_tipo == "LOBBY" else t("confirm_sair", lang)
                txt_c = FONTE_SYS.render(msg_conf, True, BRANCO)
                tela.blit(txt_c, (LARGURA//2 - txt_c.get_width()//2, 230))

                btn_sim = pygame.Rect(LARGURA//2 - 110, 300, 100, 40)
                btn_nao = pygame.Rect(LARGURA//2 + 10, 300, 100, 40)

                for btn, chave_txt, cor_base in [(btn_sim, "sim", VERMELHO), (btn_nao, "nao", CINZA)]:
                    cor = BRANCO if btn.collidepoint(pos_mouse) else cor_base
                    pygame.draw.rect(tela, cor, btn, border_radius=6)
                    txt = FONTE_SYS.render(t(chave_txt, lang), True, PRETO if cor == BRANCO else BRANCO)
                    tela.blit(txt, (btn.centerx - txt.get_width()//2, btn.centery - txt.get_height()//2))

    elif estado_jogo == "CONFIGURACOES":
        menu_config.desenhar(tela, CONFIG_JOGO, pos_mouse)

    elif estado_jogo == "INDEX":
        index_tela.desenhar(tela, pos_mouse, CONFIG_JOGO)

    elif estado_jogo in ["GAME_OVER", "VICTORY"]:
        tela.fill(PRETO)
        txt_t = FONTE_TITULO.render(t("game_over", lang) if estado_jogo == "GAME_OVER" else t("vitoria", lang), True, VERMELHO if estado_jogo == "GAME_OVER" else AMARELO)
        tela.blit(txt_t, (LARGURA//2 - txt_t.get_width()//2, 60))

        lines_e = [
            f"{t('tempo_jogado', lang)}: {estatisticas_run['tempo_segundos']} {t('segundos', lang)}",
            f"{t('mobs_mortos', lang)}: {estatisticas_run['mobs_mortos']}",
            f"{t('gemas_run', lang)}: {estatisticas_run['gemas_coletadas']}",
            f"{t('morreu_andar', lang)}: {estatisticas_run['andar_morte']}"
        ]
        y_e = 160
        for l in lines_e:
            txt_s = FONTE_SYS.render(l, True, BRANCO)
            tela.blit(txt_s, (LARGURA//2 - txt_s.get_width()//2, y_e))
            y_e += 35

        btn_jogar_novamente = pygame.Rect(LARGURA//2 - 120, 480, 240, 45)
        cor = BRANCO if btn_jogar_novamente.collidepoint(pos_mouse) else VERDE
        pygame.draw.rect(tela, cor, btn_jogar_novamente, border_radius=6)
        txt_j = FONTE_SYS.render(t("jogar_denovo", lang), True, PRETO if cor == BRANCO else BRANCO)
        tela.blit(txt_j, (btn_jogar_novamente.centerx - txt_j.get_width()//2, btn_jogar_novamente.centery - txt_j.get_height()//2))

    desenhar_fade(tela)
    pygame.display.flip()

pygame.quit()
sys.exit()