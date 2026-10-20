# main.py
import random
import copy
import pygame
import sys
import math
import time
import webbrowser

from config import *
from assets import CarregadorAssets
from particulas import GerenciadorParticulas
from debuffs import GerenciadorStatus
from jogador import (
    Jogador,
    cadencia_ataque_arma,
    configurar_municao_arma,
    custo_mana_ataque,
    atualizar_municao_arma,
)
from inimigos import GerenciadorInimigos, aplicar_dano_player, aplicar_dano_inimigo
from sala import gerar_andar, desenhar_minimapa, todas_salas_exploradas
from audio import GerenciadorAudio
from inventario import TelaInventario
from conquistas import GerenciadorConquistas, TelaConquistasBestiario
from index_codex import TelaIndexCodex
from menu_config import MenuConfiguracoes
from menu_inicial import MenuInicial
from tooltip import desenhar_tooltip
from save import carregar_dados, salvar_dados
from idiomas import t, nome_chefe_localizado, nome_bioma_localizado
from pets import Pet
from sinergias import (
    curar_por_sinergia_critica,
    custo_mana_com_sinergia,
    velocidade_projetil_com_sinergia,
)
from progressao import (
    iniciar_contrato, registrar_uso_arma, bonus_maestria,
    estado_desafio_diario,
)
from controles import estado_acoes_teclado, estado_analogico, normalizar_controles, traduzir_tecla_acao
from ambiente import aplicar_ambiente, desenhar_ambiente
from registros_run import registrar_run, obter_melhores_runs_por_dificuldade
from missoes import TelaMissoes, registrar_progresso
from personagens import RACES_AND_CLASSES
from narrativa import (
    FRAGMENTOS_BIOMAS, desbloquear_fragmento, texto_fragmento,
)
from npc_hub import SalaNPCs, comprar_servico_npc, aplicar_servicos_npc
from plataforma import IS_MOBILE, ControlesTouch
from combate_avancado import (
    ControleCombate,
    HABILIDADES_MITICAS,
    NOMES_HABILIDADES,
    arma_mitica_id,
    usar_habilidade_mitica,
    atualizar_conjuracao_mitica,
    registrar_baixa_vida,
    desenhar_efeito_vida_baixa,
)

pygame.init()
CONFIG_JOGO_PADRAO = copy.deepcopy(CONFIG_JOGO)
dados_salvos = carregar_dados()
if isinstance(dados_salvos.get("configuracoes"), dict):
    CONFIG_JOGO.update(dados_salvos["configuracoes"])
if CONFIG_JOGO.get("raca_jogador") not in RACES_AND_CLASSES["races"]:
    CONFIG_JOGO["raca_jogador"] = "Humano"
if CONFIG_JOGO.get("classe_jogador") not in RACES_AND_CLASSES["classes"]:
    CONFIG_JOGO["classe_jogador"] = "Guerreiro"
controles_jogo = normalizar_controles(CONFIG_JOGO)
pygame.joystick.init()
flags_tela = 0
if IS_MOBILE:
    flags_tela = pygame.FULLSCREEN | pygame.SCALED
elif CONFIG_JOGO.get("fullscreen"):
    flags_tela = pygame.FULLSCREEN
tela = pygame.display.set_mode((LARGURA, ALTURA), flags_tela)
pygame.display.set_caption("ASTREA")
relogio = pygame.time.Clock()
controles_touch = ControlesTouch()

audio = GerenciadorAudio()
audio.atualizar_volumes(CONFIG_JOGO)
assets = CarregadorAssets()
particulas = GerenciadorParticulas()
status_jogador = GerenciadorStatus()
conquistas_mgr = GerenciadorConquistas(dados_salvos)
index_tela = TelaIndexCodex()
tela_conquistas = TelaConquistasBestiario()
menu_config = MenuConfiguracoes()
menu_inicial = MenuInicial()
hub_npcs = SalaNPCs()
inventario_tela = TelaInventario()
missoes_tela = TelaMissoes()

player = Jogador(400, 300)
inimigos_mgr = GerenciadorInimigos()
player2 = Jogador(440, 300, numero_jogador=2) if CONFIG_JOGO.get("coop_local") else None
status_jogador2 = GerenciadorStatus()
ultimo_ataque_p2 = 0
run_registrada = False
mobs_missoes_reportados = 0
elites_missoes_reportados = 0
estado_missoes_retorno = "MENU_INICIAL"
melhores_runs_cache = obter_melhores_runs_por_dificuldade()
historia_aviso = None
historia_aviso_tempo = 0
fragmento_selecionado = 1
modo_espectador = False


def sincronizar_jogador2():
    global player2, status_jogador2
    if CONFIG_JOGO.get("coop_local") and player2 is None:
        player2 = Jogador(440, 300, numero_jogador=2)
        player2.classe = "RASTREADOR"
        status_jogador2 = GerenciadorStatus()
    elif not CONFIG_JOGO.get("coop_local"):
        player2 = None


def ativar_perfil_selecionado():
    global dados_salvos, controles_jogo, player, player2, pet_ativo
    global status_jogador, status_jogador2
    dados_salvos = carregar_dados()
    CONFIG_JOGO.clear()
    CONFIG_JOGO.update(copy.deepcopy(CONFIG_JOGO_PADRAO))
    configuracoes = dados_salvos.get("configuracoes", {})
    if isinstance(configuracoes, dict):
        CONFIG_JOGO.update(configuracoes)
    if CONFIG_JOGO.get("raca_jogador") not in RACES_AND_CLASSES["races"]:
        CONFIG_JOGO["raca_jogador"] = "Humano"
    if CONFIG_JOGO.get("classe_jogador") not in RACES_AND_CLASSES["classes"]:
        CONFIG_JOGO["classe_jogador"] = "Guerreiro"
    controles_jogo = normalizar_controles(CONFIG_JOGO)
    audio.atualizar_volumes(CONFIG_JOGO)
    player = Jogador(400, 300)
    player2 = Jogador(440, 300, numero_jogador=2) if CONFIG_JOGO.get("coop_local") else None
    status_jogador = GerenciadorStatus()
    status_jogador2 = GerenciadorStatus()
    pet_ativo = preparar_pet(player)
    conquistas_mgr.dados = dados_salvos


def salvar_configuracao():
    dados = carregar_dados()
    dados["configuracoes"] = {
        chave: valor for chave, valor in CONFIG_JOGO.items()
        if chave in ("idioma", "modo_tiro", "volume_musica", "volume_sfx", "modo_dificuldade",
                     "raca_jogador", "classe_jogador", "coop_local", "fullscreen", "controles",
                     "mostrar_missoes", "mostrar_efeitos", "modificadores_run")
    }
    salvar_dados(dados)


def recriar_tela():
    global tela
    flags = pygame.FULLSCREEN if CONFIG_JOGO.get("fullscreen") else 0
    tela = pygame.display.set_mode((LARGURA, ALTURA), flags)


def registrar_fim_run():
    global run_registrada, melhores_runs_cache
    if run_registrada:
        return
    estatisticas_run["andar_morte"] = max(estatisticas_run.get("andar_morte", 1), andar_atual)
    conquistas_mgr.dados = carregar_dados()
    conquistas_mgr.registrar_run(
        estatisticas_run, obter_modo_dificuldade(), player2 is not None
    )
    registrar_run(estatisticas_run, obter_modo_dificuldade(), player2 is not None)
    melhores_runs_cache = obter_melhores_runs_por_dificuldade()
    run_registrada = True


def preparar_pet(jogador):
    dados = carregar_dados()
    tipo = dados.get("pet_equipado")
    jogador.configurar_pet(tipo)
    return Pet(tipo, *jogador.rect.center) if tipo else None


def marcar_inicio_sala(sala):
    sala.sem_dano = True
    sala.recompensa_sem_dano_concedida = False
    sala.estatisticas_registradas = False
    sala.dano_inicio_sala = sum(
        getattr(alvo, "dano_recebido_total", 0)
        for alvo in (player, player2) if alvo
    )


def angulo_para_ataque_melee(jogador, inimigos, pos_mouse, modo_tiro):
    if modo_tiro == "MANUAL":
        dx = pos_mouse[0] - jogador.rect.centerx
        dy = pos_mouse[1] - jogador.rect.centery
    elif inimigos:
        alvo = min(
            inimigos,
            key=lambda inimigo: math.hypot(
                inimigo["rect"].centerx - jogador.rect.centerx,
                inimigo["rect"].centery - jogador.rect.centery,
            ),
        )
        dx = alvo["rect"].centerx - jogador.rect.centerx
        dy = alvo["rect"].centery - jogador.rect.centery
    else:
        dx, dy = math.cos(math.radians(jogador.angulo_olhando)), -math.sin(
            math.radians(jogador.angulo_olhando)
        )
    return math.atan2(dy, dx)


def alcance_arma_melee(arma):
    alcance_definido = arma.get("alcance")
    if alcance_definido is not None:
        return max(40, float(alcance_definido))

    nome = arma.get("nome", "").casefold()
    if any(palavra in nome for palavra in ("adaga", "faca", "estilete", "punhal")):
        return 75
    if any(palavra in nome for palavra in ("lança", "lanca", "glaive", "alabarda", "foice")):
        return 155
    if any(palavra in nome for palavra in ("duas mãos", "duas maos", "grande", "montante")):
        return 145
    if any(palavra in nome for palavra in ("machado", "martelo", "maça", "maca", "clava", "mangual")):
        return 115
    return 125


