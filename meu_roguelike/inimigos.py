# inimigos.py
import pygame
import math
import random
from config import LARGURA, ALTURA, VERMELHO, AMARELO, VERDE, CIANO, CONFIG_JOGO, obter_multiplicadores_andar, obter_gemas_chefe, arredondar_para_5
from jogador import dash_invulneravel
from progressao import registrar_abate, registrar_abate_diario, concluir_contrato
from reliquias import registrar_abate_reliquias
from idiomas import t
from banco_itens import TODAS_ARMAS
from missoes import registrar_progresso
from cosmeticos import COSMETICOS, desbloquear_cosmetico, sortear_cosmetico_bloqueado
from save import carregar_dados, salvar_dados


_ATAQUES_CHEFES = {
    1: {"nome": "Lodo", "angulos": (0,), "velocidade": 5.0, "efeito": "fraqueza", "duracao": 3000},
    2: {"nome": "Raízes", "angulos": (-0.18, 0, 0.18), "velocidade": 4.8, "efeito": "atordoamento", "duracao": 1800},
    3: {"nome": "Estilhaços", "angulos": (-0.4, -0.2, 0, 0.2, 0.4), "velocidade": 7.5, "efeito": "lentidao", "duracao": 2800},
    4: {"nome": "Ferrão", "angulos": (-0.12, 0.12), "velocidade": 8.5, "efeito": "veneno", "duracao": 3200},
    5: {"nome": "Jatos de Veneno", "angulos": (-0.3, 0, 0.3), "velocidade": 5.5, "efeito": "veneno", "duracao": 3500},
    6: {"nome": "Corte Espectral", "angulos": (0, math.pi / 2), "velocidade": 7.4, "efeito": "vulnerabilidade", "duracao": 2800},
    7: {"nome": "Rajada Glacial", "angulos": (-0.35, 0, 0.35), "velocidade": 5.2, "efeito": "lentidao", "duracao": 3800},
    8: {"nome": "Explosão de Magma", "angulos": tuple(i * math.pi / 4 for i in range(8)), "velocidade": 5.8, "efeito": "queimadura", "duracao": 3500},
    9: {"nome": "Lâminas Sombrias", "angulos": (-0.07, 0.07), "velocidade": 9.0, "efeito": "maldicao", "duracao": 3000},
    10: {"nome": "Sopro Dracônico", "angulos": (-0.48, -0.32, -0.16, 0, 0.16, 0.32, 0.48), "velocidade": 7.2, "efeito": "queimadura", "duracao": 4000},
    11: {"nome": "Anel de Brasas", "angulos": tuple(i * math.pi / 5 for i in range(10)), "velocidade": 6.4, "efeito": "queimadura", "duracao": 4200},
    12: {"nome": "Lanças Celestes", "angulos": (-0.7, -0.35, 0, 0.35, 0.7), "velocidade": 8.6, "efeito": "vulnerabilidade", "duracao": 3200},
    13: {"nome": "Tempestade de Areia", "angulos": (-0.45, -0.2, 0.2, 0.45), "velocidade": 6.0, "efeito": "fraqueza", "duracao": 3500},
    14: {"nome": "Fenda Perseguidora", "angulos": (-0.25, 0, 0.25), "velocidade": 9.0, "efeito": "atordoamento", "duracao": 1800},
    15: {"nome": "Espiral do Nada", "angulos": tuple(i * math.pi / 8 for i in range(16)), "velocidade": 8.0, "efeito": "maldicao", "duracao": 4000},
}

_AREAS_CHEFES = {
    1: (220, 220), 2: (180, 300), 3: (260, 260), 4: (340, 100), 5: (300, 300),
    6: (200, 360), 7: (340, 150), 8: (320, 320), 9: (240, 180), 10: (360, 260),
    11: (320, 240), 12: (220, 360), 13: (360, 180), 14: (280, 280), 15: (400, 320),
}

_ATAQUES_FASES_CHEFES = {
    3: {
        2: {"nome": "Prisma Quebrado", "angulos": tuple(i * math.pi / 3 for i in range(6)), "velocidade": 8.0, "efeito": "lentidao", "duracao": 3000},
    },
    6: {
        2: {"nome": "Corte das Almas", "angulos": (-0.55, -0.25, 0, 0.25, 0.55), "velocidade": 8.8, "efeito": "maldicao", "duracao": 3200},
    },
    8: {
        2: {"nome": "Chuva de Magma", "angulos": tuple(i * math.pi / 4 for i in range(8)), "velocidade": 6.8, "efeito": "queimadura", "duracao": 3500},
        3: {"nome": "Erupção Final", "angulos": tuple(i * math.pi / 6 for i in range(12)), "velocidade": 8.2, "efeito": "queimadura", "duracao": 4000},
    },
    10: {
        2: {"nome": "Garras Abissais", "angulos": (-0.75, -0.5, -0.25, 0, 0.25, 0.5, 0.75), "velocidade": 8.5, "efeito": "maldicao", "duracao": 3500},
        3: {"nome": "Eclipse Dracônico", "angulos": tuple(i * math.pi / 8 for i in range(16)), "velocidade": 9.0, "efeito": "queimadura", "duracao": 4500},
    },
    11: {
        2: {"nome": "Supernova Cinzenta", "angulos": tuple(i * math.pi / 6 for i in range(12)), "velocidade": 8.0, "efeito": "queimadura", "duracao": 4500},
    },
    12: {
        2: {"nome": "Queda dos Serafins", "angulos": (-0.8, -0.4, 0, 0.4, 0.8), "velocidade": 10.0, "efeito": "vulnerabilidade", "duracao": 3500},
    },
    13: {
        2: {"nome": "Sepulcro Desperto", "angulos": tuple(i * math.pi / 4 for i in range(8)), "velocidade": 7.0, "efeito": "fraqueza", "duracao": 3500},
    },
    14: {
        2: {"nome": "Rasgo Temporal", "angulos": (-0.65, -0.3, 0, 0.3, 0.65), "velocidade": 10.0, "efeito": "atordoamento", "duracao": 1800},
    },
    15: {
        2: {"nome": "Horizonte de Eventos", "angulos": tuple(i * math.pi / 5 for i in range(10)), "velocidade": 8.8, "efeito": "maldicao", "duracao": 4200},
        3: {"nome": "Colapso Final", "angulos": tuple(i * math.pi / 12 for i in range(24)), "velocidade": 9.5, "efeito": "vulnerabilidade", "duracao": 4500},
    },
}

_ATAQUES_POR_CLASSE = {
    "Guerreiro": {"nome": "Investida de Aço", "angulos": (-0.22, 0, 0.22), "velocidade": 6.2, "efeito": "fraqueza", "duracao": 2600},
    "Espadachim": {"nome": "Corte Cruzado", "angulos": (-0.5, 0.5), "velocidade": 8.2, "efeito": "vulnerabilidade", "duracao": 2400},
    "Mago": {"nome": "Espiral Arcana", "angulos": tuple(i * math.pi / 4 for i in range(8)), "velocidade": 6.0, "efeito": "maldicao", "duracao": 3200},
    "Atirador": {"nome": "Rajada de Precisão", "angulos": (-0.32, -0.16, 0, 0.16, 0.32), "velocidade": 9.0, "efeito": "atordoamento", "duracao": 1400},
    "Caçador": {"nome": "Rastro Selvagem", "angulos": (-0.28, 0, 0.28), "velocidade": 7.0, "efeito": "lentidao", "duracao": 3200},
    "Ladrão": {"nome": "Lâminas Ocultas", "angulos": (-0.12, 0.12), "velocidade": 10.0, "efeito": "veneno", "duracao": 3000},
}


def _ataque_chefe_para_classe(ataque, classe):
    alternativo = _ATAQUES_POR_CLASSE.get(classe)
    return alternativo.copy() if alternativo else ataque


def aplicar_dano_player(
    player,
    particulas,
    dano,
    tempo_atual,
    status_manager=None,
    chance_critico=0.0,
    efeito=None,
    duracao_efeito=0,
    audio_manager=None,
):
    if dash_invulneravel(player, tempo_atual):
        if tempo_atual - getattr(player, "esquivou_ultimo_aviso", -1000) >= 600:
            player.esquivou_ultimo_aviso = tempo_atual
            player.esquivou_tempo = tempo_atual + 800
        return False
    if player.imortal or tempo_atual - player.ultimo_dano_recebido <= 800:
        return False

    player.ultimo_dano_recebido = tempo_atual
    player.dano_recebido_total = getattr(player, "dano_recebido_total", 0) + 1
    multiplicador_recebido = getattr(player, "multiplicador_dano_recebido", 1.0)
    multiplicador_recebido *= getattr(player, "multiplicador_dano_recebido_run", 1.0)
    evento = getattr(player, "evento_bioma_ativo", None)
    if evento and tempo_atual < evento.get("fim", 0):
        multiplicador_recebido *= 1 + evento.get("dano_recebido", 0)
    defesa_run = getattr(player, "buffs_run", {}).get("defesa", 0.0)
    dano_final = max(
        5,
        arredondar_para_5(
            dano * max(0.1, 1.0 - player.defesa_percent - defesa_run) * multiplicador_recebido
        ),
    )
    eh_critico = random.random() < min(0.35, max(0.0, chance_critico))
    if eh_critico:
        dano_final = max(5, arredondar_para_5(dano_final * 1.5))
    player.hp = max(0, player.hp - dano_final)
    particulas.criar_texto_dano(
        player.rect.centerx,
        player.rect.y - 15,
        f"-{dano_final}!" if eh_critico else f"-{dano_final}",
        VERMELHO,
    )
    if status_manager and efeito and random.random() < (0.25 if efeito == "sangramento" else 0.5):
        valores = {
            "sangramento": 3,
            "lentidao": 0.4,
            "fraqueza": 0.25,
            "atordoamento": 0,
            "maldicao": 0.3,
            "vulnerabilidade": 0.25,
            "exaustao": 0.2,
            "cegueira": 0,
            "corrosao": 0.2,
        }
        valor = valores.get(efeito, 0.25)
        status_manager.adicionar_efeito(efeito, "debuff", duracao_efeito or 3500, valor)
    if audio_manager:
        audio_manager.tocar_som("critico" if eh_critico else "dano")
    return True