def danificar_obstaculo(sala, obstaculo, dano, dono):
    if obstaculo.get("tipo") not in ("caixa", "vaso", "terminal"):
        return False
    obstaculo["vida"] = obstaculo.get("vida", 1) - max(1, int(dano // 25))
    if obstaculo["vida"] > 0:
        return False
    if obstaculo in sala.obstaculos:
        sala.obstaculos.remove(obstaculo)
    recompensa = {"caixa": 10, "vaso": 15, "terminal": 25}.get(
        obstaculo.get("tipo"), 10
    )
    dono.ganhar_ouro(recompensa)
    particulas.criar_texto_dano(
        obstaculo["rect"].centerx, obstaculo["rect"].y - 12,
        f"+{recompensa} {t('ouro', CONFIG_JOGO.get('idioma', 'PT'))}",
        AMARELO,
    )
    return True


def tentar_invocar_sombra(jogador, arma, inimigo, agora):
    if (
        (arma or {}).get("mitica_id") != "adaga_sombra"
        or inimigo.get("hp", 1) > 0
        or inimigo.get("sombra_invocada")
        or random.random() >= 0.18
    ):
        return
    inimigo["sombra_invocada"] = True
    tipo = random.choice(("tank", "curandeiro", "dps"))
    jogador.soldados_sombra.append({
        "tipo": tipo, "fim": agora + 10000, "proximo_ataque": agora,
        "x": inimigo["rect"].centerx, "y": inimigo["rect"].centery,
    })
    jogador.soldados_sombra = jogador.soldados_sombra[-3:]
    particulas.criar_texto_dano(
        inimigo["rect"].centerx, inimigo["rect"].y - 14,
        "SOMBRA ERGUIDA", ROXO_UI,
    )


def alvo_melee_automatico(jogador, inimigos, arma):
    alcance = alcance_arma_melee(arma)
    alvos_no_alcance = []
    for inimigo in inimigos:
        rect = inimigo.get("rect")
        if rect is None:
            continue
        dx = rect.centerx - jogador.rect.centerx
        dy = rect.centery - jogador.rect.centery
        raio_alvo = max(rect.width, rect.height) / 2
        if math.hypot(dx, dy) <= alcance + raio_alvo:
            alvos_no_alcance.append((dx * dx + dy * dy, inimigo))
    return min(alvos_no_alcance, key=lambda entrada: entrada[0])[1] if alvos_no_alcance else None


def inimigo_no_cone_melee(inimigo, jogador, angulo, alcance, meia_abertura=0.62):
    dx = inimigo["rect"].centerx - jogador.rect.centerx
    dy = inimigo["rect"].centery - jogador.rect.centery
    distancia = math.hypot(dx, dy)
    raio_inimigo = max(inimigo["rect"].width, inimigo["rect"].height) / 2
    if distancia > alcance + raio_inimigo:
        return False
    angulo_inimigo = math.atan2(dy, dx)
    diferenca = (angulo_inimigo - angulo + math.pi) % (2 * math.pi) - math.pi
    return abs(diferenca) <= meia_abertura


def bonus_encantamento(arma, atributo):
    return sum(enc.get(atributo, 0) for enc in (arma or {}).get("encantamentos", []))


def registrar_fragmento_bioma(bioma_id):
    global historia_aviso, historia_aviso_tempo
    if desbloquear_fragmento(bioma_id):
        historia_aviso = texto_fragmento(bioma_id, CONFIG_JOGO.get("idioma", "PT"))
        historia_aviso_tempo = pygame.time.get_ticks()


def aplicar_efeitos_encantamento(arma, inimigo, jogador, dano, tempo_atual):
    for encantamento in (arma or {}).get("encantamentos", []):
        efeito = encantamento.get("efeito")
        if efeito == "sangramento":
            inimigo["sangramento_fim"] = max(inimigo.get("sangramento_fim", 0), tempo_atual + 3500)
            inimigo["sangramento_tick"] = tempo_atual
        elif efeito == "congelamento":
            inimigo["congelado_fim"] = max(inimigo.get("congelado_fim", 0), tempo_atual + 900)
        elif efeito in ("queimadura", "veneno"):
            inimigo["encantamento_dot"] = {
                "tipo": efeito,
                "dano": max(5, arredondar_para_5(dano * 0.08)),
                "fim": tempo_atual + 3000,
                "proximo": tempo_atual,
            }
    nome_arma = (arma or {}).get("nome", "").casefold()
    if (
        getattr(jogador, "classe", None) == "Ladrão"
        and any(palavra in nome_arma for palavra in ("adaga", "punhal", "daga"))
        and random.random() < 0.65
    ):
        inimigo["sangramento_fim"] = max(
            inimigo.get("sangramento_fim", 0), tempo_atual + 4500
        )
        inimigo["sangramento_tick"] = tempo_atual
    roubo = min(0.35, bonus_encantamento(arma, "roubo_vida"))
    cura = max(0, int(dano * roubo))
    if cura:
        jogador.hp = min(jogador.hp_max, jogador.hp + cura)


def usar_magia(jogador, indice, tempo_atual):
    mitica_id = arma_mitica_id(jogador.equipado_arma)
    if usar_habilidade_mitica(
        jogador, indice, tempo_atual, pygame.mouse.get_pos(),
        sala_atual.inimigos, projeteis, particulas, audio, estatisticas_run,
        lambda arma, alvo, mult: dano_arma(arma, alvo, mult),
    ):
        if mitica_id:
            conjuracao = getattr(jogador, "conjuracao_explosao", None)
            if conjuracao:
                particulas.criar_texto_dano(
                    jogador.rect.centerx, jogador.rect.y - 24,
                    t("explosao_conjurando", lang).format(segundos="0.8"),
                    LARANJA, True,
                )
                return
            particulas.criar_texto_dano(
                jogador.rect.centerx, jogador.rect.y - 24,
                t(f"mitica_{mitica_id}_{indice}", lang), ROXO_UI, True,
            )
        return
    if indice == 3:
        usar_habilidade_suprema(jogador, tempo_atual)
        return
    arma = jogador.equipado_arma
    if not arma or arma.get("tipo_arma") != "mage":
        particulas.criar_texto_dano(
            jogador.rect.centerx, jogador.rect.y - 15, t("precisa_cajado", lang), AMARELO
        )
        return
    custos = (10, 30, 70)
    danos = (30, 60, 120)
    raios = (150, 200, 250)
    custo = custo_mana_com_sinergia(jogador, custos[indice])
    if jogador.mana < custo:
        particulas.criar_texto_dano(
            jogador.rect.centerx, jogador.rect.y - 15, t("mana_insuficiente", lang), CIANO
        )
        return
    jogador.mana -= custo
    audio.tocar_som("magia")
    particulas.criar_texto_dano(
        jogador.rect.centerx, jogador.rect.y - 15,
        f"Feitiço {indice + 1} (-{custo})", CIANO,
    )
    for inimigo in sala_atual.inimigos:
        distancia = math.hypot(
            inimigo["rect"].centerx - jogador.rect.centerx,
            inimigo["rect"].centery - jogador.rect.centery,
        )
        if distancia <= raios[indice]:
            critico = random.random() < jogador.chance_crit
            dano = dano_magia_base(jogador, danos[indice], critico, tempo_atual)
            dano_aplicado = aplicar_dano_inimigo(
                inimigo, dano, critico, tempo_atual, audio, estatisticas_run
            )
            acumular_carga_suprema(jogador, dano_aplicado)
    if arma.get("mitica_id") == "cajado_explosao":
        jogador.poder_mantra = min(100, getattr(jogador, "poder_mantra", 0) + 10)


def acumular_carga_suprema(jogador, dano):
    if dano > 0:
        jogador.carga_suprema = min(
            100.0, getattr(jogador, "carga_suprema", 0.0) + min(10.0, dano * 0.05)
        )


def usar_habilidade_suprema(jogador, tempo_atual):
    carga = getattr(jogador, "carga_suprema", 0.0)
    if carga < 100:
        particulas.criar_texto_dano(
            jogador.rect.centerx, jogador.rect.y - 15,
            t("ultimate_carga", lang).format(valor=int(carga)), CIANO,
        )
        return

    classe = getattr(jogador, "classe", "Guerreiro")
    if classe not in RACES_AND_CLASSES["classes"]:
        classe = "Atirador"
    inimigos = list(sala_atual.inimigos)
    if not inimigos:
        particulas.criar_texto_dano(
            jogador.rect.centerx, jogador.rect.y - 15, t("ultimate_sem_alvo", lang), AMARELO
        )
        return

    jogador.carga_suprema = 0
    audio.tocar_som("magia")
    chave_classe = {
        "Guerreiro": "guerreiro",
        "Espadachim": "espadachim",
        "Mago": "mago",
        "Atirador": "atirador",
        "Caçador": "cacador",
        "Ladrão": "ladrao",
    }[classe]
    particulas.criar_texto_dano(
        jogador.rect.centerx, jogador.rect.y - 20,
        t("ultimate_" + chave_classe, lang), DOURADO_UI,
    )

    alvos = inimigos
    if classe == "Atirador":
        alvos = sorted(
            inimigos,
            key=lambda inimigo: math.dist(jogador.rect.center, inimigo["rect"].center),
        )[:4]
    elif classe == "Ladrão":
        alvos = [min(
            inimigos,
            key=lambda inimigo: math.dist(jogador.rect.center, inimigo["rect"].center),
        )]

    dano_base = {
        "Guerreiro": 210,
        "Espadachim": 190,
        "Mago": 270,
        "Atirador": 155,
        "Caçador": 105,
        "Ladrão": 290,
    }[classe]
    curou = 0
    for inimigo in alvos:
        distancia = math.dist(jogador.rect.center, inimigo["rect"].center)
        if classe == "Guerreiro" and distancia > 175:
            continue
        if classe == "Espadachim":
            if distancia > 260:
                continue
            dx = inimigo["rect"].centerx - jogador.rect.centerx
            dy = inimigo["rect"].centery - jogador.rect.centery
            angulo_alvo = math.degrees(math.atan2(-dy, dx))
            diferenca = abs((angulo_alvo - jogador.angulo_olhando + 180) % 360 - 180)
            if diferenca > 85:
                continue
        if classe == "Atirador" and distancia > 520:
            continue
        if classe == "Caçador" and distancia > 430:
            continue
        if classe == "Ladrão" and distancia > 340:
            continue
        critico = random.random() < jogador.chance_crit
        dano = dano_magia_base(jogador, dano_base, critico, tempo_atual)
        aplicado = aplicar_dano_inimigo(
            inimigo, dano, critico, tempo_atual, audio, estatisticas_run
        )
        aplicar_efeitos_encantamento(
            jogador.equipado_arma, inimigo, jogador, aplicado, tempo_atual
        )
        particulas.criar_explosao(
            inimigo["rect"].centerx, inimigo["rect"].centery, ROXO_UI
        )
        if classe == "Caçador" and aplicado:
            inimigo["congelado_fim"] = max(
                inimigo.get("congelado_fim", 0), tempo_atual + 2600
            )
        if classe == "Ladrão":
            curou += max(0, int(aplicado * 0.15))
    if curou:
        jogador.hp = min(jogador.hp_max, jogador.hp + curou)


def dano_magia_base(jogador, dano, critico, tempo_atual):
    mult_critico = jogador.mult_crit if critico else 1.0
    mult_raca = getattr(jogador, "multiplicador_raca_classe", 1.0)
    evento = getattr(jogador, "evento_bioma_ativo", None)
    mult_evento = 1 + evento.get("dano", 0) if evento and tempo_atual < evento.get("fim", 0) else 1.0
    return max(
        5,
        int(
            dano * mult_critico * mult_raca * mult_evento
            * getattr(jogador, "multiplicador_dano_cosmetico", 1.0)
        ),
    )


def dano_arma(arma, jogador, multiplicador_dano):
    bonus = bonus_encantamento(arma, "dano_percentual")
    mastery = bonus_maestria(arma.get("tipo_arma", "melee"))
    dano = (
        arma["dano"]
        * (1 + jogador.bonus_dano_percent + mastery + bonus)
        * multiplicador_dano
        * getattr(jogador, "multiplicador_raca_classe", 1.0)
        * getattr(jogador, "multiplicador_dano_cosmetico", 1.0)
    )
    if arma.get("mitica_id") == "espada_berserk":
        vida = max(0.0, min(1.0, jogador.hp / max(1, jogador.hp_max)))
        dano *= 1 + (1 - vida) * 1.25
    if (
        arma.get("mitica_id") == "adaga_sombra"
        and pygame.time.get_ticks() < getattr(jogador, "bonus_dano_sombra_ate", 0)
    ):
        dano *= 1.2
    if arma.get("mitica_id") == "espada_berserk":
        if any(
            sombra["tipo"] == "dps"
            and sombra["fim"] > pygame.time.get_ticks()
            for sombra in getattr(jogador, "soldados_sombra", [])
        ):
            dano *= 1.15
    if pygame.time.get_ticks() < getattr(jogador, "parry_crit_ate", 0):
        dano *= 1.5
    critico = random.random() < min(0.85, jogador.chance_crit + bonus_encantamento(arma, "critico"))
    if pygame.time.get_ticks() < getattr(jogador, "parry_crit_ate", 0):
        critico = random.random() < min(0.95, jogador.chance_crit * 2)
    if critico:
        dano *= jogador.mult_crit
    return max(5, arredondar_para_5(dano)), critico


def desenhar_cone_corte(tela, jogador, angulo, alcance, tempo_fim, tempo_atual):
    duracao = 220
    restante = max(0, tempo_fim - tempo_atual)
    if restante <= 0:
        return
    progresso = 1 - restante / duracao
    alcance_animacao = alcance * (0.65 + 0.35 * math.sin(progresso * math.pi))
    meia_abertura = 0.62
    centro = jogador.rect.center
    pontos = [centro]
    for indice in range(13):
        angulo_ponto = angulo - meia_abertura + 2 * meia_abertura * indice / 12
        pontos.append(
            (
                int(centro[0] + math.cos(angulo_ponto) * alcance_animacao),
                int(centro[1] + math.sin(angulo_ponto) * alcance_animacao),
            )
        )
    efeito = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    pygame.draw.polygon(efeito, (185, 190, 200, 105), pontos)
    pygame.draw.lines(efeito, (225, 230, 240, 220), False, pontos[1:], 4)
    pygame.draw.line(efeito, (225, 230, 240, 180), centro, pontos[1], 2)
    pygame.draw.line(efeito, (225, 230, 240, 180), centro, pontos[-1], 2)
    tela.blit(efeito, (0, 0))


def desenhar_hud_mitica(surface, jogador, tempo_atual, idioma):
    mitica_id = arma_mitica_id(jogador.equipado_arma)
    habilidade = HABILIDADES_MITICAS.get(mitica_id)
    if not habilidade:
        return
    slots = habilidade["slots"]
    largura_slot, altura_slot, espacamento = 72, 54, 8
    inicio_x = LARGURA - 14 - len(slots) * largura_slot - (len(slots) - 1) * espacamento
    y = ALTURA - altura_slot - 10
    for coluna, indice in enumerate(slots):
        rect = pygame.Rect(
            inicio_x + coluna * (largura_slot + espacamento), y,
            largura_slot, altura_slot,
        )
        cooldown_ate = jogador.cooldowns_miticos.get(indice, 0)
        restante = max(0, cooldown_ate - tempo_atual)
        custo = habilidade["custos"][indice]
        indisponivel = restante > 0 or jogador.mana < custo
        pygame.draw.rect(
            surface, PAINEL_UI_CLARO if not indisponivel else (28, 30, 40),
            rect, border_radius=7,
        )
        pygame.draw.rect(
            surface, CIANO_UI if not indisponivel else BORDA_UI,
            rect, 1, border_radius=7,
        )
        tecla = ("H", "J", "K", "L")[indice]
        label = FONTE_PEQUENA.render(
            f"[{tecla}] {t(f'mitica_{mitica_id}_{indice}', idioma)}",
            True, BRANCO if not indisponivel else CINZA_CLARO,
        )
        surface.blit(label, (rect.x + 4, rect.y + 5))
        mana_label = FONTE_PEQUENA.render(
            f"{custo} MP", True, CIANO_UI if jogador.mana >= custo else CINZA_CLARO
        )
        surface.blit(mana_label, (rect.x + 4, rect.bottom - 16))
        if restante:
            mascara = pygame.Surface(rect.size, pygame.SRCALPHA)
            mascara.fill((5, 7, 14, 175))
            surface.blit(mascara, rect.topleft)
            segundos = FONTE_SYS.render(f"{restante / 1000:.1f}", True, BRANCO)
            surface.blit(
                segundos,
                (rect.centerx - segundos.get_width() // 2,
                 rect.centery - segundos.get_height() // 2),
            )


pet_ativo = preparar_pet(player)

estado_jogo = "MENU_INICIAL"
ordem_biomas = list(BIOMAS_ESTETICA)
random.shuffle(ordem_biomas)
andar_atual = 1
bioma_atual = ordem_biomas[0]
sala_atual, mapa_salas = gerar_andar(bioma_atual, andar_atual)
marcar_inicio_sala(sala_atual)

tempo_ultimo_tiro = 0
controle_combate = ControleCombate()
ultimo_estado_ataque = False
ultimo_estado_defesa = False
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
    "andar_morte": 1,
    "elites_derrotados": 0,
    "inimigos_raros_derrotados": 0,
    "dano_causado": 0,
    "salas_concluidas": 0,
    "salas_sem_dano": 0,
    "chefes_secretos_derrotados": 0,
    "contrato": iniciar_contrato(1),
    "desafio_diario": estado_desafio_diario(),
}

intro_timer = 0
exibir_intro_andar = False
confirmacao_tipo = None
estado_config_retorno = "MENU_INICIAL"
infinito_ativo = False
mensagem_aviso = ""
tempo_aviso = 0


def interagir_bau(tecla, jogador=None):
    jogador = jogador or player
    if sala_atual.interagir_obstaculo(jogador, particulas):
        audio.tocar_som("bau")
        return True
    if sala_atual.tipo not in ("RECOMPENSA", "MIMICO", "TESOURO", "OVERCLOCK") or not sala_atual.baus:
        return False
    if tecla in (pygame.K_1, pygame.K_2):
        indice = tecla - pygame.K_1
    else:
        indice = min(
            range(len(sala_atual.baus)),
            key=lambda i: math.dist(jogador.rect.center, sala_atual.baus[i]["rect"].center),
        )
        if math.dist(jogador.rect.center, sala_atual.baus[indice]["rect"].center) > 95:
            return False
    hp_antes = jogador.hp
    tipo_sala = sala_atual.tipo
    aberto = sala_atual.interagir_bau(indice, jogador, particulas, CONFIG_JOGO.get("idioma", "PT"))
    if aberto:
        if tipo_sala == "MIMICO":
            audio.tocar_som("invocacao")
        elif jogador.hp > hp_antes:
            audio.tocar_som("cura")
        else:
            audio.tocar_som("bau")
    return aberto


def atualizar_obstaculos():
    jogadores = (
        (player, status_jogador, "ultimo_dano_p1"),
        (player2, status_jogador2, "ultimo_dano_p2"),
    )
    for obstaculo in sala_atual.obstaculos[:]:
        tipo = obstaculo["tipo"]
        if tipo == "bomba" and not obstaculo["armada"]:
            if any(
                alvo and alvo.hp > 0
                and math.dist(alvo.rect.center, obstaculo["rect"].center) < 58
                for alvo, _, _ in jogadores
            ):
                obstaculo["armada"] = True
                obstaculo["detonar_em"] = tempo_atual + 900
        if tipo == "espinhos":
            for alvo, status, chave in jogadores:
                if (
                    alvo and alvo.hp > 0 and alvo.rect.colliderect(obstaculo["rect"])
                    and tempo_atual - obstaculo[chave] >= 1100
                ):
                    obstaculo[chave] = tempo_atual
                    aplicar_dano_player(
                        alvo, particulas, 10, tempo_atual, status,
                        efeito="lentidao", duracao_efeito=700, audio_manager=audio,
                    )
        if tipo == "bomba" and obstaculo["armada"] and tempo_atual >= obstaculo["detonar_em"]:
            centro = obstaculo["rect"].center
            for alvo, status, _ in jogadores:
                if alvo and alvo.hp > 0 and math.dist(alvo.rect.center, centro) <= 105:
                    aplicar_dano_player(
                        alvo, particulas, 30, tempo_atual, status,
                        efeito="queimadura", duracao_efeito=1800, audio_manager=audio,
                    )
            for inimigo in sala_atual.inimigos[:]:
                if math.dist(inimigo["rect"].center, centro) <= 105:
                    inimigo["hp"] -= 45
            particulas.criar_explosao(centro[0], centro[1], AMARELO)
            sala_atual.obstaculos.remove(obstaculo)


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

def avancar_andar():
    global andar_atual, bioma_atual, sala_atual, mapa_salas
    global exibir_intro_andar, intro_timer, inimigos_mgr, estado_jogo
    if andar_atual % len(ordem_biomas) == 0:
        bioma_anterior = bioma_atual
        random.shuffle(ordem_biomas)
        if len(ordem_biomas) > 1 and ordem_biomas[0] == bioma_anterior:
            ordem_biomas[0], ordem_biomas[1] = ordem_biomas[1], ordem_biomas[0]
    registrar_progresso(carregar_dados(), "andar")
    andar_atual += 1
    bioma_atual = ordem_biomas[(andar_atual - 1) % len(ordem_biomas)]
    registrar_fragmento_bioma(bioma_atual)
    sala_atual, mapa_salas = gerar_andar(bioma_atual, andar_atual)
    marcar_inicio_sala(sala_atual)
    inimigos_mgr = GerenciadorInimigos()
    projeteis.clear()
    projeteis_inimigos.clear()
    player.rect.center = (LARGURA // 2, ALTURA // 2)
    estatisticas_run["contrato"] = iniciar_contrato(andar_atual)
    exibir_intro_andar = True
    intro_timer = pygame.time.get_ticks()
    estado_jogo = "JOGANDO"

rodando = True
modo_musica_atual = None
ultima_troca_musica = 0
while rodando:
    sincronizar_jogador2()
    tempo_atual = pygame.time.get_ticks()
    relogio.tick(60)
    pos_mouse = pygame.mouse.get_pos()
    clicou = False
    evento_tecla = None
    lang = CONFIG_JOGO.get('idioma', 'PT')
    controles_jogo = normalizar_controles(CONFIG_JOGO)
    audio.atualizar_volumes(CONFIG_JOGO)
    joysticks = []
    for indice_joystick in range(pygame.joystick.get_count()):
        joystick = pygame.joystick.Joystick(indice_joystick)
        if not joystick.get_init():
            joystick.init()
        joysticks.append(joystick)
    if estado_jogo in ("MENU_INICIAL", "NPC_HUB", "CONFIGURACOES", "GAME_OVER"):
        modo_musica = "menu"
    else:
        chefao = next(
            (inimigo for inimigo in sala_atual.inimigos if inimigo.get("tipo") == "boss"),
            None,
        )
        jogadores_vivos = [jogador for jogador in (player, player2) if jogador and jogador.hp > 0]
        vida_baixa = bool(jogadores_vivos) and min(
            jogador.hp / max(1, jogador.hp_max) for jogador in jogadores_vivos
        ) <= 0.30
        em_perigo = any(
            math.dist(inimigo["rect"].center, jogador.rect.center) < 260
            for inimigo in sala_atual.inimigos
            for jogador in jogadores_vivos
        )
        if chefao and chefao.get("fase_atual", 1) >= 2:
            modo_musica = "chefe_fase"
        elif chefao:
            modo_musica = "chefe"
        elif vida_baixa:
            modo_musica = "vida_baixa"
        elif em_perigo:
            modo_musica = "perigo"
        else:
            modo_musica = "exploracao"
    if modo_musica != modo_musica_atual and (
        modo_musica_atual is None
        or modo_musica == "menu"
        or pygame.time.get_ticks() - ultima_troca_musica >= 2500
    ):
        if modo_musica == "menu":
            audio.tocar_musica("menu")
        else:
            audio.tocar_musica_dinamica(bioma_atual, modo_musica)
        modo_musica_atual = modo_musica
        ultima_troca_musica = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN and estado_jogo == "JOGANDO":
            if event.button == 1 and CONFIG_JOGO.get("modo_tiro") == "MANUAL":
                controle_combate.iniciar_ataque(tempo_atual)
                continue
            if event.button == 3:
                controle_combate.ativar_escudo(tempo_atual)
                continue
        if (
            event.type == pygame.MOUSEBUTTONUP
            and event.button == 1
            and estado_jogo == "JOGANDO"
            and CONFIG_JOGO.get("modo_tiro") == "MANUAL"
        ):
            controle_combate.soltar_ataque(tempo_atual)
            continue
        touch_consumido, teclas_touch = controles_touch.processar_evento(
            event, tela, estado_jogo == "JOGANDO"
        )
        for tecla_touch in teclas_touch:
            pygame.event.post(pygame.event.Event(
                pygame.KEYDOWN, key=tecla_touch, unicode="",
            ))
        if touch_consumido:
            continue
        if event.type == pygame.QUIT:
            rodando = False
        if event.type == pygame.JOYBUTTONDOWN and estado_jogo == "CONFIGURACOES":
            if menu_config.capturar_botao_controle(event, CONFIG_JOGO):
                salvar_configuracao()
                continue
        if event.type == pygame.JOYBUTTONDOWN and estado_jogo == "JOGANDO":
            jogadores_controle = [(0, "P1", player)]
            if player2:
                jogadores_controle.append((min(1, max(0, len(joysticks) - 1)), "P2", player2))
            for indice_joystick, chave_jogador, jogador_controle in jogadores_controle:
                config_controle = controles_jogo[chave_jogador]
                if (
                    config_controle["dispositivo"] != "controle"
                    or event.joy != indice_joystick
                    or jogador_controle.hp <= 0
                ):
                    continue
                botoes = config_controle.get("botoes", {})
                mapa_botoes = {
                    acao: botoes.get(acao, padrao)
                    for acao, padrao in {
                        "interagir": 2, "magia_1": 3, "magia_2": 4,
                        "magia_3": 5, "magia_4": 6,
                    }.items()
                }
                if event.button == mapa_botoes["interagir"]:
                    if chave_jogador == "P1":
                        if not interagir_bau(pygame.K_e):
                            if sala_atual.tipo == "OVERCLOCK":
                                evento_interacao = pygame.event.Event(
                                    pygame.KEYDOWN, key=pygame.K_e, unicode="e"
                                )
                                sala_atual.desenhar_conteudo_especial(
                                    tela, player, evento_interacao, particulas,
                                    status_jogador, player2,
                                )
                            elif sala_atual.tipo == "IMPOSTOR":
                                evento_interacao = pygame.event.Event(
                                    pygame.KEYDOWN, key=pygame.K_e, unicode="e"
                                )
                                sala_atual.desenhar_conteudo_especial(
                                    tela, player, evento_interacao, particulas,
                                    status_jogador, player2,
                                )
                            elif sala_atual.tipo in ("RECOMPENSA", "MIMICO", "TESOURO"):
                                pass
                            elif sala_atual.tipo in ("RESGATE", "NPC_ENCONTRO", "REVIVER_P2", "ENIGMA", "OBELISCO", "POCO", "RITUAL"):
                                evento_interacao = pygame.event.Event(
                                    pygame.KEYDOWN, key=pygame.K_1, unicode="1"
                                )
                                sala_atual.desenhar_conteudo_especial(
                                    tela, player, evento_interacao, particulas,
                                    status_jogador, player2,
                                )
                            else:
                                estado_jogo = "INVENTARIO"
                    else:
                        if sala_atual.tipo in ("OVERCLOCK", "IMPOSTOR") and not interagir_bau(pygame.K_e, jogador_controle):
                            evento_interacao = pygame.event.Event(
                                pygame.KEYDOWN, key=pygame.K_e, unicode="e"
                            )
                            sala_atual.desenhar_conteudo_especial(
                                tela, player, evento_interacao, particulas,
                                status_jogador, player2,
                            )
                        elif sala_atual.tipo in ("RESGATE", "NPC_ENCONTRO", "REVIVER_P2", "ENIGMA", "OBELISCO", "POCO", "RITUAL"):
                            evento_interacao = pygame.event.Event(
                                pygame.KEYDOWN, key=pygame.K_1, unicode="1"
                            )
                            sala_atual.desenhar_conteudo_especial(
                                tela, player, evento_interacao, particulas,
                                status_jogador, player2,
                            )
                        else:
                            interagir_bau(pygame.K_e, jogador_controle)
                elif chave_jogador == "P1":
                    teclas_magia = {
                        mapa_botoes["magia_1"]: pygame.K_h,
                        mapa_botoes["magia_2"]: pygame.K_j,
                        mapa_botoes["magia_3"]: pygame.K_k,
                        mapa_botoes["magia_4"]: pygame.K_l,
                    }
                    if event.button in teclas_magia:
                        pygame.event.post(pygame.event.Event(
                            pygame.KEYDOWN,
                            key=teclas_magia[event.button],
                            unicode="",
                        ))
                else:
                    indice_magia = {
                        mapa_botoes["magia_1"]: 0,
                        mapa_botoes["magia_2"]: 1,
                        mapa_botoes["magia_3"]: 2,
                        mapa_botoes["magia_4"]: 3,
                    }.get(event.button)
                    if indice_magia is not None:
                        usar_magia(jogador_controle, indice_magia, tempo_atual)
        if event.type == pygame.MOUSEWHEEL and estado_jogo == "MISSOES":
            missoes_tela.tratar_evento(event)
        if event.type == pygame.MOUSEWHEEL and estado_jogo == "INDEX":
            index_tela.tratar_evento(event, pos_mouse)
        elif event.type == pygame.MOUSEWHEEL and estado_jogo == "CONQUISTAS":
            tela_conquistas.tratar_evento(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if (
                IS_MOBILE
                and controles_touch.eh_botao_touch(
                    event.pos, tela, estado_jogo == "JOGANDO"
                )
            ):
                continue
            if event.button == 1: 
                audio.tocar_som("menu")
                clicou = True
                if estado_jogo == "MENU_INICIAL":
                    res = menu_inicial.tratar_clique(pos_mouse, CONFIG_JOGO)
                    if res == "PERFIL_TROCADO":
                        ativar_perfil_selecionado()
                    elif res == "IR_NPCS":
                        estado_jogo = "NPC_HUB"
                    if estado_jogo == "NPC_HUB":
                        continue
                    if res == "INICIAR_RUN":
                        def reset_game():
                            global andar_atual, bioma_atual, ordem_biomas, sala_atual, mapa_salas, estado_jogo, exibir_intro_andar, intro_timer, estatisticas_run, player, player2, tempo_inicio_run, inimigos_mgr, projeteis, projeteis_inimigos, status_jogador, status_jogador2, pet_ativo, infinito_ativo, run_registrada, ultimo_ataque_p2, mobs_missoes_reportados, elites_missoes_reportados, modo_espectador
                            ordem_biomas = list(BIOMAS_ESTETICA)
                            random.shuffle(ordem_biomas)
                            andar_atual = 1
                            bioma_atual = ordem_biomas[0]
                            player = Jogador(400, 300)
                            player2 = Jogador(440, 300, numero_jogador=2) if CONFIG_JOGO.get("coop_local") else None
                            dados_pre_run = carregar_dados()
                            servicos_npc = dados_pre_run.pop("preparacao_npc_run", {})
                            if servicos_npc:
                                salvar_dados(dados_pre_run)
                                for jogador_preparado in (player, player2):
                                    if jogador_preparado:
                                        aplicar_servicos_npc(jogador_preparado, servicos_npc)
                            registrar_fragmento_bioma(bioma_atual)
                            pet_ativo = preparar_pet(player)
                            inimigos_mgr = GerenciadorInimigos()
                            projeteis = []
                            projeteis_inimigos = []
                            status_jogador = GerenciadorStatus()
                            status_jogador2 = GerenciadorStatus()
                            ultimo_ataque_p2 = 0
                            run_registrada = False
                            mobs_missoes_reportados = 0
                            elites_missoes_reportados = 0
                            tempo_inicio_run = time.time()
                            sala_atual, mapa_salas = gerar_andar(bioma_atual, andar_atual)
                            marcar_inicio_sala(sala_atual)
                            estatisticas_run = {"mobs_mortos": 0, "gemas_coletadas": 0, "tempo_segundos": 0, "andar_morte": 1, "elites_derrotados": 0, "inimigos_raros_derrotados": 0, "dano_causado": 0, "salas_concluidas": 0, "salas_sem_dano": 0, "chefes_secretos_derrotados": 0, "contrato": iniciar_contrato(1), "desafio_diario": estado_desafio_diario(), "modificadores": list(CONFIG_JOGO.get("modificadores_run", []))}
                            infinito_ativo = False
                            estado_jogo = "JOGANDO"
                            modo_espectador = False
                            exibir_intro_andar = True
                            intro_timer = tempo_atual
                        iniciar_transicao(reset_game)
                    elif res == "IR_INDEX":
                        estado_jogo = "INDEX"
                    elif res == "IR_CONQUISTAS":
                        estado_jogo = "CONQUISTAS"
                    elif res == "IR_MISSOES":
                        estado_missoes_retorno = "MENU_INICIAL"
                        estado_jogo = "MISSOES"
                    elif res == "IR_HISTORIA":
                        estado_jogo = "HISTORIA"
                    elif res == "IR_CONFIG":
                        estado_config_retorno = "MENU_INICIAL"
                        estado_jogo = "CONFIGURACOES"
                    elif res == "ABRIR_DISCORD":
                        webbrowser.open_new_tab("https://discord.gg/zsXp6Nf6zF")
                    elif res == "SAIR":
                        rodando = False
                elif estado_jogo == "NPC_HUB":
                    acao_hub = hub_npcs.tratar_clique(pos_mouse)
                    if acao_hub == "VOLTAR":
                        estado_jogo = "MENU_INICIAL"
                    elif acao_hub == "COMPRAR":
                        _, chave_aviso = comprar_servico_npc(hub_npcs.alvo_npc)
                        hub_npcs.aviso = t(chave_aviso, lang)
                    elif acao_hub == "EVOLUIR_PET":
                        hub_npcs.aviso = hub_npcs.evoluir_pet(lang)
                elif estado_jogo == "INDEX":
                    acao_index = index_tela.tratar_evento(event, pos_mouse)
                    if acao_index == "VOLTAR_LOBBY":
                        estado_jogo = "MENU_INICIAL"
                elif estado_jogo == "CONQUISTAS":
                    if tela_conquistas.tratar_clique(pos_mouse) == "VOLTAR":
                        estado_jogo = "MENU_INICIAL"
                elif estado_jogo == "MISSOES":
                    acao_missao = missoes_tela.tratar_clique(pos_mouse)
                    if acao_missao == "VOLTAR":
                        estado_jogo = estado_missoes_retorno
                elif estado_jogo == "HISTORIA":
                    btn_voltar_historia = pygame.Rect(LARGURA // 2 - 110, ALTURA - 58, 220, 38)
                    if btn_voltar_historia.collidepoint(pos_mouse):
                        estado_jogo = "MENU_INICIAL"
                    else:
                        for indice in range(1, len(FRAGMENTOS_BIOMAS) + 1):
                            rect_fragmento = pygame.Rect(24, 116 + (indice - 1) * 29, 270, 26)
                            if rect_fragmento.collidepoint(pos_mouse):
                                fragmento_selecionado = indice
                                break
                elif estado_jogo == "INVENTARIO":
                    cura_pocao = inventario_tela.tratar_clique(pos_mouse, player)
                    if cura_pocao:
                        particulas.criar_texto_dano(
                            player.rect.centerx, player.rect.y - 20,
                            f"+{cura_pocao}", VERDE,
                        )
                        audio.tocar_som("cura")
                elif estado_jogo == "CONFIGURACOES":
                    res = menu_config.tratar_clique(pos_mouse, CONFIG_JOGO)
                    if res == "VOLTAR":
                        estado_jogo = estado_config_retorno
                    elif res == "TELA_CHEIA":
                        recriar_tela()
                elif estado_jogo == "PAUSE":
                    btn_retomar = pygame.Rect(LARGURA//2 - 120, 220, 240, 45)
                    btn_pause_lobby = pygame.Rect(LARGURA//2 - 120, 280, 240, 45)
                    btn_pause_sair = pygame.Rect(LARGURA//2 - 120, 340, 240, 45)
                    btn_pause_config = pygame.Rect(LARGURA//2 - 120, 400, 240, 45)
                    btn_pause_missoes = pygame.Rect(LARGURA//2 - 120, 460, 240, 45)
                    
                    if confirmacao_tipo is None:
                        if btn_retomar.collidepoint(pos_mouse):
                            estado_jogo = "JOGANDO"
                        elif btn_pause_lobby.collidepoint(pos_mouse):
                            confirmacao_tipo = "LOBBY"
                        elif btn_pause_sair.collidepoint(pos_mouse):
                            confirmacao_tipo = "SAIR"
                        elif btn_pause_config.collidepoint(pos_mouse):
                            estado_config_retorno = "PAUSE"
                            estado_jogo = "CONFIGURACOES"
                        elif btn_pause_missoes.collidepoint(pos_mouse):
                            estado_missoes_retorno = "PAUSE"
                            estado_jogo = "MISSOES"
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

                elif estado_jogo == "GAME_OVER":
                    btn_jogar_novamente = pygame.Rect(LARGURA//2 - 120, 505, 240, 40)
                    if btn_jogar_novamente.collidepoint(pos_mouse):
                        def jogar_novamente():
                            global andar_atual, bioma_atual, ordem_biomas, sala_atual, mapa_salas, estado_jogo, exibir_intro_andar, intro_timer, estatisticas_run, player, player2, tempo_inicio_run, inimigos_mgr, projeteis, projeteis_inimigos, status_jogador, status_jogador2, pet_ativo, infinito_ativo, run_registrada, ultimo_ataque_p2, mobs_missoes_reportados, elites_missoes_reportados, modo_espectador
                            ordem_biomas = list(BIOMAS_ESTETICA)
                            random.shuffle(ordem_biomas)
                            player = Jogador(400, 300)
                            player2 = Jogador(440, 300, numero_jogador=2) if CONFIG_JOGO.get("coop_local") else None
                            pet_ativo = preparar_pet(player)
                            andar_atual = 1
                            bioma_atual = ordem_biomas[0]
                            registrar_fragmento_bioma(bioma_atual)
                            inimigos_mgr = GerenciadorInimigos()
                            projeteis = []
                            projeteis_inimigos = []
                            status_jogador = GerenciadorStatus()
                            status_jogador2 = GerenciadorStatus()
                            ultimo_ataque_p2 = 0
                            run_registrada = False
                            tempo_inicio_run = time.time()
                            sala_atual, mapa_salas = gerar_andar(bioma_atual, andar_atual)
                            marcar_inicio_sala(sala_atual)
                            estatisticas_run = {"mobs_mortos": 0, "gemas_coletadas": 0, "tempo_segundos": 0, "andar_morte": 1, "elites_derrotados": 0, "inimigos_raros_derrotados": 0, "dano_causado": 0, "salas_concluidas": 0, "salas_sem_dano": 0, "chefes_secretos_derrotados": 0, "contrato": iniciar_contrato(1), "desafio_diario": estado_desafio_diario(), "modificadores": list(CONFIG_JOGO.get("modificadores_run", []))}
                            infinito_ativo = False
                            estado_jogo = "JOGANDO"
                            modo_espectador = False
                            exibir_intro_andar = True
                            intro_timer = pygame.time.get_ticks()
                        iniciar_transicao(jogar_novamente)
                    elif estado_jogo == "GAME_OVER" and pygame.Rect(
                        LARGURA // 2 - 120, 550, 240, 40
                    ).collidepoint(pos_mouse):
                        player.em_run = False
                        estado_jogo = "MENU_INICIAL"
                elif estado_jogo == "CICLO_FIM":
                    btn_continuar = pygame.Rect(LARGURA // 2 - 150, 340, 300, 48)
                    btn_lobby_ciclo = pygame.Rect(LARGURA // 2 - 150, 405, 300, 48)
                    if btn_continuar.collidepoint(pos_mouse):
                        infinito_ativo = True
                        iniciar_transicao(avancar_andar)
                    elif btn_lobby_ciclo.collidepoint(pos_mouse):
                        registrar_fim_run()
                        player.em_run = False
                        estado_jogo = "MENU_INICIAL"
            elif event.button == 3 and estado_jogo == "INVENTARIO":
                inventario_tela.alternar_protecao(player, pos_mouse)

        if event.type == pygame.KEYDOWN:
            if estado_jogo == "NPC_HUB":
                acao_hub = hub_npcs.tratar_tecla(event.key, lang)
                if acao_hub == "VOLTAR":
                    estado_jogo = "MENU_INICIAL"
                elif acao_hub == "COMPRAR":
                    _, chave_aviso = comprar_servico_npc(hub_npcs.alvo_npc)
                    hub_npcs.aviso = t(chave_aviso, lang)
                continue
            if estado_jogo == "INVENTARIO" and event.key == pygame.K_f:
                inventario_tela.alternar_protecao(player)
                continue
            if estado_jogo == "JOGANDO" and event.key == pygame.K_p:
                cura_pocao = inventario_tela.usar_pocao(player)
                if cura_pocao:
                    particulas.criar_texto_dano(
                        player.rect.centerx, player.rect.y - 20,
                        f"+{cura_pocao}", VERDE,
                    )
                    audio.tocar_som("cura")
                continue
            if (
                estado_jogo == "JOGANDO"
                and event.key == pygame.K_TAB
                and player.hp > 0
                and player2
                and player2.hp > 0
            ):
                modo_espectador = not modo_espectador
                continue
            if estado_jogo == "CONFIGURACOES" and menu_config.capturar_tecla(event, CONFIG_JOGO):
                salvar_configuracao()
                continue
            if estado_jogo == "JOGANDO" and event.key in (pygame.K_t, pygame.K_y):
                chave_visibilidade = "mostrar_missoes" if event.key == pygame.K_t else "mostrar_efeitos"
                CONFIG_JOGO[chave_visibilidade] = not CONFIG_JOGO.get(chave_visibilidade, True)
                salvar_configuracao()
                continue
            if (
                estado_jogo == "JOGANDO"
                and player2
                and player2.hp > 0
                and controles_jogo["P2"]["dispositivo"] == "teclado"
                and event.key == controles_jogo["P2"].get("interagir")
            ):
                if sala_atual.tipo in ("OVERCLOCK", "IMPOSTOR"):
                    if not interagir_bau(pygame.K_e, player2):
                        sala_atual.desenhar_conteudo_especial(
                            tela, player, pygame.event.Event(
                                pygame.KEYDOWN, key=pygame.K_e, unicode="e"
                            ), particulas, status_jogador, player2,
                        )
                elif sala_atual.tipo in ("RESGATE", "NPC_ENCONTRO", "REVIVER_P2", "ENIGMA", "OBELISCO", "POCO", "RITUAL"):
                    sala_atual.desenhar_conteudo_especial(
                        tela, player, pygame.event.Event(
                            pygame.KEYDOWN, key=pygame.K_1, unicode="1"
                        ), particulas, status_jogador, player2,
                    )
                else:
                    interagir_bau(pygame.K_e, player2)
            if (
                estado_jogo == "JOGANDO"
                and player2
                and player2.hp > 0
                and controles_jogo["P2"]["dispositivo"] == "teclado"
            ):
                for indice_magia in range(4):
                    if event.key == controles_jogo["P2"].get(f"magia_{indice_magia + 1}"):
                        usar_magia(player2, indice_magia, tempo_atual)
            tecla_jogo = traduzir_tecla_acao(event.key, controles_jogo, "P1")
            evento_tecla = pygame.event.Event(
                event.type, key=tecla_jogo, unicode=getattr(event, "unicode", "")
            )
            if tecla_jogo == pygame.K_e:
                if estado_jogo == "JOGANDO":
                    if not interagir_bau(tecla_jogo):
                        if sala_atual.tipo in ("OVERCLOCK", "IMPOSTOR"):
                            sala_atual.desenhar_conteudo_especial(
                                tela, player, evento_tecla, particulas,
                                status_jogador, player2,
                            )
                        elif sala_atual.tipo in ("RESGATE", "NPC_ENCONTRO", "REVIVER_P2", "ENIGMA", "OBELISCO", "POCO", "RITUAL"):
                            evento_interacao = pygame.event.Event(
                                pygame.KEYDOWN, key=pygame.K_1, unicode="1"
                            )
                            sala_atual.desenhar_conteudo_especial(
                                tela, player, evento_interacao, particulas,
                                status_jogador, player2,
                            )
                        elif sala_atual.tipo not in ("RECOMPENSA", "MIMICO", "TESOURO", "OVERCLOCK"):
                            estado_jogo = "INVENTARIO"
                elif estado_jogo == "INVENTARIO":
                    estado_jogo = "JOGANDO"
            elif tecla_jogo in (pygame.K_1, pygame.K_2) and estado_jogo == "JOGANDO":
                interagir_bau(tecla_jogo)
            elif tecla_jogo == pygame.K_ESCAPE:
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
                elif estado_jogo == "MISSOES":
                    estado_jogo = estado_missoes_retorno
                elif estado_jogo == "CONQUISTAS":
                    estado_jogo = "MENU_INICIAL"
                elif estado_jogo == "CONFIGURACOES":
                    estado_jogo = estado_config_retorno
                elif estado_jogo == "HISTORIA":
                    estado_jogo = "MENU_INICIAL"
            elif tecla_jogo == pygame.K_q and player.hp > 0 and not modo_espectador:
                teclas = pygame.key.get_pressed()
                acoes_dash = estado_acoes_teclado(teclas, controles_jogo["P1"])
                dash_antes = player.em_dash
                player.executar_dash(acoes_dash, tempo_atual, controles_jogo["P1"])
                if player.em_dash and not dash_antes:
                    audio.tocar_som("dash")
            elif estado_jogo == "JOGANDO" and player.hp > 0 and not modo_espectador:
                indice_magia = {
                    pygame.K_h: 0,
                    pygame.K_j: 1,
                    pygame.K_k: 2,
                    pygame.K_l: 3,
                }.get(tecla_jogo)
                if indice_magia is not None:
                    usar_magia(player, indice_magia, tempo_atual)

    atualizar_transicao()

    if estado_jogo == "JOGANDO":
        if atualizar_conjuracao_mitica(
            player, tempo_atual, sala_atual.inimigos, particulas,
            audio, estatisticas_run,
        ):
            particulas.criar_texto_dano(
                player.rect.centerx, player.rect.y - 30,
                t("explosao_cansaco", lang), LARANJA, True,
            )
        if player2 and player2.hp > 0:
            if atualizar_conjuracao_mitica(
                player2, tempo_atual, sala_atual.inimigos, particulas,
                audio, estatisticas_run,
            ):
                particulas.criar_texto_dano(
                    player2.rect.centerx, player2.rect.y - 30,
                    t("explosao_cansaco", lang), LARANJA, True,
                )
        player.em_run = True
        estatisticas_run["tempo_segundos"] = int(time.time() - tempo_inicio_run)
        player.mana = min(player.mana_max, player.mana + 0.05)
        stats_dict = {
            'hp': player.hp,
            'hp_max': player.hp_max,
            'pode_curar': True,
            'em_movimento': player.movendo,
        }
        if not modo_espectador:
            status_jogador.atualizar(stats_dict, tempo_atual)
            player.hp = stats_dict['hp']
            nome_ambiente, tipo_ambiente = aplicar_ambiente(
                bioma_atual, andar_atual, player, status_jogador, tempo_atual,
                particulas, lang,
            )
        else:
            nome_ambiente = nome_bioma_localizado(bioma_atual, lang)
            stats_dict["multiplicador_velocidade"] = 1.0
            stats_dict["multiplicador_dano"] = 1.0
            stats_dict["multiplicador_dano_recebido"] = 1.0
        evento_p1 = player.evento_bioma_ativo
        if evento_p1 and tempo_atual >= evento_p1.get("fim", 0):
            player.evento_bioma_ativo = None
            evento_p1 = None
        mult_velocidade_player = stats_dict['multiplicador_velocidade'] * (
            1 + player.buffs_run.get("velocidade", 0) / max(1, player.vel_base)
        ) * (1 + (evento_p1 or {}).get("velocidade", 0))
        if any(
            sombra["tipo"] == "dps" and sombra["fim"] > tempo_atual
            for sombra in getattr(player, "soldados_sombra", [])
        ):
            mult_velocidade_player *= 1.08
        mult_dano_player = stats_dict['multiplicador_dano'] * (
            1 + player.buffs_run.get("dano", 0)
        ) * (1 + (evento_p1 or {}).get("dano", 0))
        player.multiplicador_dano_recebido = stats_dict["multiplicador_dano_recebido"]
        if pet_ativo and not modo_espectador:
            pet_ativo.atualizar(*player.rect.center, sala_atual, projeteis)
        if player2:
            player2.em_run = True
            player2.mana = min(player2.mana_max, player2.mana + 0.05)
            stats_p2 = {
                "hp": player2.hp, "hp_max": player2.hp_max,
                "pode_curar": True, "em_movimento": player2.movendo,
            }
            status_jogador2.atualizar(stats_p2, tempo_atual)
            player2.hp = stats_p2["hp"]
            aplicar_ambiente(
                bioma_atual, andar_atual, player2, status_jogador2, tempo_atual,
                particulas, lang,
            )
            evento_p2 = player2.evento_bioma_ativo
            if evento_p2 and tempo_atual >= evento_p2.get("fim", 0):
                player2.evento_bioma_ativo = None
                evento_p2 = None
            player2.multiplicador_dano_recebido = stats_p2.get(
                "multiplicador_dano_recebido", 1.0
            )
            player2.multiplicador_dano_run = (
                1 + (evento_p2 or {}).get("dano", 0)
            )
        dados_index = carregar_dados()
        descobertos = dados_index.setdefault("index_descobertas", {}).setdefault("inimigos", {})
        houve_novo = False
        for inimigo in sala_atual.inimigos:
            tipo_inimigo = inimigo.get("tipo_inimigo")
            bioma_inimigo = inimigo.get("bioma_id", sala_atual.bioma_id)
            if not tipo_inimigo and inimigo.get("tipo") == "boss":
                tipo_inimigo = "boss"
            if tipo_inimigo:
                chave_inimigo = f"{bioma_inimigo}:{tipo_inimigo}"
                if not descobertos.get(chave_inimigo):
                    descobertos[chave_inimigo] = True
                    houve_novo = True
            if inimigo.get("raro"):
                chave_raro = f"{bioma_inimigo}:raro"
                if not descobertos.get(chave_raro):
                    descobertos[chave_raro] = True
                    houve_novo = True
        if houve_novo:
            salvar_dados(dados_index)

        teclas = pygame.key.get_pressed()
        acoes_p1 = (
            estado_analogico(joysticks[0], controles_jogo["P1"])
            if controles_jogo["P1"]["dispositivo"] == "controle" and joysticks
            else estado_acoes_teclado(teclas, controles_jogo["P1"])
        )
        acoes_touch = controles_touch.acoes_pressionadas(estado_jogo == "JOGANDO")
        for acao, pressionada in acoes_touch.items():
            acoes_p1[acao] = acoes_p1.get(acao, False) or pressionada
        controle_combate.atualizar_ataque(
            acoes_p1.get("ataque", False), tempo_atual
        )
        defesa_pressionada = acoes_p1.get("defesa", False)
        if defesa_pressionada and not ultimo_estado_defesa:
            controle_combate.ativar_escudo(tempo_atual)
        ultimo_estado_defesa = defesa_pressionada
        player.escudo_ativo = controle_combate.escudo_ativo(tempo_atual)
        player.parry_window_ate = controle_combate.janela_parry_ate
        if player.hp > 0 and not modo_espectador:
            if tempo_atual >= getattr(player, "imovel_ate", 0):
                player.mover(
                    acoes_p1, tempo_atual,
                    mult_velocidade_player * (0.58 if player.escudo_ativo else 1.0),
                    controles_jogo["P1"],
                    sala_atual.obstaculos,
                )
            else:
                player.movendo = False
                player.vel_x = 0
                player.vel_y = 0
            if acoes_p1.get("dash") and not player.em_dash:
                dash_antes_p1 = player.em_dash
                player.executar_dash(acoes_p1, tempo_atual, controles_jogo["P1"])
                if player.em_dash and not dash_antes_p1:
                    audio.tocar_som("dash")
            if any(
                sombra["tipo"] == "curandeiro" and sombra["fim"] > tempo_atual
                for sombra in getattr(player, "soldados_sombra", [])
            ):
                player.hp = min(player.hp_max, player.hp + 0.035)
        acoes_p2 = {}
        if player2:
            indice_joystick_p2 = min(1, len(joysticks) - 1) if joysticks else 0
            acoes_p2 = (
                estado_analogico(joysticks[indice_joystick_p2], controles_jogo["P2"])
                if controles_jogo["P2"]["dispositivo"] == "controle" and joysticks
                else estado_acoes_teclado(teclas, controles_jogo["P2"])
            )
            velocidade_p2 = stats_p2["multiplicador_velocidade"] * (
                1 + player2.buffs_run.get("velocidade", 0) / max(1, player2.vel_base)
            ) * (1 + (evento_p2 or {}).get("velocidade", 0))
            if player2.hp > 0:
                player2.mover(
                    acoes_p2, tempo_atual, velocidade_p2, controles_jogo["P2"],
                    sala_atual.obstaculos,
                )
            if player2.hp > 0 and acoes_p2.get("dash") and not player2.em_dash:
                dash_antes_p2 = player2.em_dash
                player2.executar_dash(acoes_p2, tempo_atual, controles_jogo["P2"])
                if player2.em_dash and not dash_antes_p2:
                    audio.tocar_som("dash")

        atualizar_obstaculos()

        if sala_atual.tipo == "CHEFE" and sala_atual.fase_chefe == 0:
            if evento_tecla:
                if evento_tecla.key == pygame.K_1:
                    if todas_salas_exploradas(mapa_salas):
                        sala_atual.spawnar_boss_direto()
                    else:
                        mensagem_aviso = t("boss_explorar", lang)
                        tempo_aviso = tempo_atual
                elif evento_tecla.key == pygame.K_2:
                    sala_atual.limpa = True
                elif evento_tecla.key == pygame.K_3:
                    if (
                        sala_atual.segredo_chefe_disponivel
                        and todas_salas_exploradas(mapa_salas)
                        and estatisticas_run.get("elites_derrotados", 0) >= 5
                    ):
                        sala_atual.spawnar_boss_direto(secreto=True)
                    else:
                        mensagem_aviso = t("chefe_secreto_bloqueado", lang)
                        tempo_aviso = tempo_atual

        if sala_atual.tipo in ["LOJA", "FERREIRO", "FORJA", "MAGIA", "CASSINO", "SACRIFICIO", "TESOURO", "EVENTO", "RELIQUIA", "BIBLIOTECA", "SANTUARIO", "FONTE", "PORTAL", "EXCLUSIVA_BIOMA", "RESGATE", "NPC_ENCONTRO", "REVIVER_P2", "TREINO_CHEFE", "ENIGMA", "OBELISCO", "POCO", "RITUAL", "OVERCLOCK", "IMPOSTOR"] and evento_tecla:
            sala_atual.desenhar_conteudo_especial(
                tela, player, evento_tecla, particulas, status_jogador, player2
            )

        if player2 and player2.hp > 0 and acoes_p2.get("ataque") and sala_atual.inimigos:
            arma_p2 = player2.equipado_arma
            configurar_municao_arma(arma_p2)
            recarga_p2 = atualizar_municao_arma(arma_p2, tempo_atual)
            cd_p2 = max(100, int(cadencia_ataque_arma(arma_p2) * (
                1 - bonus_encantamento(arma_p2, "cadencia_percentual")
            )))
            if tempo_atual - ultimo_ataque_p2 >= cd_p2 and not recarga_p2:
                custo_p2 = custo_mana_com_sinergia(player2, custo_mana_ataque(arma_p2))
                tem_municao_p2 = arma_p2.get("tipo_arma") != "ranged" or arma_p2.get("municao", 0) > 0
                if player2.mana >= custo_p2 and arma_p2 and tem_municao_p2:
                    player2.mana -= custo_p2
                    dano_p2, critico_p2 = dano_arma(
                        arma_p2,
                        player2,
                        stats_p2["multiplicador_dano"]
                        * getattr(player2, "multiplicador_dano_run", 1.0)
                        * (1 + player2.buffs_run.get("dano", 0)),
                    )
                    if arma_p2.get("tipo_arma") == "melee":
                        alvo_p2 = alvo_melee_automatico(player2, sala_atual.inimigos, arma_p2)
                        if alvo_p2:
                            angulo_p2 = angulo_para_ataque_melee(player2, [alvo_p2], pos_mouse, "AUTOMATICO")
                            player2.melee_animacao_angulo = angulo_p2
                            player2.melee_animacao_alcance = alcance_arma_melee(arma_p2)
                            player2.melee_animacao_fim = tempo_atual + 220
                            for inimigo in sala_atual.inimigos:
                                if inimigo_no_cone_melee(inimigo, player2, angulo_p2, alcance_arma_melee(arma_p2)):
                                    dano_real_p2 = aplicar_dano_inimigo(
                                        inimigo, dano_p2, critico_p2, tempo_atual, audio, estatisticas_run
                                    )
                                    acumular_carga_suprema(player2, dano_real_p2)
                                    aplicar_efeitos_encantamento(arma_p2, inimigo, player2, dano_p2, tempo_atual)
                    else:
                        alvo_p2 = min(
                            sala_atual.inimigos,
                            key=lambda inimigo: math.dist(player2.rect.center, inimigo["rect"].center),
                        )
                        angulo_p2 = math.atan2(
                            alvo_p2["rect"].centery - player2.rect.centery,
                            alvo_p2["rect"].centerx - player2.rect.centerx,
                        )
                        velocidade_p2 = 8 * (1 + bonus_encantamento(arma_p2, "velocidade_projetil"))
                        projeteis.append({
                            "x": player2.rect.centerx, "y": player2.rect.centery,
                            "vx": math.cos(angulo_p2) * velocidade_p2,
                            "vy": math.sin(angulo_p2) * velocidade_p2,
                            "dano": dano_p2, "crit": critico_p2,
                            "dono": 2, "arma": arma_p2,
                        })
                        if arma_p2.get("tipo_arma") == "ranged":
                            arma_p2["municao"] -= 1
                            if arma_p2["municao"] <= 0:
                                arma_p2["recarregando_ate"] = tempo_atual + arma_p2.get("recarga_ms", 1400)
                    audio.tocar_som("corte" if arma_p2.get("tipo_arma") == "melee" else "tiro")
                    registrar_uso_arma(arma_p2.get("tipo_arma", "melee"))
                    ultimo_ataque_p2 = tempo_atual

        arma = player.equipado_arma
        configurar_municao_arma(arma)
        cadencia_ataque = max(
            100,
            int(cadencia_ataque_arma(arma) * (1 - bonus_encantamento(arma, "cadencia_percentual"))),
        ) if arma else 400
        alvo_melee_auto = (
            alvo_melee_automatico(player, sala_atual.inimigos, arma)
            if arma and arma.get("tipo_arma") == "melee"
            and CONFIG_JOGO["modo_tiro"] == "AUTOMATICO"
            else None
        )
        multiplicador_ataque_carregado = controle_combate.consumir_ataque()
        entrada_manual = multiplicador_ataque_carregado > 0
        if arma and arma.get("tipo_arma") == "melee":
            ataque_solicitado = (
                entrada_manual
                if CONFIG_JOGO["modo_tiro"] == "MANUAL"
                else alvo_melee_auto is not None
            )
        else:
            ataque_solicitado = (
                entrada_manual
                if CONFIG_JOGO["modo_tiro"] == "MANUAL"
                else bool(sala_atual.inimigos)
            )
        recarga_ativa = atualizar_municao_arma(arma, tempo_atual)
        player.recarregando_ate = (
            arma.get("recarregando_ate", 0)
            if arma and arma.get("tipo_arma") == "ranged"
            else 0
        )
        custo_mana = max(0, int(custo_mana_com_sinergia(player, custo_mana_ataque(arma)) * (
            1 + bonus_encantamento(arma, "mana_percentual")
        )))
        if (
            arma
            and custo_mana > 0
            and player.mana < custo_mana
            and (tempo_atual - tempo_ultimo_tiro > cadencia_ataque)
            and not recarga_ativa
            and ataque_solicitado
            and tempo_atual - getattr(player, "aviso_mana_tempo", 0) > 1000
        ):
            particulas.criar_texto_dano(player.rect.centerx, player.rect.y - 15, t("mana_insuficiente", lang), CIANO)
            player.aviso_mana_tempo = tempo_atual
        if player.hp > 0 and not modo_espectador and arma and player.mana >= custo_mana and (tempo_atual - tempo_ultimo_tiro > cadencia_ataque) and not recarga_ativa:
            if ataque_solicitado:
                registrar_uso_arma(arma.get("tipo_arma", "melee"))
                player.mana = max(0, player.mana - custo_mana)
                tempo_ultimo_tiro = tempo_atual
                if arma.get("tipo_arma") == "ranged":
                    arma["municao"] -= 1
                dano_final, eh_crit = dano_arma(arma, player, mult_dano_player)
                dano_final = max(
                    5, arredondar_para_5(
                        dano_final * max(1.0, multiplicador_ataque_carregado)
                    )
                )

                if arma.get('tipo_arma') == 'melee':
                    audio.tocar_som("corte")
                    alcance_melee = alcance_arma_melee(arma) * (
                        1.45 if multiplicador_ataque_carregado >= 1.8 else 1.0
                    )
                    inimigos_para_mirar = (
                        [alvo_melee_auto]
                        if CONFIG_JOGO["modo_tiro"] == "AUTOMATICO" and alvo_melee_auto
                        else sala_atual.inimigos
                    )
                    angulo_melee = angulo_para_ataque_melee(
                        player, inimigos_para_mirar, pos_mouse, CONFIG_JOGO["modo_tiro"]
                    )
                    player.melee_animacao_angulo = angulo_melee
                    player.melee_animacao_alcance = alcance_melee
                    player.melee_animacao_fim = tempo_atual + 220
                    acertou_critico = False
                    for inimigo in sala_atual.inimigos:
                        if inimigo_no_cone_melee(inimigo, player, angulo_melee, alcance_melee):
                            aviso_chefe = inimigo.get("ataque_especial_pendente")
                            em_janela_parry = bool(
                                aviso_chefe
                                and aviso_chefe["aviso_ms"]
                                - (tempo_atual - aviso_chefe["inicio"]) <= 180
                            ) or (
                                inimigo.get("tipo") == "boss"
                                and inimigos_mgr.boss_em_preparacao
                            )
                            if (
                                em_janela_parry
                                and arma.get("tipo_arma") == "melee"
                                and "espad" in arma.get("nome", "").casefold()
                                and tempo_atual >= getattr(player, "parry_cooldown_ate", 0)
                            ):
                                inimigo["parry_atordoado_ate"] = tempo_atual + (
                                    2200 if inimigo.get("tipo") == "boss" else 1300
                                )
                                player.parry_cooldown_ate = tempo_atual + 650
                                player.parry_crit_ate = tempo_atual + 2200
                                particulas.criar_texto_dano(
                                    inimigo["rect"].centerx, inimigo["rect"].y - 32,
                                    t("parry_perfeito", lang), AMARELO, True,
                                )
                                if inimigo.get("tipo") == "boss":
                                    inimigos_mgr.boss_em_preparacao = False
                                    inimigo["ataque_especial_pendente"] = None
                            escudo_inimigo = inimigo.get("escudo", 0)
                            if arma.get("mitica_id") == "espada_berserk":
                                inimigo["escudo"] = 0
                            dano_aplicado = aplicar_dano_inimigo(
                                inimigo, dano_final, eh_crit, tempo_atual, audio, estatisticas_run
                            )
                            if arma.get("mitica_id") == "espada_berserk":
                                inimigo["escudo"] = escudo_inimigo
                            tentar_invocar_sombra(player, arma, inimigo, tempo_atual)
                            acumular_carga_suprema(player, dano_aplicado)
                            aplicar_efeitos_encantamento(arma, inimigo, player, dano_aplicado, tempo_atual)
                            acertou_critico = acertou_critico or eh_crit
                            particulas.criar_explosao(inimigo['rect'].centerx, inimigo['rect'].centery, AMARELO)
                            particulas.criar_texto_dano(inimigo['rect'].centerx, inimigo['rect'].y - 10, f"-{dano_aplicado}!" if eh_crit else f"-{dano_aplicado}", VERMELHO if eh_crit else BRANCO, eh_crit)
                    for obstaculo in sala_atual.obstaculos[:]:
                        if inimigo_no_cone_melee(
                            {"rect": obstaculo["rect"]}, player, angulo_melee,
                            alcance_melee,
                        ):
                            danificar_obstaculo(
                                sala_atual, obstaculo, dano_final, player
                            )
                    cura_sinergia = curar_por_sinergia_critica(player, acertou_critico)
                    if cura_sinergia:
                        particulas.criar_texto_dano(
                            player.rect.centerx, player.rect.y - 15,
                            f"+{cura_sinergia} HP", VERDE,
                        )
                else:
                    audio.tocar_som("magia" if arma.get("tipo_arma") == "mage" else "tiro")
                    if CONFIG_JOGO['modo_tiro'] == 'MANUAL':
                        ang = math.atan2(pos_mouse[1] - player.rect.centery, pos_mouse[0] - player.rect.centerx)
                    else:
                        alvo = min(sala_atual.inimigos, key=lambda e: math.hypot(e['rect'].centerx - player.rect.centerx, e['rect'].centery - player.rect.centery))
                        ang = math.atan2(alvo['rect'].centery - player.rect.centery, alvo['rect'].centerx - player.rect.centerx)
                    velocidade_projetil = velocidade_projetil_com_sinergia(player, 8)
                    quantidade_tiros = (
                        8 if arma.get("mitica_id") == "pistolas_duplas" and player.em_dash else 1
                    )
                    for indice_tiro in range(quantidade_tiros):
                        angulo_tiro = (
                            math.tau * indice_tiro / quantidade_tiros
                            if quantidade_tiros > 1 else ang
                        )
                        projeteis.append({
                            'x': player.rect.centerx,
                            'y': player.rect.centery,
                            'vx': math.cos(angulo_tiro) * velocidade_projetil,
                            'vy': math.sin(angulo_tiro) * velocidade_projetil,
                            'dano': dano_final,
                            'crit': eh_crit,
                            'dono': 1,
                            'arma': arma,
                            'retorna': bool(arma.get("retorna")),
                            'origem': tuple(player.rect.center),
                            'alcance_max': 260,
                            'distancia_percorrida': 0,
                            'hit_ids': [],
                            'raio_explosao': 0,
                            'pierce': arma.get("mitica_id") == "arco_luz",
                        })
                    if eh_crit and arma.get("mitica_id") == "arco_luz" and sala_atual.inimigos:
                        alvo_luz = min(
                            sala_atual.inimigos,
                            key=lambda inimigo: math.dist(
                                inimigo["rect"].center, player.rect.center
                            ),
                        )
                        for deslocamento in (-0.28, 0, 0.28):
                            angulo_luz = math.atan2(
                                alvo_luz["rect"].centery - player.rect.centery,
                                alvo_luz["rect"].centerx - player.rect.centerx,
                            ) + deslocamento
                            projeteis.append({
                                "x": player.rect.centerx, "y": player.rect.centery,
                                "vx": math.cos(angulo_luz) * velocidade_projetil,
                                "vy": math.sin(angulo_luz) * velocidade_projetil,
                                "dano": max(5, dano_final // 2), "crit": False,
                                "dono": 1, "arma": arma, "pierce": True,
                                "hit_ids": [],
                            })
                if arma.get("tipo_arma") == "ranged" and arma["municao"] <= 0:
                    arma["recarregando_ate"] = tempo_atual + arma.get("recarga_ms", 1400)
                    player.recarregando_ate = arma["recarregando_ate"]

        for p in projeteis[:]:
            dono = player2 if p.get("dono") == 2 and player2 else player
            if p.get("retorna") and p.get("voltando"):
                dx_retorno = dono.rect.centerx - p["x"]
                dy_retorno = dono.rect.centery - p["y"]
                distancia_retorno = max(1, math.hypot(dx_retorno, dy_retorno))
                if distancia_retorno <= 22:
                    projeteis.remove(p)
                    continue
                velocidade_retorno = max(6, math.hypot(p["vx"], p["vy"]))
                p["vx"] = dx_retorno / distancia_retorno * velocidade_retorno
                p["vy"] = dy_retorno / distancia_retorno * velocidade_retorno
            x_anterior, y_anterior = p["x"], p["y"]
            p['x'] += p['vx']
            p['y'] += p['vy']
            if p.get("retorna"):
                p["distancia_percorrida"] = p.get("distancia_percorrida", 0) + math.hypot(
                    p["x"] - x_anterior, p["y"] - y_anterior
                )
                if (
                    not p.get("voltando")
                    and p["distancia_percorrida"] >= p.get("alcance_max", 260)
                ):
                    p["voltando"] = True
                    p["hit_ids"] = []
            p_rect = pygame.Rect(p['x']-4, p['y']-4, 8, 8)
            hit = False
            for inimigo in sala_atual.inimigos:
                if (
                    p_rect.colliderect(inimigo['rect'])
                    and id(inimigo) not in p.get("hit_ids", [])
                ):
                    if inimigo.get('tipo') == 'boss' and tempo_atual < inimigo.get('tempo_imortal_fim', 0):
                        particulas.criar_texto_dano(p['x'], p['y'] - 10, "IMORTAL!", CIANO)
                    else:
                        dano_real = aplicar_dano_inimigo(
                            inimigo, p['dano'], p['crit'], tempo_atual, audio, estatisticas_run
                        )
                        tentar_invocar_sombra(dono, p.get("arma"), inimigo, tempo_atual)
                        acumular_carga_suprema(dono, dano_real)
                        aplicar_efeitos_encantamento(p.get("arma"), inimigo, dono, p["dano"], tempo_atual)
                        particulas.criar_explosao(p['x'], p['y'], AMARELO)
                        particulas.criar_texto_dano(
                            p['x'], p['y'] - 10,
                            f"-{dano_real}{'!!!' if p['crit'] else ''}",
                            AMARELO if p['crit'] else BRANCO, p['crit'],
                        )
                        raio = p.get("raio_explosao", 0)
                        if raio:
                            for inimigo_area in sala_atual.inimigos:
                                if inimigo_area is inimigo or math.dist(
                                    inimigo_area["rect"].center, p_rect.center
                                ) > raio:
                                    continue
                                aplicar_dano_inimigo(
                                    inimigo_area, p["dano"] * 0.75, p["crit"],
                                    tempo_atual, audio, estatisticas_run,
                                )
                        if p.get("split") and not p.get("split_done"):
                            p["split_done"] = True
                            alvos_laser = sorted(
                                (
                                    alvo for alvo in sala_atual.inimigos
                                    if alvo is not inimigo
                                ),
                                key=lambda alvo: math.dist(
                                    alvo["rect"].center, inimigo["rect"].center
                                ),
                            )[:3]
                            for alvo_laser in alvos_laser:
                                dx = alvo_laser["rect"].centerx - inimigo["rect"].centerx
                                dy = alvo_laser["rect"].centery - inimigo["rect"].centery
                                distancia = max(1, math.hypot(dx, dy))
                                projeteis.append({
                                    "x": inimigo["rect"].centerx,
                                    "y": inimigo["rect"].centery,
                                    "vx": dx / distancia * 12,
                                    "vy": dy / distancia * 12,
                                    "dano": max(5, int(p["dano"] * 0.45)),
                                    "crit": False, "dono": p.get("dono", 1),
                                    "arma": p.get("arma"), "pierce": True,
                                    "hit_ids": [],
                                })
                    p.setdefault("hit_ids", []).append(id(inimigo))
                    if p.get("retorna") and not p.get("voltando"):
                        p["voltando"] = True
                        p["hit_ids"] = []
                        break
                    if not p.get("pierce"):
                        hit = True
                        break
            if not hit:
                for obstaculo in sala_atual.obstaculos[:]:
                    if not p_rect.colliderect(obstaculo["rect"]):
                        continue
                    danificar_obstaculo(sala_atual, obstaculo, p["dano"], dono)
                    if obstaculo["solido"]:
                        hit = True
                        break
            fora_da_sala = (
                p['x'] < 60 or p['x'] > LARGURA - 60
                or p['y'] < 60 or p['y'] > ALTURA - 60
            )
            if p.get("retorna") and fora_da_sala and not p.get("voltando"):
                p["voltando"] = True
                p["hit_ids"] = []
            if hit or (fora_da_sala and not p.get("retorna")):
                projeteis.remove(p)

        for dono_efeito in (player, player2):
            if not dono_efeito:
                continue
            meteoros = getattr(dono_efeito, "meteoros_ativos", [])
            for meteoro in meteoros[:]:
                raio = meteoro["raio"]
                if tempo_atual < meteoro["detonar"]:
                    continue
                for inimigo in sala_atual.inimigos:
                    if math.dist(inimigo["rect"].center, meteoro["pos"]) <= raio:
                        dano_meteoro = aplicar_dano_inimigo(
                            inimigo, meteoro["dano"], True, tempo_atual,
                            audio, estatisticas_run,
                        )
                        particulas.criar_texto_dano(
                            inimigo["rect"].centerx, inimigo["rect"].y - 12,
                            f"-{dano_meteoro}!!!", AMARELO, True,
                        )
                particulas.criar_explosao(*meteoro["pos"], LARANJA)
                meteoros.remove(meteoro)
            dono_efeito.meteoros_ativos = meteoros

            singularidade = getattr(dono_efeito, "singularidade_ativa", None)
            if not singularidade:
                continue
            pos = singularidade["pos"]
            if tempo_atual < singularidade["fim"]:
                for inimigo in sala_atual.inimigos:
                    dx = pos[0] - inimigo["rect"].centerx
                    dy = pos[1] - inimigo["rect"].centery
                    distancia = math.hypot(dx, dy)
                    if 0 < distancia <= 260:
                        inimigo["rect"].x += int(dx / distancia * 4)
                        inimigo["rect"].y += int(dy / distancia * 4)
            else:
                for inimigo in sala_atual.inimigos:
                    if math.dist(inimigo["rect"].center, pos) <= 260:
                        dano_singularidade = aplicar_dano_inimigo(
                            inimigo, singularidade["dano"], True,
                            tempo_atual, audio, estatisticas_run,
                        )
                        particulas.criar_texto_dano(
                            inimigo["rect"].centerx, inimigo["rect"].y - 12,
                            f"-{dano_singularidade}!!!", ROXO_UI, True,
                        )
                particulas.criar_explosao(*pos, ROXO_UI)
                dono_efeito.singularidade_ativa = None

        if not sala_atual.limpa and len(sala_atual.inimigos) == 0:
            if sala_atual.tipo == "NORMAL":
                sala_atual.spawnar_proxima_onda(getattr(player, "sorte_run", 0.0))
            elif sala_atual.tipo == "TREINO_CHEFE":
                sala_atual.spawnar_proxima_onda(getattr(player, "sorte_run", 0.0))
            elif sala_atual.tipo == "OVERCLOCK" and sala_atual.overclock_inicio is not None and not sala_atual.overclock_concluido:
                sala_atual.spawnar_proxima_onda(getattr(player, "sorte_run", 0.0))
            elif sala_atual.tipo == "IMPOSTOR" and sala_atual.impostor_revelado:
                sala_atual.limpa = True
            elif sala_atual.tipo == "MIMICO":
                sala_atual.limpa = True

        for inimigo in sala_atual.inimigos:
            if tempo_atual < inimigo.get("sangramento_fim", 0) and tempo_atual - inimigo.get("sangramento_tick", 0) >= 700:
                dano_dot = arredondar_para_5(3)
                estatisticas_run["dano_causado"] += min(dano_dot, max(0, inimigo["hp"]))
                inimigo["hp"] -= dano_dot
                inimigo["sangramento_tick"] = tempo_atual
                particulas.criar_texto_dano(
                    inimigo["rect"].centerx, inimigo["rect"].y - 10,
                    f"-{arredondar_para_5(3)}", VERMELHO,
                )
            dot = inimigo.get("encantamento_dot")
            if dot and tempo_atual < dot["fim"] and tempo_atual >= dot["proximo"]:
                estatisticas_run["dano_causado"] += min(
                    dot["dano"], max(0, inimigo["hp"])
                )
                inimigo["hp"] -= dot["dano"]
                dot["proximo"] = tempo_atual + 900
                particulas.criar_texto_dano(
                    inimigo["rect"].centerx, inimigo["rect"].y - 12,
                    f"-{dot['dano']}", (255, 120, 80) if dot["tipo"] == "queimadura" else (120, 220, 100),
                )
            elif dot and tempo_atual >= dot["fim"]:
                inimigo.pop("encantamento_dot", None)

        for sombra in player.soldados_sombra[:]:
            if sombra["fim"] <= tempo_atual:
                player.soldados_sombra.remove(sombra)
                continue
            sombra.setdefault("x", player.rect.centerx)
            sombra.setdefault("y", player.rect.centery)
            alvo_sombra = min(
                sala_atual.inimigos,
                key=lambda alvo: math.dist(
                    (sombra["x"], sombra["y"]), alvo["rect"].center
                ),
                default=None,
            )
            if not alvo_sombra:
                continue
            dx = alvo_sombra["rect"].centerx - sombra["x"]
            dy = alvo_sombra["rect"].centery - sombra["y"]
            distancia = max(1, math.hypot(dx, dy))
            if distancia > 30:
                sombra["x"] += dx / distancia * 3.2
                sombra["y"] += dy / distancia * 3.2
            elif tempo_atual >= sombra["proximo_ataque"]:
                dano_sombra = aplicar_dano_inimigo(
                    alvo_sombra, max(5, int(player.equipado_arma["dano"] * 0.3)),
                    False, tempo_atual, audio, estatisticas_run,
                )
                sombra["proximo_ataque"] = tempo_atual + 800
                acumular_carga_suprema(player, dano_sombra)

        inimigos_mgr.atualizar_e_colidir(
            sala_atual, player, particulas, estatisticas_run, projeteis_inimigos,
            status_jogador, audio,
            players=[
                alvo for alvo in (player, player2)
                if alvo and alvo.hp > 0 and (alvo is not player or not modo_espectador)
            ] or [player],
            status_managers=[
                gerente for alvo, gerente in ((player, status_jogador), (player2, status_jogador2))
                if alvo and alvo.hp > 0 and (alvo is not player or not modo_espectador)
            ] or [status_jogador],
        )

        dano_total_sala = sum(
            getattr(alvo, "dano_recebido_total", 0)
            for alvo in (player, player2) if alvo
        )
        if dano_total_sala > sala_atual.dano_inicio_sala:
            sala_atual.sem_dano = False
        if (
            sala_atual.tipo in ("CHEFE", "TREINO_CHEFE")
            and sala_atual.boss_derrotado
            and not sala_atual.boss_derrota_registrada
        ):
            sala_atual.boss_derrota_registrada = True
            dados_boss = carregar_dados()
            chefes_derrotados = dados_boss.setdefault("chefes_derrotados", [])
            if sala_atual.bioma_id not in chefes_derrotados:
                chefes_derrotados.append(sala_atual.bioma_id)
                salvar_dados(dados_boss)

        novos_abates = max(0, estatisticas_run["mobs_mortos"] - mobs_missoes_reportados)
        novos_elites = max(0, estatisticas_run["elites_derrotados"] - elites_missoes_reportados)
        if novos_abates:
            registrar_progresso(carregar_dados(), "abates", novos_abates)
            mobs_missoes_reportados += novos_abates
        if novos_elites:
            registrar_progresso(carregar_dados(), "elites", novos_elites)
            elites_missoes_reportados += novos_elites

        if sala_atual.tipo == "CHEFE" and sala_atual.boss_derrotado and not em_transicao:
            if andar_atual == 15 and not infinito_ativo:
                registrar_progresso(carregar_dados(), "andar")
                estado_jogo = "CICLO_FIM"
            else:
                iniciar_transicao(avancar_andar)

        for pi in projeteis_inimigos[:]:
            aura_infinita = (
                player.equipado_arma
                and player.equipado_arma.get("mitica_id") == "grimorio_infinito"
                and math.dist((pi["x"], pi["y"]), player.rect.center) <= 115
            )
            fator_aura = 0.18 if aura_infinita else 1.0
            pi['x'] += pi['vx'] * fator_aura
            pi['y'] += pi['vy'] * fator_aura
            pi_rect = pygame.Rect(pi['x']-3, pi['y']-3, 6, 6)
            atingidos = [] if modo_espectador else [(player, status_jogador)]
            if player2:
                atingidos.append((player2, status_jogador2))
            alvo_atingido = next(
                ((alvo, gerente) for alvo, gerente in atingidos
                 if alvo.hp > 0 and pi_rect.colliderect(alvo.rect)),
                None,
            )
            if alvo_atingido:
                alvo, gerente = alvo_atingido
                aplicar_dano_player(
                    alvo, particulas, pi['dano'], tempo_atual,
                    gerente, 0.08, pi.get("efeito"),
                    pi.get("duracao_efeito", 0), audio,
                )
                projeteis_inimigos.remove(pi)
            elif any(
                obstaculo.get("solido") and pi_rect.colliderect(obstaculo["rect"])
                for obstaculo in sala_atual.obstaculos
            ):
                projeteis_inimigos.remove(pi)
            elif pi['x'] < 60 or pi['x'] > LARGURA - 60 or pi['y'] < 60 or pi['y'] > ALTURA - 60:
                projeteis_inimigos.remove(pi)

        dano_total_sala = sum(
            getattr(alvo, "dano_recebido_total", 0)
            for alvo in (player, player2) if alvo
        )
        if dano_total_sala > sala_atual.dano_inicio_sala:
            sala_atual.sem_dano = False
        if (
            sala_atual.limpa
            and sala_atual.tipo in ("NORMAL", "CACADA", "CHEFE", "TREINO_CHEFE")
            and (sala_atual.tipo not in ("CHEFE", "TREINO_CHEFE") or sala_atual.boss_derrotado)
            and not sala_atual.estatisticas_registradas
        ):
            sala_atual.estatisticas_registradas = True
            estatisticas_run["salas_concluidas"] = estatisticas_run.get("salas_concluidas", 0) + 1
            registrar_progresso(carregar_dados(), "salas")
            if sala_atual.sem_dano and not sala_atual.recompensa_sem_dano_concedida:
                sala_atual.recompensa_sem_dano_concedida = True
                player.ganhar_ouro(25)
                dados_recompensa = carregar_dados()
                dados_recompensa["gemas"] = dados_recompensa.get("gemas", 0) + 5
                salvar_dados(dados_recompensa)
                estatisticas_run["gemas_coletadas"] = (
                    estatisticas_run.get("gemas_coletadas", 0) + 5
                )
                estatisticas_run["salas_sem_dano"] = (
                    estatisticas_run.get("salas_sem_dano", 0) + 1
                )
                particulas.criar_texto_dano(
                    player.rect.centerx, player.rect.y - 28,
                    t("recompensa_sem_dano", lang), DOURADO_UI, True,
                )

        for jogador_morto in [alvo for alvo in (player, player2) if alvo and alvo.hp <= 0]:
            itens_jogador = jogador_morto.amuletos_equipados + jogador_morto.mochila_itens
            tem_fenix = any(item.get("nome") == "Anel da Fênix" for item in itens_jogador)
            if tem_fenix:
                jogador_morto.hp = jogador_morto.hp_max
                jogador_morto.tempo_imortal_fim = tempo_atual + 10000
                particulas.criar_texto_dano(
                    jogador_morto.rect.centerx, jogador_morto.rect.y - 30,
                    "FÊNIX RENASCIDA!", LARANJA, True,
                )
                for lista_itens in (jogador_morto.amuletos_equipados, jogador_morto.mochila_itens):
                    for item in lista_itens[:]:
                        if item.get("nome") == "Anel da Fênix":
                            lista_itens.remove(item)
                            break
            elif jogador_morto is player:
                player.em_run = False
            else:
                jogador_morto.em_run = False

        if player.hp <= 0 and player2 and player2.hp > 0:
            modo_espectador = True

        if player.hp <= 0 and (not player2 or player2.hp <= 0):
            estatisticas_run["andar_morte"] = andar_atual
            estado_jogo = "GAME_OVER"
            registrar_fim_run()
        elif modo_espectador and player2 and player2.hp <= 0:
            estatisticas_run["andar_morte"] = andar_atual
            estado_jogo = "GAME_OVER"
            registrar_fim_run()

        pode_s = sala_atual.limpa or sala_atual.tipo in [
            "LOJA", "FERREIRO", "FORJA", "MAGIA", "CASSINO", "SACRIFICIO",
            "RECOMPENSA", "TESOURO", "EVENTO", "RELIQUIA", "BIBLIOTECA", "SANTUARIO",
            "FONTE", "PORTAL", "EXCLUSIVA_BIOMA", "RESGATE", "NPC_ENCONTRO", "REVIVER_P2",
        ]
        if pode_s and not em_transicao:
            prox_s = None
            jogador_transicao = player2 if modo_espectador and player2 and player2.hp > 0 else player
            if 'NORTE' in sala_atual.vizinhos and jogador_transicao.rect.top <= 80:
                prox_s = sala_atual.vizinhos['NORTE']; n_pos = (jogador_transicao.rect.x, ALTURA - 120)
            elif 'SUL' in sala_atual.vizinhos and jogador_transicao.rect.bottom >= ALTURA - 80:
                prox_s = sala_atual.vizinhos['SUL']; n_pos = (jogador_transicao.rect.x, 120)
            elif 'OESTE' in sala_atual.vizinhos and jogador_transicao.rect.left <= 80:
                prox_s = sala_atual.vizinhos['OESTE']; n_pos = (LARGURA - 120, jogador_transicao.rect.y)
            elif 'LESTE' in sala_atual.vizinhos and jogador_transicao.rect.right >= LARGURA - 80:
                prox_s = sala_atual.vizinhos['LESTE']; n_pos = (120, jogador_transicao.rect.y)

            if prox_s:
                def trocar_sala():
                    global sala_atual
                    sala_atual = prox_s
                    sala_atual.revelar()
                    marcar_inicio_sala(sala_atual)
                    jogador_transicao.rect.x, jogador_transicao.rect.y = n_pos
                    audio.tocar_som("porta")
                iniciar_transicao(trocar_sala)

    # RENDERIZAÇÃO
    tela.fill(PRETO)

    if estado_jogo == "MENU_INICIAL":
        menu_inicial.desenhar(tela, pos_mouse, carregar_dados().get('gemas', 0), CONFIG_JOGO)

    elif estado_jogo == "NPC_HUB":
        hub_npcs.atualizar()
        hub_npcs.desenhar(tela, pos_mouse, lang, carregar_dados())

    elif estado_jogo in ["JOGANDO", "INVENTARIO", "PAUSE"]:
        info_b = BIOMAS_ESTETICA.get(bioma_atual, BIOMAS_ESTETICA[1])
        pygame.draw.rect(tela, info_b['piso'], (60, 60, LARGURA - 120, ALTURA - 120))
        pygame.draw.rect(tela, info_b['parede'], (60, 60, LARGURA - 120, ALTURA - 120), 8)
        pygame.draw.rect(tela, BORDA_UI, (68, 68, LARGURA - 136, ALTURA - 136), 1)

        if sala_atual.tipo == "CHEFE" and sala_atual.fase_chefe == 0:
            boss_nome = nome_chefe_localizado(bioma_atual, lang)
            txt_p1 = FONTE_GRANDE.render(f"{t('enfrentar_chefe', lang)}: {boss_nome}", True, VERMELHO)
            txt_p2 = FONTE_SYS.render(
                t("opcoes_chefe", lang) if todas_salas_exploradas(mapa_salas)
                else t("boss_explorar", lang),
                True, BRANCO,
            )
            tela.blit(txt_p1, (LARGURA//2 - txt_p1.get_width()//2, ALTURA//2 - 50))
            tela.blit(txt_p2, (LARGURA//2 - txt_p2.get_width()//2, ALTURA//2))
            if not sala_atual.segredo_chefe_disponivel:
                chave_segredo = "chefe_secreto_sem_portal"
            elif estatisticas_run.get("elites_derrotados", 0) >= 5:
                chave_segredo = "chefe_secreto_desbloqueado"
            else:
                chave_segredo = "chefe_secreto_bloqueado"
            texto_secreto = t(chave_segredo, lang)
            txt_secreto = FONTE_PEQUENA.render(texto_secreto, True, DOURADO_UI)
            tela.blit(txt_secreto, (LARGURA // 2 - txt_secreto.get_width() // 2, ALTURA // 2 + 24))

            if tempo_atual - tempo_aviso < 3000:
                txt_aviso = FONTE_SYS.render(mensagem_aviso, True, AMARELO)
                tela.blit(txt_aviso, (LARGURA//2 - txt_aviso.get_width()//2, ALTURA//2 + 50))

        desenhar_ambiente(tela, bioma_atual, tempo_atual)
        if sala_atual.tipo in ["LOJA", "FERREIRO", "FORJA", "MAGIA", "CASSINO", "SACRIFICIO", "RECOMPENSA", "MIMICO", "TESOURO", "EVENTO", "RELIQUIA", "BIBLIOTECA", "SANTUARIO", "FONTE", "PORTAL", "CACADA", "EXCLUSIVA_BIOMA", "RESGATE", "NPC_ENCONTRO", "REVIVER_P2", "TREINO_CHEFE", "ENIGMA", "OBELISCO", "POCO", "RITUAL", "OVERCLOCK", "IMPOSTOR"]:
            sala_atual.desenhar_conteudo_especial(
                tela, player, None, particulas, status_jogador, player2
            )
        sala_atual.desenhar_obstaculos(tela)

        for p in projeteis:
            pygame.draw.circle(tela, AMARELO, (int(p['x']), int(p['y'])), 4)

        for pi in projeteis_inimigos:
            pygame.draw.circle(tela, VERMELHO, (int(pi['x']), int(pi['y'])), 4)

        for dono_efeito in (player, player2):
            if not dono_efeito:
                continue
            for meteoro in getattr(dono_efeito, "meteoros_ativos", []):
                pygame.draw.circle(
                    tela, LARANJA, meteoro["pos"], int(meteoro["raio"]), 2
                )
            singularidade = getattr(dono_efeito, "singularidade_ativa", None)
            if singularidade:
                pygame.draw.circle(tela, ROXO_UI, singularidade["pos"], 105, 2)

        inimigos_mgr.desenhar_mira_boss(tela, sala_atual)
        sala_atual.desenhar_inimigos_e_moedas(
            tela, player, particulas, estatisticas_run, audio,
            [
                alvo for alvo in (player, player2)
                if alvo and alvo.hp > 0 and (alvo is not player or not modo_espectador)
            ] or [player],
        )
        for sombra in getattr(player, "soldados_sombra", []):
            pygame.draw.circle(
                tela, (104, 63, 190),
                (int(sombra.get("x", player.rect.centerx)),
                 int(sombra.get("y", player.rect.centery))), 11,
            )
            pygame.draw.circle(
                tela, ROXO_UI,
                (int(sombra.get("x", player.rect.centerx)),
                 int(sombra.get("y", player.rect.centery))), 11, 2,
            )

        if not modo_espectador:
            desenhar_cone_corte(
                tela,
                player,
                getattr(player, "melee_animacao_angulo", 0),
                getattr(player, "melee_animacao_alcance", 125),
                getattr(player, "melee_animacao_fim", 0),
                tempo_atual,
            )
        if player.hp > 0 and not modo_espectador:
            player.desenhar(tela)
            desenhar_hud_mitica(tela, player, tempo_atual, lang)
            conjuracao = getattr(player, "conjuracao_explosao", None)
            if conjuracao:
                progresso = max(
                    0.0,
                    min(
                        1.0,
                        (tempo_atual - conjuracao["inicio"])
                        / max(1, conjuracao["fim"] - conjuracao["inicio"]),
                    ),
                )
                barra_conjuracao = pygame.Rect(
                    player.rect.centerx - 36, player.rect.y - 18, 72, 6
                )
                pygame.draw.rect(tela, (34, 25, 20), barra_conjuracao, border_radius=3)
                pygame.draw.rect(
                    tela, LARANJA,
                    (barra_conjuracao.x, barra_conjuracao.y,
                     int(barra_conjuracao.width * progresso), barra_conjuracao.height),
                    border_radius=3,
                )
            if player.escudo_ativo:
                pygame.draw.circle(tela, CIANO_UI, player.rect.center, 23, 3)
                restante_escudo = max(0, controle_combate.escudo_ate - tempo_atual)
                barra = pygame.Rect(
                    player.rect.centerx - 28, player.rect.bottom + 8, 56, 6
                )
                pygame.draw.rect(tela, (24, 42, 48), barra, border_radius=3)
                pygame.draw.rect(
                    tela, CIANO_UI,
                    (barra.x, barra.y, int(barra.width * restante_escudo / 3000), barra.height),
                    border_radius=3,
                )
                texto = FONTE_PEQUENA.render(
                    f"{t('escudo_ativo', lang)} {restante_escudo / 1000:.1f}s",
                    True, CIANO_UI,
                )
                tela.blit(
                    texto,
                    (player.rect.centerx - texto.get_width() // 2, barra.bottom + 2),
                )
            if controle_combate.inicio_ataque is not None:
                progresso_carga = min(
                    1.0, (tempo_atual - controle_combate.inicio_ataque) / 800
                )
                barra_carga = pygame.Rect(
                    player.rect.centerx - 28, player.rect.bottom + 8, 56, 6
                )
                pygame.draw.rect(tela, (48, 41, 18), barra_carga, border_radius=3)
                pygame.draw.rect(
                    tela, AMARELO,
                    (barra_carga.x, barra_carga.y,
                     int(barra_carga.width * progresso_carga), barra_carga.height),
                    border_radius=3,
                )
        if player2:
            desenhar_cone_corte(
                tela, player2,
                getattr(player2, "melee_animacao_angulo", 0),
                getattr(player2, "melee_animacao_alcance", 125),
                getattr(player2, "melee_animacao_fim", 0),
                tempo_atual,
            )
            player2.desenhar(tela)
            if modo_espectador and player2.hp > 0:
                faixa_espectador = FONTE_SYS.render(t("espectador_p2", lang), True, DOURADO_UI)
                faixa_rect = pygame.Rect(0, 0, faixa_espectador.get_width() + 28, 34)
                faixa_rect.centerx = LARGURA // 2
                faixa_rect.y = 14
                pygame.draw.rect(tela, PAINEL_UI, faixa_rect, border_radius=10)
                pygame.draw.rect(tela, CIANO_UI, faixa_rect, 1, border_radius=10)
                tela.blit(faixa_espectador, (faixa_rect.centerx - faixa_espectador.get_width() // 2, faixa_rect.centery - faixa_espectador.get_height() // 2))
        if pet_ativo:
            pet_ativo.desenhar(tela)
        particulas.atualizar_e_desenhar(tela, FONTE_SYS)

        for inimigo in sala_atual.inimigos:
            if inimigo.get('tipo') == 'boss':
                largura_barra = 400
                altura_barra = 20
                bx_b = (LARGURA - largura_barra) // 2
                by_b = ALTURA - 40
                hp_perc = max(0, inimigo['hp'] / inimigo['hp_max'])
                
                pygame.draw.rect(tela, PAINEL_UI, (bx_b, by_b, largura_barra, altura_barra), border_radius=7)
                pygame.draw.rect(tela, VERMELHO, (bx_b, by_b, int(largura_barra * hp_perc), altura_barra), border_radius=4)
                pygame.draw.rect(tela, BORDA_UI, (bx_b, by_b, largura_barra, altura_barra), 1, border_radius=7)
                nome_boss = t("chefe_secreto_nome", lang) if inimigo.get("secreto") else nome_chefe_localizado(inimigo.get("bioma_id", bioma_atual), lang)
                hp_boss_atual = arredondar_para_5(inimigo['hp'])
                hp_boss_max = arredondar_para_5(inimigo['hp_max'])
                txt_b = FONTE_SYS.render(f"{nome_boss}: {hp_boss_atual} / {hp_boss_max} HP", True, BRANCO)
                tela.blit(txt_b, (bx_b + largura_barra//2 - txt_b.get_width()//2, by_b - 22))
                restante_atordoado = max(
                    0, inimigo.get("parry_atordoado_ate", 0) - tempo_atual
                )
                if restante_atordoado:
                    barra_parry = pygame.Rect(
                        inimigo["rect"].centerx - 48, inimigo["rect"].top - 18,
                        96, 7,
                    )
                    pygame.draw.rect(tela, (52, 42, 14), barra_parry, border_radius=3)
                    pygame.draw.rect(
                        tela, AMARELO,
                        (barra_parry.x, barra_parry.y,
                         int(barra_parry.width * restante_atordoado / 2200),
                         barra_parry.height),
                        border_radius=3,
                    )
                    label_parry = FONTE_PEQUENA.render(
                        t("parry_boss", lang), True, AMARELO
                    )
                    tela.blit(
                        label_parry,
                        (inimigo["rect"].centerx - label_parry.get_width() // 2,
                         barra_parry.y - label_parry.get_height() - 2),
                    )

        desenhar_minimapa(tela, mapa_salas, sala_atual)
        ambiente_txt = FONTE_PEQUENA.render(f"{t('bioma', lang)}: {nome_ambiente}", True, CIANO_UI)
        tela.blit(ambiente_txt, (14, 52))

        # Barras de Status
        bx = LARGURA - 160
        by = 175
        fundo_status = pygame.Surface((164, 114), pygame.SRCALPHA)
        fundo_status.fill((*PAINEL_UI, 190))
        tela.blit(fundo_status, (bx - 12, by - 13))
        pygame.draw.rect(tela, BORDA_UI, (bx - 12, by - 13, 164, 114), 1, border_radius=12)
        pygame.draw.rect(tela, (8, 10, 18), (bx - 1, by - 1, 142, 14), border_radius=6)
        pygame.draw.rect(tela, VERDE, (bx, by, int(140 * max(0, player.hp/player.hp_max)), 12))
        pygame.draw.rect(tela, BORDA_UI, (bx, by, 140, 12), 1, border_radius=6)
        txt_hp = FONTE_PEQUENA.render(
            f"HP: {arredondar_para_5(player.hp)}/{arredondar_para_5(player.hp_max)}", True, BRANCO
        )
        tela.blit(txt_hp, (bx + 5, by - 1))

        my = by + 18
        pygame.draw.rect(tela, (8, 10, 18), (bx - 1, my - 1, 142, 14), border_radius=6)
        pygame.draw.rect(tela, CIANO_UI, (bx, my, int(140 * max(0, player.mana/player.mana_max)), 12), border_radius=6)
        pygame.draw.rect(tela, BORDA_UI, (bx, my, 140, 12), 1, border_radius=6)
        txt_mana = FONTE_PEQUENA.render(
            f"Mana: {arredondar_para_5(player.mana)}/{arredondar_para_5(player.mana_max)}", True, BRANCO
        )
        tela.blit(txt_mana, (bx + 5, my - 1))
        texto_suprema = FONTE_PEQUENA.render(
            t("ultimate_carga", lang).format(valor=int(player.carga_suprema)),
            True, ROXO_UI,
        )
        tela.blit(texto_suprema, (bx, my + 35))
        pygame.draw.rect(tela, (8, 10, 18), (bx, my + 52, 140, 6), border_radius=3)
        pygame.draw.rect(
            tela, ROXO_UI, (bx, my + 52, int(140 * player.carga_suprema / 100), 6),
            border_radius=3,
        )
        pygame.draw.rect(tela, BORDA_UI, (bx, my + 52, 140, 6), 1, border_radius=3)

        # Dificuldade abaixo do mapa
        modo_dif = obter_modo_dificuldade()
        cor_dif = {
            "EASY": VERDE,
            "NORMAL": CIANO,
            "HARD": AMARELO,
            "HARDCORE": VERMELHO_ESCURO,
        }[modo_dif]
        txt_dif = FONTE_PEQUENA.render(f"{t('modo', lang)}: {t(f'dificuldade_{modo_dif.lower()}', lang)}", True, cor_dif)
        tela.blit(txt_dif, (bx, my + 18))
        if player2:
            p2_y = 290
            p2_card = pygame.Rect(bx - 12, p2_y - 8, 164, 64)
            pygame.draw.rect(tela, PAINEL_UI, p2_card, border_radius=8)
            pygame.draw.rect(tela, BORDA_UI, p2_card, 1, border_radius=8)
            pygame.draw.rect(tela, (8, 10, 18), (bx, p2_y, 140, 12), border_radius=6)
            pygame.draw.rect(tela, CIANO_UI, (bx, p2_y, int(140 * max(0, player2.hp / player2.hp_max)), 12), border_radius=6)
            pygame.draw.rect(tela, BORDA_UI, (bx, p2_y, 140, 12), 1, border_radius=6)
            texto_p2_hp = FONTE_PEQUENA.render(
                f"{t('jogador_dois', lang)} HP {arredondar_para_5(player2.hp)}/{arredondar_para_5(player2.hp_max)}",
                True, BRANCO,
            )
            tela.blit(texto_p2_hp, (bx + 2, p2_y + 15))
            texto_suprema_p2 = FONTE_PEQUENA.render(
                t("ultimate_carga", lang).format(valor=int(player2.carga_suprema)),
                True, ROXO_UI,
            )
            tela.blit(texto_suprema_p2, (bx + 2, p2_y + 31))
            pygame.draw.rect(tela, (8, 10, 18), (bx, p2_y + 48, 140, 6), border_radius=3)
            pygame.draw.rect(
                tela, ROXO_UI,
                (bx, p2_y + 48, int(140 * player2.carga_suprema / 100), 6),
                border_radius=3,
            )
            pygame.draw.rect(tela, BORDA_UI, (bx, p2_y + 48, 140, 6), 1, border_radius=3)

        # HUD Topo
        txt_hud = FONTE_SYS.render(
            f"{t('andar', lang)} {andar_atual} | {t('ouro', lang)}: ${player.ouro}",
            True, BRANCO,
        )
        hud_rect = pygame.Rect(14, 12, txt_hud.get_width() + 18, txt_hud.get_height() + 14)
        pygame.draw.rect(tela, PAINEL_UI, hud_rect, border_radius=10)
        pygame.draw.rect(tela, BORDA_UI, hud_rect, 1, border_radius=10)
        tela.blit(txt_hud, (hud_rect.x + 9, hud_rect.centery - txt_hud.get_height() // 2))

        arma_hud = player.equipado_arma
        x_chips = min(max(220, hud_rect.right + 10), LARGURA - 500)
        chip_municao = pygame.Rect(x_chips, 12, 175, 34)
        chip_gemas = pygame.Rect(chip_municao.right + 8, 12, 135, 34)
        for chip in (chip_municao, chip_gemas):
            fundo_chip = pygame.Surface(chip.size, pygame.SRCALPHA)
            fundo_chip.fill((*PAINEL_UI, 190))
            tela.blit(fundo_chip, chip.topleft)
            pygame.draw.rect(tela, BORDA_UI, chip, 1, border_radius=10)
        gemas_atual = carregar_dados().get("gemas", 0)
        texto_gemas = FONTE_SYS.render(f"{t('gemas', lang)}: {gemas_atual}", True, CIANO_UI)
        tela.blit(texto_gemas, (chip_gemas.centerx - texto_gemas.get_width() // 2, chip_gemas.centery - texto_gemas.get_height() // 2))

        if arma_hud and arma_hud.get("tipo_arma") == "ranged":
            if tempo_atual < getattr(player, "recarregando_ate", 0):
                texto_municao = t("recarregando", lang)
                cor_municao = DOURADO_UI
            else:
                texto_municao = (
                    f"{t('municao', lang)}: "
                    f"{arma_hud.get('municao', 0)}/{arma_hud.get('municao_max', 0)}"
                )
                cor_municao = BRANCO
            texto_chip_municao = FONTE_SYS.render(texto_municao, True, cor_municao)
            tela.blit(
                texto_chip_municao,
                (chip_municao.centerx - texto_chip_municao.get_width() // 2,
                 chip_municao.centery - texto_chip_municao.get_height() // 2),
            )
        else:
            texto_sem_municao = FONTE_SYS.render(t("hud_sem_municao", lang), True, CINZA_CLARO)
            tela.blit(
                texto_sem_municao,
                (chip_municao.centerx - texto_sem_municao.get_width() // 2,
                 chip_municao.centery - texto_sem_municao.get_height() // 2),
            )

        clip_anterior_efeitos = tela.get_clip()
        if not CONFIG_JOGO.get("mostrar_efeitos", True):
            tela.set_clip(pygame.Rect(0, 0, 0, 0))
        painel_efeitos = pygame.Rect(LARGURA - 184, 286, 170, 146)
        camada_efeitos = pygame.Surface(painel_efeitos.size, pygame.SRCALPHA)
        camada_efeitos.fill((*PAINEL_UI, 205))
        tela.blit(camada_efeitos, painel_efeitos.topleft)
        pygame.draw.rect(tela, BORDA_UI, painel_efeitos, 1, border_radius=10)
        cabecalho_efeitos = FONTE_PEQUENA.render(t("hud_efeitos", lang), True, DOURADO_UI)
        tela.blit(cabecalho_efeitos, (painel_efeitos.x + 10, painel_efeitos.y + 6))

        linhas_efeitos = []
        for reliquia in getattr(player, "reliquias_run", []):
            proximo_nivel = min(5, reliquia["nivel"] + 1)
            alvo_abates = proximo_nivel * 5
            nome_reliquia = t(f"reliquia_{reliquia['nome']}", lang).split(":")[0]
            linhas_efeitos.append((
                f"{nome_reliquia} {reliquia['nivel']}/5 · {reliquia['abates']}/{alvo_abates}",
                ROXO_UI,
            ))
        linhas_objetivos = len(linhas_efeitos)
        nomes_efeitos = {
            "queimadura": "efeito_queimadura",
            "veneno": "efeito_veneno",
            "sangramento": "efeito_sangramento",
            "lentidao": "efeito_lentidao",
            "fraqueza": "efeito_fraqueza",
            "atordoamento": "efeito_atordoamento",
            "maldicao": "efeito_maldicao",
            "vulnerabilidade": "efeito_vulnerabilidade",
            "exaustao": "efeito_exaustao",
            "cegueira": "efeito_cegueira",
            "corrosao": "efeito_corrosao",
            "regeneracao": "efeito_regeneracao",
            "foco": "efeito_foco",
        }
        for nome, dados_efeito in status_jogador.status_ativos.items():
            restante = max(0, dados_efeito["fim"] - tempo_atual)
            linhas_efeitos.append((
                f"{t(nomes_efeitos.get(nome, 'efeito_desconhecido'), lang)}  {restante / 1000:.1f}s",
                VERMELHO if nome in ("queimadura", "veneno", "sangramento") else ROXO_UI,
            ))

        for chave_buff, chave_texto in (
            ("dano", "buff_dano_hud"),
            ("vida", "buff_vida_hud"),
            ("velocidade", "buff_velocidade_hud"),
            ("defesa", "buff_defesa_hud"),
        ):
            valor_buff = player.buffs_run.get(chave_buff, 0)
            if valor_buff:
                if chave_buff == "vida":
                    valor_texto = f"+{int(valor_buff)}"
                else:
                    valor_texto = f"+{round(valor_buff * 100)}%"
                linhas_efeitos.append((
                    f"{t(chave_texto, lang)} {valor_texto} · {t('hud_run', lang)}",
                    CIANO_UI,
                ))

        if len(linhas_efeitos) == linhas_objetivos:
            linhas_efeitos.append((t("hud_sem_efeitos", lang), CINZA_CLARO))
        tela.set_clip(painel_efeitos.inflate(-12, -25))
        if not CONFIG_JOGO.get("mostrar_efeitos", True):
            tela.set_clip(pygame.Rect(0, 0, 0, 0))
        for indice, (linha, cor_linha) in enumerate(linhas_efeitos[:5]):
            texto_efeito = FONTE_PEQUENA.render(linha, True, cor_linha)
            tela.blit(texto_efeito, (painel_efeitos.x + 8, painel_efeitos.y + 27 + indice * 18))
        tela.set_clip(clip_anterior_efeitos)
        if not CONFIG_JOGO.get("mostrar_efeitos", True):
            tela.set_clip(pygame.Rect(0, 0, 0, 0))
        if len(linhas_efeitos) > 5:
            texto_extra = FONTE_PEQUENA.render(f"+{len(linhas_efeitos) - 5}", True, BRANCO)
            tela.blit(texto_extra, (painel_efeitos.x + 8, painel_efeitos.bottom - 19))
        tela.set_clip(clip_anterior_efeitos)

        clip_anterior_missoes = tela.get_clip()
        if not CONFIG_JOGO.get("mostrar_missoes", True):
            tela.set_clip(pygame.Rect(0, 0, 0, 0))
        painel_missoes = pygame.Rect(14, ALTURA - 91, 360, 77)
        camada_missoes = pygame.Surface(painel_missoes.size, pygame.SRCALPHA)
        camada_missoes.fill((*PAINEL_UI, 205))
        tela.blit(camada_missoes, painel_missoes.topleft)
        pygame.draw.rect(tela, BORDA_UI, painel_missoes, 1, border_radius=10)
        contrato = estatisticas_run.get("contrato", {})
        desafio = estatisticas_run.get("desafio_diario", {})
        linhas_missoes = []
        if contrato:
            nome_contrato = t(f"contrato_{contrato['objetivo']}", lang)
            linhas_missoes.append(
                f"{t('contrato_progresso', lang)}: {nome_contrato} {contrato['progresso']}/{contrato['meta']}"
            )
        if desafio:
            linhas_missoes.append(
                f"{t('desafio_diario', lang)} {min(20, int(desafio.get('abates', 0)))}/20"
            )
        for indice, linha in enumerate(linhas_missoes[:2]):
            texto_missao = FONTE_PEQUENA.render(linha, True, DOURADO_UI if indice == 0 else CIANO_UI)
            tela.blit(texto_missao, (painel_missoes.x + 8, painel_missoes.y + 10 + indice * 25))
        tela.set_clip(clip_anterior_missoes)

        if tempo_atual < getattr(player, "esquivou_tempo", 0):
            texto_esquivou = FONTE_PEQUENA.render(t("esquivou", lang), True, CIANO)
            tela.blit(
                texto_esquivou,
                (player.rect.centerx - texto_esquivou.get_width() // 2, player.rect.y - 42),
            )

        if historia_aviso and tempo_atual - historia_aviso_tempo < 5000:
            titulo_fragmento, texto_fragmento_atual = historia_aviso
            caixa_fragmento = pygame.Rect(0, 0, 600, 70)
            caixa_fragmento.midtop = (LARGURA // 2, ALTURA - 172)
            pygame.draw.rect(tela, PAINEL_UI, caixa_fragmento, border_radius=10)
            pygame.draw.rect(tela, ROXO_UI, caixa_fragmento, 2, border_radius=10)
            titulo_render = FONTE_SYS.render(titulo_fragmento, True, DOURADO_UI)
            descricao_render = FONTE_PEQUENA.render(texto_fragmento_atual, True, BRANCO)
            tela.blit(titulo_render, (caixa_fragmento.centerx - titulo_render.get_width() // 2, caixa_fragmento.y + 8))
            tela.blit(descricao_render, (caixa_fragmento.centerx - descricao_render.get_width() // 2, caixa_fragmento.y + 39))

        if exibir_intro_andar:
            if tempo_atual - intro_timer < 2000:
                s_intro = pygame.Surface((LARGURA, ALTURA))
                s_intro.set_alpha(200)
                s_intro.fill(PRETO)
                tela.blit(s_intro, (0, 0))
                
                t_andar = FONTE_GRANDE.render(f"{t('andar', lang)} {andar_atual}", True, AMARELO)
                t_bioma = FONTE_SYS.render(
                    f"{t('bioma', lang)}: {nome_bioma_localizado(bioma_atual, lang)}",
                    True, VERDE_CLARO,
                )
                
                tela.blit(t_andar, (LARGURA//2 - t_andar.get_width()//2, ALTURA//2 - 30))
                tela.blit(t_bioma, (LARGURA//2 - t_bioma.get_width()//2, ALTURA//2 + 10))
            else:
                exibir_intro_andar = False

        if estado_jogo == "INVENTARIO":
            inventario_tela.desenhar(tela, player, pos_mouse, lang)
            # Tooltip para itens no inventário
            for slot in player.slots_inventario:
                if slot['rect'].collidepoint(pos_mouse) and slot['item']:
                    desenhar_tooltip(tela, slot['item'], pos_mouse)

        elif estado_jogo == "PAUSE":
            s_pause = pygame.Surface((LARGURA, ALTURA))
            s_pause.set_alpha(200)
            s_pause.fill(PRETO)
            tela.blit(s_pause, (0, 0))

            txt_p = FONTE_GRANDE.render(t("pausa", lang), True, DOURADO_UI)
            tela.blit(txt_p, (LARGURA//2 - txt_p.get_width()//2, 120))

            if confirmacao_tipo is None:
                btn_retomar = pygame.Rect(LARGURA//2 - 120, 220, 240, 45)
                btn_pause_lobby = pygame.Rect(LARGURA//2 - 120, 280, 240, 45)
                btn_pause_sair = pygame.Rect(LARGURA//2 - 120, 340, 240, 45)

                for btn, chave_txt, cor_base in [
                    (btn_retomar, "retomar", ROXO_UI),
                    (btn_pause_lobby, "voltar_lobby", PAINEL_UI),
                    (btn_pause_sair, "sair", PAINEL_UI),
                    (pygame.Rect(LARGURA//2 - 120, 400, 240, 45), "pausa_config", PAINEL_UI),
                    (pygame.Rect(LARGURA//2 - 120, 460, 240, 45), "missoes_titulo", PAINEL_UI),
                ]:
                    hover = btn.collidepoint(pos_mouse)
                    cor = PAINEL_UI_CLARO if hover else cor_base
                    pygame.draw.rect(tela, cor, btn, border_radius=8)
                    pygame.draw.rect(tela, ROXO_UI if hover else BORDA_UI, btn, 2 if hover else 1, border_radius=8)
                    txt = FONTE_SYS.render(t(chave_txt, lang), True, DOURADO_UI if hover else BRANCO)
                    tela.blit(txt, (btn.centerx - txt.get_width()//2, btn.centery - txt.get_height()//2))
            else:
                msg_conf = t("confirm_lobby", lang) if confirmacao_tipo == "LOBBY" else t("confirm_sair", lang)
                txt_c = FONTE_SYS.render(msg_conf, True, BRANCO)
                tela.blit(txt_c, (LARGURA//2 - txt_c.get_width()//2, 230))

                btn_sim = pygame.Rect(LARGURA//2 - 110, 300, 100, 40)
                btn_nao = pygame.Rect(LARGURA//2 + 10, 300, 100, 40)

                for btn, chave_txt, cor_base in [(btn_sim, "sim", ROXO_UI), (btn_nao, "nao", PAINEL_UI)]:
                    hover = btn.collidepoint(pos_mouse)
                    cor = PAINEL_UI_CLARO if hover else cor_base
                    pygame.draw.rect(tela, cor, btn, border_radius=8)
                    pygame.draw.rect(tela, ROXO_UI if hover else BORDA_UI, btn, 2 if hover else 1, border_radius=8)
                    txt = FONTE_SYS.render(t(chave_txt, lang), True, DOURADO_UI if hover else BRANCO)
                    tela.blit(txt, (btn.centerx - txt.get_width()//2, btn.centery - txt.get_height()//2))

    elif estado_jogo == "CONFIGURACOES":
        menu_config.desenhar(tela, CONFIG_JOGO, pos_mouse)

    elif estado_jogo == "INDEX":
        index_tela.desenhar(tela, pos_mouse, CONFIG_JOGO)

    elif estado_jogo == "CONQUISTAS":
        tela_conquistas.desenhar(tela, conquistas_mgr, pos_mouse, CONFIG_JOGO)

    elif estado_jogo == "MISSOES":
        missoes_tela.desenhar(tela, pos_mouse, CONFIG_JOGO)

    elif estado_jogo == "HISTORIA":
        tela.fill(FUNDO_UI)
        titulo = FONTE_TITULO.render(t("historia_titulo", lang), True, ROXO_UI)
        tela.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 25))
        dados_historia = carregar_dados()
        descobertos = dados_historia.get("fragmentos_historia", {})
        painel_lista = pygame.Rect(16, 92, 300, 455)
        painel_texto = pygame.Rect(330, 92, LARGURA - 346, 455)
        for painel in (painel_lista, painel_texto):
            pygame.draw.rect(tela, PAINEL_UI, painel, border_radius=10)
            pygame.draw.rect(tela, BORDA_UI, painel, 1, border_radius=10)
        for indice in range(1, len(FRAGMENTOS_BIOMAS) + 1):
            y = 104 + (indice - 1) * 28
            rect_fragmento = pygame.Rect(25, y, 282, 25)
            liberado = bool(descobertos.get(str(indice)))
            ativo = indice == fragmento_selecionado
            if ativo:
                pygame.draw.rect(tela, PAINEL_UI_CLARO, rect_fragmento, border_radius=5)
            nome_bioma, nome_fragmento = FRAGMENTOS_BIOMAS[indice]
            label = (
                f"{indice:02d} · {nome_bioma}"
                if liberado
                else f"{indice:02d} · {t('historia_bloqueado', lang)}"
            )
            render = FONTE_PEQUENA.render(label, True, DOURADO_UI if ativo else (BRANCO if liberado else CINZA_CLARO))
            tela.blit(render, (rect_fragmento.x + 7, rect_fragmento.centery - render.get_height() // 2))
        if descobertos.get(str(fragmento_selecionado)):
            nome_bioma, texto_historia = texto_fragmento(fragmento_selecionado, lang)
            titulo_historia = FONTE_GRANDE.render(nome_bioma, True, DOURADO_UI)
            tela.blit(titulo_historia, (painel_texto.x + 18, painel_texto.y + 22))
            palavras = texto_historia.split()
            linha_atual = ""
            y_historia = painel_texto.y + 90
            for palavra in palavras:
                candidato = f"{linha_atual} {palavra}".strip()
                if FONTE_SYS.size(candidato)[0] > painel_texto.width - 36:
                    render_linha = FONTE_SYS.render(linha_atual, True, BRANCO)
                    tela.blit(render_linha, (painel_texto.x + 18, y_historia))
                    y_historia += 27
                    linha_atual = palavra
                else:
                    linha_atual = candidato
            if linha_atual:
                render_linha = FONTE_SYS.render(linha_atual, True, BRANCO)
                tela.blit(render_linha, (painel_texto.x + 18, y_historia))
        btn_voltar_historia = pygame.Rect(LARGURA // 2 - 110, ALTURA - 58, 220, 38)
        hover_historia = btn_voltar_historia.collidepoint(pos_mouse)
        pygame.draw.rect(tela, PAINEL_UI_CLARO if hover_historia else PAINEL_UI, btn_voltar_historia, border_radius=8)
        pygame.draw.rect(tela, ROXO_UI if hover_historia else BORDA_UI, btn_voltar_historia, 1, border_radius=8)
        texto_voltar_historia = FONTE_SYS.render(t("voltar", lang), True, BRANCO)
        tela.blit(texto_voltar_historia, (btn_voltar_historia.centerx - texto_voltar_historia.get_width() // 2, btn_voltar_historia.centery - texto_voltar_historia.get_height() // 2))

    elif estado_jogo == "GAME_OVER":
        tela.fill(FUNDO_UI)
        pygame.draw.circle(tela, (32, 30, 48), (LARGURA // 2, 100), 150, 1)
        pygame.draw.circle(tela, (28, 35, 54), (LARGURA // 2, 100), 126, 1)
        pygame.draw.rect(tela, PAINEL_UI, (135, 145, LARGURA - 270, 275), border_radius=18)
        pygame.draw.rect(tela, BORDA_UI, (135, 145, LARGURA - 270, 275), 2, border_radius=18)
        txt_brand = FONTE_GRANDE.render("ASTREA", True, ROXO_UI)
        tela.blit(txt_brand, (LARGURA // 2 - txt_brand.get_width() // 2, 20))
        txt_t = FONTE_TITULO.render(t("game_over", lang), True, (220, 112, 123))
        tela.blit(txt_t, (LARGURA//2 - txt_t.get_width()//2, 74))

        lines_e = [
            f"{t('tempo_jogado', lang)}: {estatisticas_run['tempo_segundos']} {t('segundos', lang)}",
            f"{t('mobs_mortos', lang)}: {estatisticas_run['mobs_mortos']}",
            f"{t('run_dano_causado', lang)}: {estatisticas_run.get('dano_causado', 0)}",
            f"{t('run_salas_concluidas', lang)}: {estatisticas_run.get('salas_concluidas', 0)}",
            f"{t('run_salas_sem_dano', lang)}: {estatisticas_run.get('salas_sem_dano', 0)}",
            f"{t('run_raros_derrotados', lang)}: {estatisticas_run.get('inimigos_raros_derrotados', 0)}",
            f"{t('gemas_run', lang)}: {estatisticas_run['gemas_coletadas']}",
            f"{t('morreu_andar', lang)}: {estatisticas_run['andar_morte']}",
        ]
        y_e = 180
        for indice, linha in enumerate(lines_e):
            cor_linha = CIANO_UI if indice in (2, 4, 6) else BRANCO
            txt_s = FONTE_PEQUENA.render(linha, True, cor_linha)
            tela.blit(txt_s, (LARGURA // 2 - txt_s.get_width() // 2, y_e))
            y_e += 28

        painel_recordes = pygame.Rect(14, 430, 250, 154)
        pygame.draw.rect(tela, PAINEL_UI, painel_recordes, border_radius=8)
        pygame.draw.rect(tela, BORDA_UI, painel_recordes, 1, border_radius=8)
        titulo_recordes = FONTE_SYS.render(t("melhores_runs", lang), True, DOURADO_UI)
        tela.blit(titulo_recordes, (painel_recordes.x + 8, painel_recordes.y + 6))
        for indice, (modo, registro) in enumerate(melhores_runs_cache.items()):
            resumo = (
                t("registro_run_curto", lang).format(
                    andar=registro.get("andar", 1),
                    gemas=registro.get("gemas", 0),
                )
                if registro else t("sem_registro", lang)
            )
            label_recorde = FONTE_PEQUENA.render(
                f"{t('dificuldade_' + modo.lower(), lang)}: {resumo}",
                True, BRANCO,
            )
            tela.blit(label_recorde, (painel_recordes.x + 8, painel_recordes.y + 30 + indice * 26))

        btn_jogar_novamente = pygame.Rect(LARGURA//2 - 120, 505, 240, 40)
        hover_reiniciar = btn_jogar_novamente.collidepoint(pos_mouse)
        cor = PAINEL_UI_CLARO if hover_reiniciar else PAINEL_UI
        pygame.draw.rect(tela, (4, 6, 13), btn_jogar_novamente.move(0, 4), border_radius=10)
        pygame.draw.rect(tela, cor, btn_jogar_novamente, border_radius=10)
        pygame.draw.rect(tela, CIANO_UI if hover_reiniciar else BORDA_UI, btn_jogar_novamente, 2, border_radius=10)
        txt_j = FONTE_SYS.render(t("jogar_denovo", lang), True, CIANO_UI if hover_reiniciar else BRANCO)
        tela.blit(txt_j, (btn_jogar_novamente.centerx - txt_j.get_width()//2, btn_jogar_novamente.centery - txt_j.get_height()//2))
        btn_lobby_game_over = pygame.Rect(LARGURA // 2 - 120, 550, 240, 40)
        hover_lobby = btn_lobby_game_over.collidepoint(pos_mouse)
        cor_lobby = PAINEL_UI_CLARO if hover_lobby else PAINEL_UI
        pygame.draw.rect(tela, cor_lobby, btn_lobby_game_over, border_radius=10)
        pygame.draw.rect(tela, DOURADO_UI if hover_lobby else BORDA_UI, btn_lobby_game_over, 1, border_radius=10)
        txt_lobby_game_over = FONTE_SYS.render(
            t("voltar_lobby", lang), True, DOURADO_UI if hover_lobby else BRANCO
        )
        tela.blit(
            txt_lobby_game_over,
            (
                btn_lobby_game_over.centerx - txt_lobby_game_over.get_width() // 2,
                btn_lobby_game_over.centery - txt_lobby_game_over.get_height() // 2,
            ),
        )

    elif estado_jogo == "CICLO_FIM":
        tela.fill(FUNDO_UI)
        pygame.draw.circle(tela, (48, 35, 85), (LARGURA // 2, 110), 155, 2)
        pygame.draw.rect(tela, PAINEL_UI, (115, 150, LARGURA - 230, 340), border_radius=18)
        pygame.draw.rect(tela, ROXO_UI, (115, 150, LARGURA - 230, 340), 2, border_radius=18)
        titulo_ciclo = FONTE_TITULO.render(t("fim_ciclo_titulo", lang), True, DOURADO_UI)
        tela.blit(titulo_ciclo, (LARGURA // 2 - titulo_ciclo.get_width() // 2, 185))
        linha_ciclo = FONTE_SYS.render(t("fim_ciclo_texto", lang), True, BRANCO)
        tela.blit(linha_ciclo, (LARGURA // 2 - linha_ciclo.get_width() // 2, 260))
        texto_floors = FONTE_GRANDE.render(
            f"{andar_atual}  ·  {nome_bioma_localizado(bioma_atual, lang)}",
            True, CIANO_UI,
        )
        tela.blit(texto_floors, (LARGURA // 2 - texto_floors.get_width() // 2, 300))
        for rect, chave in (
            (pygame.Rect(LARGURA // 2 - 150, 340, 300, 48), "fim_ciclo_continuar"),
            (pygame.Rect(LARGURA // 2 - 150, 405, 300, 48), "fim_ciclo_lobby"),
        ):
            hover = rect.collidepoint(pos_mouse)
            pygame.draw.rect(tela, PAINEL_UI_CLARO if hover else PAINEL_UI, rect, border_radius=9)
            pygame.draw.rect(tela, ROXO_UI if hover else BORDA_UI, rect, 2 if hover else 1, border_radius=9)
            label = FONTE_SYS.render(t(chave, lang), True, DOURADO_UI if hover else BRANCO)
            tela.blit(label, (rect.centerx - label.get_width() // 2, rect.centery - label.get_height() // 2))

    if (
        estado_jogo in ("JOGANDO", "INVENTARIO", "PAUSE")
        and registrar_baixa_vida(player, tempo_atual, audio)
    ):
        desenhar_efeito_vida_baixa(tela)
    controles_touch.desenhar(tela, estado_jogo == "JOGANDO")
    desenhar_fade(tela)
    pygame.display.flip()

pygame.quit()
sys.exit()