def aplicar_dano_inimigo(
    inimigo, dano, eh_critico, tempo_atual, audio_manager=None, estatisticas_run=None
):
    if inimigo.get("horda_ativa") or tempo_atual < inimigo.get("tempo_imortal_fim", 0):
        return 0
    dano = max(5, arredondar_para_5(dano))
    escudo = max(0, inimigo.get("escudo", 0))
    if escudo:
        absorvido = min(escudo, dano)
        inimigo["escudo"] = escudo - absorvido
        dano -= absorvido
        if dano <= 0:
            return absorvido
    if inimigo.get("modificador_elite") == "blindado":
        dano = max(5, arredondar_para_5(dano * 0.8))
    vida_antes = max(0, inimigo["hp"])
    inimigo["hp"] -= dano
    if isinstance(estatisticas_run, dict):
        estatisticas_run["dano_causado"] = (
            estatisticas_run.get("dano_causado", 0) + min(dano, vida_antes)
        )
    if eh_critico and random.random() < 0.2:
        inimigo["congelado_fim"] = max(inimigo.get("congelado_fim", 0), tempo_atual + 1800)
    if eh_critico:
        if audio_manager:
            audio_manager.tocar_som("critico")
        if random.random() < 0.3:
            inimigo["sangramento_fim"] = max(
                inimigo.get("sangramento_fim", 0), tempo_atual + 3500
            )
            inimigo["sangramento_tick"] = tempo_atual
    return dano


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
        self.tamanho_aoe = (260, 260)

    def atualizar_e_colidir(
        self,
        sala,
        player,
        particulas,
        estatisticas_run,
        projeteis_inimigos,
        status_manager=None,
        audio_manager=None,
        players=None,
        status_managers=None,
    ):
        tempo_atual = pygame.time.get_ticks()
        dificuldade = obter_multiplicadores_andar(getattr(sala, "andar", 1))
        mult_velocidade_base = dificuldade['multiplicador_velocidade_inimigo']
        todos_jogadores = players or [player]
        todos_status = status_managers or [status_manager] * len(todos_jogadores)
        pares_jogadores = [
            (alvo, todos_status[indice] if indice < len(todos_status) else status_manager)
            for indice, alvo in enumerate(todos_jogadores) if alvo.hp > 0
        ] or [(player, status_manager)]
        jogadores_ativos = [par[0] for par in pares_jogadores]
        gestores_status = [par[1] for par in pares_jogadores]

        for inimigo in sala.inimigos[:]:
            if 'rect' not in inimigo:
                continue
            mult_velocidade = mult_velocidade_base
            if tempo_atual < inimigo.get("congelado_fim", 0):
                mult_velocidade *= 0.55
            
            r = inimigo['rect']
            r.clamp_ip(pygame.Rect(80, 80, LARGURA - 160, ALTURA - 160))

            indice_alvo = min(
                range(len(jogadores_ativos)),
                key=lambda indice: math.dist(jogadores_ativos[indice].rect.center, r.center),
            )
            player = jogadores_ativos[indice_alvo]
            status_manager = gestores_status[indice_alvo] if indice_alvo < len(gestores_status) else None
            tipo = inimigo.get('tipo', 'melee')
            px, py = player.rect.center
            ix, iy = r.center
            dist = math.hypot(px - ix, py - iy)

            if inimigo.get("elite"):
                mult_velocidade *= inimigo.get("multiplicador_velocidade", 1.0)

            if tipo == 'boss':
                hp_max = inimigo['hp_max']

                fases_total = inimigo.get("fases_total", 1)
                fase_atual = inimigo.get("fase_atual", 1)
                fase_fim = inimigo.get("fase_transicao_fim", 0)
                if fase_fim:
                    if tempo_atual >= fase_fim:
                        fase_atual += 1
                        inimigo["fase_atual"] = fase_atual
                        inimigo["fase_transicao_fim"] = 0
                        inimigo["hp"] = hp_max
                        self.boss_em_preparacao = False
                        self.boss_em_dash = False
                        self.boss_em_aoe = False
                        particulas.criar_texto_dano(
                            r.centerx, r.y - 25,
                            f"FASE {fase_atual}!", AMARELO, True,
                        )
                    else:
                        continue
                if fase_atual < fases_total:
                    limiar = 0.5 if fases_total == 2 else (
                        2 / 3 if fase_atual == 1 else 1 / 3
                    )
                    if inimigo["hp"] <= hp_max * limiar:
                        inimigo["hp"] = 1
                        inimigo["fase_transicao_fim"] = tempo_atual + 2000
                        inimigo["tempo_imortal_fim"] = tempo_atual + 2000
                        self.boss_em_preparacao = False
                        self.boss_em_dash = False
                        self.boss_em_aoe = False
                        particulas.criar_texto_dano(
                            r.centerx, r.y - 25,
                            "MUDANDO DE FASE - IMORTAL!", AMARELO, True,
                        )
                        continue

                if inimigo.get("horda_ativa"):
                    servos = [
                        mob for mob in sala.inimigos
                        if mob.get("invocado_pelo_boss") == id(inimigo) and mob.get("hp", 0) > 0
                    ]
                    if servos:
                        continue
                    inimigo["horda_ativa"] = False
                    inimigo["tempo_imortal_fim"] = 0
                    inimigo["ultimo_ataque_especial"] = tempo_atual
                    particulas.criar_texto_dano(
                        r.centerx, r.y - 25, "A Horda foi derrotada!", CIANO, True,
                    )

                marcos_horda = inimigo.setdefault("hordas_invocadas", [])
                porcentagem_vida = inimigo["hp"] / max(1, hp_max)
                marco_horda = next(
                    (marco for marco in (0.70, 0.35) if porcentagem_vida <= marco and marco not in marcos_horda),
                    None,
                )
                if marco_horda is not None:
                    marcos_horda.append(marco_horda)
                    inimigo["horda_ativa"] = True
                    inimigo["tempo_imortal_fim"] = float("inf")
                    quantidade = 3 + fase_atual
                    servo_hp = max(10, arredondar_para_5(hp_max * 0.035))
                    for indice_servo in range(quantidade):
                        angulo_servo = math.tau * indice_servo / quantidade
                        sala.inimigos.append({
                            "tipo": "melee" if indice_servo % 2 == 0 else "assassin",
                            "nome": "Servo da Horda",
                            "rect": pygame.Rect(
                                int(r.centerx + math.cos(angulo_servo) * 115 - 13),
                                int(r.centery + math.sin(angulo_servo) * 115 - 13),
                                26, 26,
                            ),
                            "hp": servo_hp,
                            "hp_max": servo_hp,
                            "dano_contato": arredondar_para_5(inimigo.get("dano_contato", 20) * 0.35),
                            "chance_critico": 0.08,
                            "bioma_id": inimigo.get("bioma_id", sala.bioma_id),
                            "invocado": True,
                            "invocado_pelo_boss": id(inimigo),
                        })
                    particulas.criar_texto_dano(
                        r.centerx, r.y - 25, "O CHEFE INVOCA A HORDA!", VERMELHO, True,
                    )
                    if audio_manager:
                        audio_manager.tocar_som("invocacao")
                    continue

                if not inimigo.get('rage_ativado', False) and inimigo['hp'] <= hp_max / 3:
                    inimigo['rage_ativado'] = True
                    vida_rec = arredondar_para_5(hp_max * 0.15)
                    inimigo['hp'] = min(hp_max, inimigo['hp'] + vida_rec)
                    inimigo['tempo_imortal_fim'] = tempo_atual + 5000
                    particulas.criar_texto_dano(r.centerx, r.y - 25, f"MODO FÚRIA! +{vida_rec} HP & IMORTAL (5s)!", AMARELO)

                em_furia = inimigo.get('rage_ativado', False) or (inimigo['hp'] <= hp_max * 0.6)
                vel_boss = (4.5 if em_furia else 2.5) * mult_velocidade
                cd_dash = (2000 if em_furia else 3500) / mult_velocidade

                if self.boss_em_aoe:
                    if tempo_atual - self.tempo_inicio_aoe >= 1000:
                        self.boss_em_aoe = False
                        largura_aoe, altura_aoe = self.tamanho_aoe
                        if em_furia:
                            largura_aoe = int(largura_aoe * 1.2)
                            altura_aoe = int(altura_aoe * 1.2)
                        aoe_rect = pygame.Rect(0, 0, largura_aoe, altura_aoe)
                        aoe_rect.center = self.pos_alvo_aoe
                        for alvo_indice, alvo in enumerate(jogadores_ativos):
                            if not alvo.rect.colliderect(aoe_rect):
                                continue
                            dano = max(5, arredondar_para_5(
                                inimigo.get('dano_contato', 30) * (1.65 if em_furia else 1.25)
                            ))
                            aplicar_dano_player(
                                alvo, particulas, dano, tempo_atual,
                                gestores_status[alvo_indice] if alvo_indice < len(gestores_status) else status_manager,
                                inimigo.get("chance_critico", 0.08), inimigo.get("efeito_especial", "lentidao"), 3200, audio_manager,
                            )
                    continue

                if self.boss_em_dash:
                    if tempo_atual - self.tempo_inicio_dash > 300:
                        self.boss_em_dash = False
                        self.boss_em_aoe = True
                        self.tempo_inicio_aoe = tempo_atual
                        self.pos_alvo_aoe = r.center
                        self.tamanho_aoe = _AREAS_CHEFES.get(
                            int(inimigo.get("bioma_id", 1)), _AREAS_CHEFES[1]
                        )
                    else:
                        rect_anterior = r.copy()
                        deslocamento_x = int(self.dir_dash_x * 18 * mult_velocidade)
                        deslocamento_y = int(self.dir_dash_y * 18 * mult_velocidade)
                        r.x += deslocamento_x
                        r.y += deslocamento_y
                        r.clamp_ip(pygame.Rect(80, 80, LARGURA - 160, ALTURA - 160))

                        dx_real = r.x - rect_anterior.x
                        dy_real = r.y - rect_anterior.y
                        passos = max(1, int(max(abs(dx_real), abs(dy_real)) / 8))
                        jogadores_atingidos = set()
                        for passo in range(1, passos + 1):
                            posicao = rect_anterior.copy()
                            fracao = passo / passos
                            posicao.x = round(rect_anterior.x + dx_real * fracao)
                            posicao.y = round(rect_anterior.y + dy_real * fracao)
                            for alvo_indice, alvo in enumerate(jogadores_ativos):
                                if alvo.rect.colliderect(posicao):
                                    jogadores_atingidos.add(alvo_indice)
                        if jogadores_atingidos:
                            dano = max(5, arredondar_para_5(inimigo.get('dano_contato', 30)))
                            for alvo_indice in jogadores_atingidos:
                                aplicar_dano_player(
                                    jogadores_ativos[alvo_indice], particulas, dano,
                                    tempo_atual,
                                    gestores_status[alvo_indice] if alvo_indice < len(gestores_status) else status_manager,
                                    inimigo.get("chance_critico", 0.08), "lentidao", 2500, audio_manager,
                                )
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

                intervalo_especial = 2300 if em_furia else 3400
                ataque_pendente = inimigo.get("ataque_especial_pendente")
                if ataque_pendente:
                    if tempo_atual - ataque_pendente["inicio"] >= ataque_pendente["aviso_ms"]:
                        inimigo["ataque_especial_pendente"] = None
                        ataque = ataque_pendente["ataque"]
                        for deslocamento in ataque["angulos"]:
                            angulo = ataque_pendente["angulo"] + deslocamento
                            velocidade = ataque["velocidade"]
                            projeteis_inimigos.append({
                                "x": r.centerx, "y": r.centery,
                                "vx": math.cos(angulo) * velocidade * mult_velocidade,
                                "vy": math.sin(angulo) * velocidade * mult_velocidade,
                                "dano": max(5, arredondar_para_5(inimigo.get("dano_contato", 34) * 0.75)),
                                "efeito": ataque["efeito"],
                                "duracao_efeito": ataque["duracao"],
                                "ataque_chefe": ataque["nome"],
                            })
                elif tempo_atual - inimigo.get("ultimo_ataque_especial", 0) >= intervalo_especial / mult_velocidade and dist > 0:
                    inimigo["ultimo_ataque_especial"] = tempo_atual
                    angulo_base = math.atan2(py - r.centery, px - r.centerx)
                    bioma_id = int(inimigo.get("bioma_id", 1))
                    fase = inimigo.get("fase_atual", 1)
                    ataque = _ATAQUES_FASES_CHEFES.get(bioma_id, {}).get(
                        fase, _ATAQUES_CHEFES.get(bioma_id, _ATAQUES_CHEFES[1])
                    )
                    ataque = _ataque_chefe_para_classe(
                        ataque, CONFIG_JOGO.get("classe_jogador", "")
                    )
                    inimigo["ultimo_ataque_aviso"] = ataque["nome"]
                    inimigo["ataque_especial_pendente"] = {
                        "inicio": tempo_atual,
                        "aviso_ms": 700,
                        "angulo": angulo_base,
                        "ataque": ataque,
                    }

                if (
                    not inimigo.get("ataque_especial_pendente")
                    and tempo_atual - self.ultimo_dash_boss > cd_dash
                ):
                    self.ultimo_dash_boss = tempo_atual
                    self.boss_em_preparacao = True
                    self.tempo_inicio_preparacao = tempo_atual
                    if dist > 0:
                        self.dir_dash_x = (px - ix) / dist
                        self.dir_dash_y = (py - iy) / dist

            elif tipo == 'mimico':
                if 0 < dist < 420:
                    r.x += int((px - ix) / dist * 4.2 * mult_velocidade)
                    r.y += int((py - iy) / dist * 4.2 * mult_velocidade)
            elif tipo == "assassin":
                if dist > 0:
                    em_investida = tempo_atual < inimigo.get("investida_fim", 0)
                    if em_investida:
                        velocidade = 7.0
                    elif tempo_atual >= inimigo.get("proxima_investida", 0):
                        inimigo["investida_fim"] = tempo_atual + 350
                        inimigo["proxima_investida"] = tempo_atual + 1800
                        velocidade = 7.0
                    else:
                        velocidade = 2.8
                    r.x += int((px - ix) / dist * velocidade * mult_velocidade)
                    r.y += int((py - iy) / dist * velocidade * mult_velocidade)
            elif tipo == "duelist":
                if dist > 0:
                    if tempo_atual >= inimigo.get("proxima_investida", 0):
                        inimigo["investida_fim"] = tempo_atual + 260
                        inimigo["proxima_investida"] = tempo_atual + 1900
                    velocidade = 6.2 if tempo_atual < inimigo.get("investida_fim", 0) else 2.6
                    r.x += int((px - ix) / dist * velocidade * mult_velocidade)
                    r.y += int((py - iy) / dist * velocidade * mult_velocidade)
            elif tipo == "bomber":
                if dist > 0:
                    if dist <= inimigo.get("raio_explosao", 95):
                        dano_explosao = inimigo.get("dano_explosao", inimigo.get("dano_contato", 20))
                        if player.rect.inflate(70, 70).colliderect(r):
                            aplicar_dano_player(
                                player, particulas, dano_explosao, tempo_atual,
                                status_manager, inimigo.get("chance_critico", 0.08),
                                "queimadura", 2000, audio_manager,
                            )
                        particulas.criar_explosao(ix, iy, AMARELO)
                        inimigo["hp"] = 0
                    else:
                        r.x += int((px - ix) / dist * 2.5 * mult_velocidade)
                        r.y += int((py - iy) / dist * 2.5 * mult_velocidade)
            elif tipo == 'melee':
                if dist > 0:
                    r.x += int((px - ix) / dist * 3 * mult_velocidade)
                    r.y += int((py - iy) / dist * 3 * mult_velocidade)
            elif tipo == 'tank':
                if dist > 0:
                    r.x += int((px - ix) / dist * 1.8 * mult_velocidade)
                    r.y += int((py - iy) / dist * 1.8 * mult_velocidade)
            elif tipo in ('ranged', 'mage', 'trapper'):
                if dist > 220 and dist > 0:
                    velocidade = 1.8 if tipo in ("mage", "trapper") else 2.2
                    r.x += int((px - ix) / dist * velocidade * mult_velocidade)
                    r.y += int((py - iy) / dist * velocidade * mult_velocidade)
                elif tipo in ("mage", "trapper") and 0 < dist < 170:
                    r.x += int((ix - px) / dist * 1.5 * mult_velocidade)
                    r.y += int((iy - py) / dist * 1.5 * mult_velocidade)
                ultimo_tiro = inimigo.get('ultimo_tiro', 0)
                intervalo = 1900 if tipo in ("mage", "trapper") else 2000
                if tempo_atual - ultimo_tiro > intervalo / mult_velocidade:
                    inimigo['ultimo_tiro'] = tempo_atual
                    if dist > 0:
                        velocidade_projetil = 4.5 if tipo == "trapper" else 5 if tipo == "mage" else 6
                        vx = (px - ix) / dist * velocidade_projetil * mult_velocidade
                        vy = (py - iy) / dist * velocidade_projetil * mult_velocidade
                        dano = int(inimigo.get('dano_contato', 10))
                        projetil = {'x': ix, 'y': iy, 'vx': vx, 'vy': vy, 'dano': dano}
                        if tipo in ("mage", "trapper"):
                            projetil["efeito"] = random.choice(("queimadura", "veneno", "lentidao", "fraqueza"))
                            projetil["duracao_efeito"] = 4500 if tipo == "trapper" else 3500
                        projeteis_inimigos.append(projetil)
            elif tipo == "summoner":
                if 0 < dist < 260:
                    r.x += int((ix - px) / dist * 1.5 * mult_velocidade)
                    r.y += int((iy - py) / dist * 1.5 * mult_velocidade)
                if (
                    inimigo.get("invocacoes_feitas", 0) < 2
                    and tempo_atual - inimigo.get("ultima_invocacao", 0) > 5000 / mult_velocidade
                ):
                    inimigo["ultima_invocacao"] = tempo_atual
                    inimigo["invocacoes_feitas"] = inimigo.get("invocacoes_feitas", 0) + 1
                    servo_hp = int(22 * dificuldade["multiplicador_hp_inimigo"])
                    sala.inimigos.append({
                        "tipo": "melee",
                        "nome": "Servo Invocado",
                        "rect": pygame.Rect(r.centerx + random.randint(-35, 35), r.centery + random.randint(-35, 35), 22, 22),
                        "hp": servo_hp,
                        "hp_max": servo_hp,
                        "dano_contato": arredondar_para_5(7 * dificuldade["multiplicador_dano_inimigo"]),
                        "chance_critico": 0.05,
                        "invocado": True,
                    })
                    particulas.criar_texto_dano(r.centerx, r.y - 10, "INVOCAR!", CIANO)
                    if audio_manager:
                        audio_manager.tocar_som("invocacao")
            elif tipo == 'support':
                aliados = [e for e in sala.inimigos if e.get('tipo') != 'support' and e != inimigo]
                if aliados:
                    dx_player = ix - px
                    dy_player = iy - py
                    dist_p = math.hypot(dx_player, dy_player)
                    if dist_p > 0:
                        r.x += int((dx_player / dist_p) * 2.2 * mult_velocidade)
                        r.y += int((dy_player / dist_p) * 2.2 * mult_velocidade)

                    ultima_cura = inimigo.get('ultima_cura', 0)
                    if tempo_atual - ultima_cura > 3000 / mult_velocidade:
                        inimigo['ultima_cura'] = tempo_atual
                        alvo_aliado = min(aliados, key=lambda a: math.hypot(a['rect'].centerx - ix, a['rect'].centery - iy))
                        if alvo_aliado['hp'] < alvo_aliado['hp_max']:
                            cura_val = 25
                            alvo_aliado['hp'] = min(alvo_aliado['hp_max'], alvo_aliado['hp'] + cura_val)
                            alvo_aliado["escudo"] = min(
                                alvo_aliado["hp_max"] * 0.3,
                                alvo_aliado.get("escudo", 0) + cura_val * 0.5,
                            )
                            particulas.criar_texto_dano(alvo_aliado['rect'].centerx, alvo_aliado['rect'].y - 10, f"+{cura_val} HP", VERDE)
                elif 0 < dist < 300:
                    r.x += int((ix - px) / dist * 2 * mult_velocidade)
                    r.y += int((iy - py) / dist * 2 * mult_velocidade)

            if tipo != "bomber" and any(r.colliderect(alvo.rect) for alvo in jogadores_ativos):
                dano_t = arredondar_para_5(inimigo.get('dano_contato', 20 if tipo == 'mimico' else 15))
                efeito_contato = (
                    "veneno" if inimigo.get("modificador_elite") == "toxina"
                    else random.choice(("sangramento", "fraqueza")) if tipo in ("melee", "mimico", "assassin")
                    else random.choice(("exaustao", "cegueira", "corrosao")) if tipo in ("mage", "summoner")
                    else random.choice(("atordoamento", "maldicao", "vulnerabilidade")) if tipo == "boss"
                    else None
                )
                for alvo_indice, alvo in enumerate(jogadores_ativos):
                    if not r.colliderect(alvo.rect):
                        continue
                    gestor = gestores_status[alvo_indice] if alvo_indice < len(gestores_status) else status_manager
                    recebeu_dano = aplicar_dano_player(
                        alvo, particulas, dano_t, tempo_atual, gestor,
                        inimigo.get("chance_critico", 0.08), efeito_contato, 3500, audio_manager,
                    )
                    if recebeu_dano and inimigo.get("modificador_elite") == "vampirico":
                        cura_elite = max(5, arredondar_para_5(inimigo["hp_max"] * 0.04))
                        inimigo["hp"] = min(inimigo["hp_max"], inimigo["hp"] + cura_elite)

            if inimigo['hp'] <= 0:
                if isinstance(estatisticas_run, dict):
                    estatisticas_run["mobs_mortos"] = estatisticas_run.get("mobs_mortos", 0) + 1
                    registrar_abate(estatisticas_run, inimigo)
                if isinstance(estatisticas_run, dict):
                    estatisticas_run["desafio_diario"] = registrar_abate_diario()
                for aliado in jogadores_ativos:
                    registrar_abate_reliquias(aliado)

                if tipo == 'boss':
                    registrar_progresso(carregar_dados(), "chefes")
                    if inimigo.get("secreto") and isinstance(estatisticas_run, dict):
                        estatisticas_run["chefes_secretos_derrotados"] = (
                            estatisticas_run.get("chefes_secretos_derrotados", 0) + 1
                        )
                    if isinstance(estatisticas_run, dict):
                        gemas_contrato = concluir_contrato(estatisticas_run)
                        if gemas_contrato and particulas:
                            particulas.criar_texto_dano(
                                player.rect.centerx, player.rect.y - 30,
                                f"{gemas_contrato} {t('gemas', CONFIG_JOGO.get('idioma', 'PT'))} · {t('contrato_completo', CONFIG_JOGO.get('idioma', 'PT'))}",
                                CIANO, True,
                            )
                    mult_drop = dificuldade['multiplicador_drop_ouro']
                    sala.moedas_no_chao.append({
                        'rect': pygame.Rect(r.centerx, r.centery, 16, 16),
                        'tipo': 'gema_ciano',
                        'valor': obter_gemas_chefe(getattr(sala, "andar", 1)),
                    })
                    sala.boss_derrotado = True
                    sala.limpa = True
                else:
                    mult_drop = dificuldade['multiplicador_drop_ouro']
                    if random.random() < mult_drop:
                        ouro_drop = max(5, arredondar_para_5(random.randint(3, 7) * mult_drop))
                        sala.moedas_no_chao.append({'rect': pygame.Rect(r.centerx, r.centery, 12, 12), 'tipo': 'ouro', 'valor': ouro_drop})
                    if inimigo.get("elite"):
                        sala.moedas_no_chao.append({
                            "rect": pygame.Rect(r.centerx, r.centery, 14, 14),
                            "tipo": "gema_ciano",
                            "valor": inimigo.get("gemas_elite", 5),
                        })
                        if isinstance(estatisticas_run, dict):
                            estatisticas_run["elites_derrotados"] = estatisticas_run.get("elites_derrotados", 0) + 1
                    if inimigo.get("raro"):
                        registrar_progresso(carregar_dados(), "raros")
                        itens_raros = [
                            item for item in TODAS_ARMAS
                            if item.get("raridade") in ("Raro", "Épico", "Lendário")
                        ]
                        if itens_raros:
                            item_raro = dict(random.choice(itens_raros), tipo="equip_arma")
                            sala.moedas_no_chao.append({
                                "rect": pygame.Rect(r.centerx - 8, r.centery - 8, 16, 16),
                                "tipo": "item",
                                "item": item_raro,
                            })
                        if isinstance(estatisticas_run, dict):
                            estatisticas_run["inimigos_raros_derrotados"] = (
                                estatisticas_run.get("inimigos_raros_derrotados", 0) + 1
                            )
                        if random.random() < 0.15:
                            dados_cosmetico = carregar_dados()
                            cosmetico = sortear_cosmetico_bloqueado(dados_cosmetico)
                            if cosmetico and desbloquear_cosmetico(dados_cosmetico, cosmetico):
                                salvar_dados(dados_cosmetico)
                                if particulas:
                                    particulas.criar_texto_dano(
                                        player.rect.centerx, player.rect.y - 35,
                                        f"COSMÉTICO: {COSMETICOS[cosmetico]['nome']['PT']}",
                                        (220, 150, 255), True,
                                    )
                    if random.random() < 0.08 * mult_drop:
                        sala.orbes_cura.append({'rect': pygame.Rect(r.centerx + 10, r.centery, 14, 14), 'cura': 20})
                
                particulas.criar_explosao(r.centerx, r.centery, VERMELHO)
                if audio_manager:
                    audio_manager.tocar_som("morte_inimigo")
                sala.inimigos.remove(inimigo)

    def desenhar_mira_boss(self, tela, sala):
        avisos = pygame.Surface(tela.get_size(), pygame.SRCALPHA)
        for inimigo in sala.inimigos:
            if inimigo.get('tipo') == 'boss':
                r = inimigo['rect']
                if self.boss_em_preparacao:
                    frente = (r.centerx + self.dir_dash_x * 220, r.centery + self.dir_dash_y * 220)
                    normal = (-self.dir_dash_y * 24, self.dir_dash_x * 24)
                    pygame.draw.polygon(avisos, (255, 45, 45, 65), [
                        (r.centerx + normal[0], r.centery + normal[1]),
                        (frente[0] + normal[0], frente[1] + normal[1]),
                        (frente[0] - normal[0], frente[1] - normal[1]),
                        (r.centerx - normal[0], r.centery - normal[1]),
                    ])
                    pygame.draw.line(tela, (255, 80, 80), r.center, frente, 4)
                    pygame.draw.line(
                        tela, (255, 190, 190),
                        (r.centerx - normal[0], r.centery - normal[1]),
                        (r.centerx + normal[0], r.centery + normal[1]), 3,
                    )

                pendente = inimigo.get("ataque_especial_pendente")
                if pendente:
                    ataque = pendente["ataque"]
                    angulo_base = pendente["angulo"]
                    for deslocamento in ataque["angulos"]:
                        angulo = angulo_base + deslocamento
                        fim = (
                            r.centerx + math.cos(angulo) * 250,
                            r.centery + math.sin(angulo) * 250,
                        )
                        pygame.draw.line(avisos, (255, 60, 60, 75), r.center, fim, 20)
                        pygame.draw.line(tela, (255, 85, 85), r.center, fim, 2)
                        pygame.draw.circle(tela, (255, 100, 100), (int(fim[0]), int(fim[1])), 7, 2)
                    restante = max(
                        0,
                        pendente["aviso_ms"] - (pygame.time.get_ticks() - pendente["inicio"]),
                    )
                    largura = 72
                    fundo = pygame.Rect(r.centerx - largura // 2, r.top - 17, largura, 6)
                    pygame.draw.rect(tela, (70, 25, 25), fundo, border_radius=3)
                    pygame.draw.rect(
                        tela, (255, 70, 70),
                        (fundo.x, fundo.y, int(largura * restante / pendente["aviso_ms"]), fundo.height),
                        border_radius=3,
                    )
        
        if self.boss_em_aoe:
            bx, by = self.pos_alvo_aoe
            aoe_rect = pygame.Rect(0, 0, *self.tamanho_aoe)
            aoe_rect.center = (bx, by)
            progresso = (pygame.time.get_ticks() - self.tempo_inicio_aoe) / 1000
            pulso = int(45 + 35 * (0.5 + 0.5 * math.sin(progresso * math.pi * 8)))
            pygame.draw.rect(avisos, (255, 35, 35, pulso), aoe_rect, border_radius=12)
            pygame.draw.rect(tela, (255, 55, 55), aoe_rect, 4, border_radius=12)
            pygame.draw.rect(tela, (255, 190, 190), aoe_rect.inflate(-12, -12), 2, border_radius=9)
            pygame.draw.circle(tela, (255, 100, 100), (bx, by), 8, 2)
            largura_barra = aoe_rect.width
            fundo = pygame.Rect(bx - largura_barra // 2, aoe_rect.bottom + 7, largura_barra, 7)
            pygame.draw.rect(tela, (70, 25, 25), fundo, border_radius=3)
            restante = max(0, 1 - progresso)
            pygame.draw.rect(
                tela, (255, 70, 70),
                (fundo.x, fundo.y, int(largura_barra * restante), fundo.height),
                border_radius=3,
            )
        tela.blit(avisos, (0, 0))