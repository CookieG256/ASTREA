# sala.py
import random
import pygame
import math
from config import LARGURA, ALTURA, VERMELHO, AMARELO, BRANCO, CINZA, CINZA_CLARO, VERDE, ROXO, CIANO, DOURADO_UI, RARIDADE_CORES, CONFIG_JOGO, FONTE_SYS, FONTE_GRANDE, VERMELHO_ESCURO, LARANJA, BIOMAS_INIMIGOS, obter_multiplicadores_andar, arredondar_para_5
from save import carregar_dados, salvar_dados
from banco_itens import TODAS_ARMAS, TODOS_AMULETOS, SETS_ARMADURAS, registrar_item_no_index
from idiomas import t, nome_inimigo_localizado, nome_chefe_localizado, nome_bioma_localizado
from pixel_assets import sprite_inimigo
from encantamentos import aplicar_forja, custo_encantamento, custo_forja, sortear_encantamento
from reliquias import conceder_reliquia
from narrativa import NPCS, resgatar_npc, npc_para_reencontro, registrar_reencontro
from narrativa import nivel_reputacao
from cosmeticos import desbloquear_cosmetico, sortear_cosmetico_bloqueado
from missoes import registrar_progresso
from modificadores import calcular_efeitos_modificadores


def preco_redondo(valor, minimo=10):
    valor = max(0, int(valor))
    return max(minimo, ((valor + 5) // 10) * 10)


class Sala:
    def __init__(self, x, y, tipo="DESCONHECIDO", bioma_id=1, andar=1):
        self.grid_x = x
        self.grid_y = y
        self.tipo = tipo
        self.bioma_id = bioma_id
        self.andar = andar
        self.revelada = False
        self.vizinhos = {}
        salas_sem_combate = {
            "INICIAL", "CURA", "LOJA", "FERREIRO", "FORJA", "MAGIA",
            "CASSINO", "SACRIFICIO", "RECOMPENSA", "CHEFE", "MIMICO", "EVENTO", "RELIQUIA",
            "BIBLIOTECA", "SANTUARIO", "FONTE", "PORTAL", "EXCLUSIVA_BIOMA",
            "RESGATE", "NPC_ENCONTRO", "REVIVER_P2", "TREINO_CHEFE",
        }
        self.limpa = tipo in salas_sem_combate
        self.inimigos = []
        self.moedas_no_chao = []
        self.orbes_cura = []
        self.baus = []
        self.bau_resolvido = False
        self.boss_derrotado = False
        self.boss_ativo = False
        self.segredo_chefe_disponivel = False
        self.exclusiva_variante = random.randrange(3)
        
        self.fase_chefe = 0  
        self.cassino_cliq = 0
        self.cassino_msg = "Faça sua aposta e torne-se rico! Cada tenta é só 30 Gold! 25% de chance de ganhar o TRIPLO!!!)"
        self.sacrificio_feito = False
        self.evento_resolvido = False
        self.sala_resolvida = False
        self.reliquia_resolvida = False
        self.npc_id = None
        self.sem_dano = True
        self.dano_inicio_sala = 0
        self.recompensa_sem_dano_concedida = False
        self.estatisticas_registradas = False
        self.boss_treino_id = None
        self.boss_derrota_registrada = False
        self.enigma_resposta = 2
        self.enigma_resolvido = False
        self.ofertas_ferreiro = []
        self.ferreiro_comprados = []

        self.itens_ofertados = []
        self.loja_comprados = []

        self.total_ondas = random.randint(3, 5) if tipo not in (
            "INICIAL", "CURA", "LOJA", "FERREIRO", "FORJA", "MAGIA",
            "CASSINO", "SACRIFICIO", "RECOMPENSA", "CHEFE", "BAU", "MIMICO", "EVENTO", "RELIQUIA",
            "BIBLIOTECA", "SANTUARIO", "FONTE", "PORTAL", "EXCLUSIVA_BIOMA",
            "RESGATE", "NPC_ENCONTRO", "REVIVER_P2", "TREINO_CHEFE", "ENIGMA",
        ) else 0
        self.onda_atual = 0
        self.ordem_tipos_inimigos = list(BIOMAS_INIMIGOS.get(bioma_id, BIOMAS_INIMIGOS[1]))
        random.shuffle(self.ordem_tipos_inimigos)
        self.indice_tipo_inimigo = 0

    def revelar(self):
        self.revelada = True
        if self.tipo == "RESGATE" and self.npc_id is None:
            resgatados = carregar_dados().get("npcs_resgatados", [])
            disponiveis = [npc for npc in NPCS if npc not in resgatados]
            self.npc_id = random.choice(disponiveis) if disponiveis else None
        elif self.tipo == "NPC_ENCONTRO" and self.npc_id is None:
            self.npc_id = npc_para_reencontro()
        if self.tipo == "TREINO_CHEFE":
            chefes = carregar_dados().get("chefes_derrotados", [])
            if chefes:
                self.boss_treino_id = random.choice(chefes)
                self.bioma_id = int(self.boss_treino_id)
                self.limpa = False
        if self.tipo == "LOJA" and not self.itens_ofertados:
            armas = [dict(item, tipo="equip_arma") for item in TODAS_ARMAS]
            amuletos = [dict(item, tipo="equip_amulet") for item in TODOS_AMULETOS]
            armaduras = []
            for conjunto, dados in SETS_ARMADURAS.items():
                for parte, tipo_peca in (
                    ("Capacete", "equip_capacete"),
                    ("Peitoral", "equip_peitoral"),
                    ("Calça", "equip_calca"),
                ):
                    armaduras.append({
                        "nome": f"{parte} {conjunto}",
                        "tipo": tipo_peca,
                        "raridade": dados["raridade"],
                        "valor_hp": max(5, int(dados["hp"] / 3)),
                        "valor_def": max(1, int(dados["def"] / 3)),
                        "desc": dados["set_completo"],
                    })
            garantidos = [
                random.choice(armas),
                random.choice(amuletos),
                random.choice(armaduras),
            ]
            todos = armas + amuletos + armaduras
            restantes = [item for item in todos if item not in garantidos]
            escolhidos = garantidos + random.sample(restantes, k=min(2, len(restantes)))
            for item in escolhidos:
                item["custo"] = preco_redondo(
                    item.get("dano", item.get("valor", item.get("valor_hp", 10))) * 5
                )
            self.itens_ofertados = escolhidos

            self.loja_comprados = [False] * len(self.itens_ofertados)
        elif self.tipo in ("RECOMPENSA", "MIMICO") and not self.baus and not self.bau_resolvido:
            self.baus = [
                {
                    "rect": pygame.Rect(LARGURA // 2 - 170 + indice * 340, ALTURA // 2, 60, 52),
                    "conteudo": self._sortear_recompensa(),
                }
                for indice in range(2)
            ]
        elif self.tipo == "FERREIRO" and not self.ofertas_ferreiro:
            self.ofertas_ferreiro = self._sortear_ofertas_ferreiro()
            self.ferreiro_comprados = [False] * len(self.ofertas_ferreiro)
        elif self.tipo == "CACADA" and not self.inimigos and not self.sala_resolvida:
            dificuldade = obter_multiplicadores_andar(self.andar)
            hp = arredondar_para_5(170 * dificuldade["multiplicador_hp_inimigo"])
            self.inimigos.append({
                "tipo": "assassin",
                "nome": t("sala_cacada_inimigo", CONFIG_JOGO.get("idioma", "PT")),
                "tipo_inimigo": "assassin",
                "bioma_id": self.bioma_id,
                "rect": pygame.Rect(LARGURA // 2 - 17, ALTURA // 2 - 17, 34, 34),
                "hp": hp,
                "hp_max": hp,
                "dano_contato": arredondar_para_5(18 * dificuldade["multiplicador_dano_inimigo"]),
                "chance_critico": 0.16,
                "elite": True,
                "modificador_elite": random.choice(("frenetico", "toxina")),
                "multiplicador_velocidade": 1.4,
                "gemas_elite": max(10, preco_redondo(10 + self.andar)),
            })
            self.limpa = False

    def _sortear_ofertas_ferreiro(self):
        armas = [item.copy() for item in TODAS_ARMAS]
        for item in armas:
            item["tipo"] = "equip_arma"
        amuletos = [dict(item, tipo="equip_amulet") for item in TODOS_AMULETOS]
        armaduras = []
        for conjunto, dados in SETS_ARMADURAS.items():
            for parte, tipo in (
                ("Capacete", "equip_capacete"),
                ("Peitoral", "equip_peitoral"),
                ("Calça", "equip_calca"),
            ):
                armaduras.append({
                    "nome": f"{parte} {conjunto}",
                    "tipo": tipo,
                    "raridade": dados["raridade"],
                    "valor_hp": max(5, int(dados["hp"] / 3)),
                    "valor_def": max(1, int(dados["def"] / 3)),
                    "desc": f"+{int(dados['hp'] / 3)} HP e +{int(dados['def'] / 3)} defesa.",
                })
        disponiveis = armas + amuletos + armaduras
        nivel = nivel_reputacao("ferreiro")
        raridade_peso = {"Comum": 0, "Incomum": 1, "Raro": 2, "Épico": 3, "Lendário": 4, "Mítico": 5}
        disponiveis.sort(
            key=lambda item: raridade_peso.get(item.get("raridade", "Comum"), 0)
            * nivel + random.random()
        )
        ofertas = []
        for item in reversed(disponiveis):
            item["custo"] = preco_redondo(
                item.get("dano", item.get("valor", item.get("valor_hp", 10)))
                * 5 * max(0.65, 1 - nivel * 0.05), 50
            )
            ofertas.append(item)
            if len(ofertas) == 5:
                break
        return ofertas

    def _sortear_recompensa(self):
        modo = CONFIG_JOGO.get("modo_dificuldade", "EASY")
        chance_arma = {"EASY": 0.22, "CASUAL": 0.22, "NORMAL": 0.32, "HARD": 0.45, "DIFICIL": 0.45, "HARDCORE": 0.58}.get(modo, 0.22)
        tipo = random.choices(
            ("ouro", "cura", "arma", "buff_dano", "buff_vida", "buff_velocidade", "buff_defesa", "buff_mana", "reliquia"),
            weights=((1.0 - chance_arma) * 0.30, (1.0 - chance_arma) * 0.25, chance_arma, 0.08, 0.07, 0.04, 0.04, 0.05, 0.10),
            k=1,
        )[0]
        if tipo == "ouro":
            mult_drop = obter_multiplicadores_andar(self.andar)["multiplicador_drop_ouro"]
            return {"tipo": tipo, "valor": preco_redondo(random.randint(80, 160) * mult_drop)}
        if tipo == "cura":
            return {"tipo": tipo, "valor": 0.35}
        if tipo.startswith("buff_"):
            valores = {
                "buff_dano": 0.12,
                "buff_vida": 40,
                "buff_velocidade": 0.8,
                "buff_defesa": 0.08,
                "buff_mana": 30,
            }
            return {"tipo": tipo, "valor": valores[tipo]}
        if tipo == "reliquia":
            return {"tipo": tipo, "nome": random.choice(("berserker", "vitalidade", "arcana"))}

        pesos_raridade = {
            "EASY": (65, 30, 5),
            "CASUAL": (65, 30, 5),
            "NORMAL": (50, 38, 12),
            "HARD": (35, 45, 20),
            "DIFICIL": (35, 45, 20),
            "HARDCORE": (20, 45, 35),
        }.get(modo, (65, 30, 5))
        raridade = random.choices(("Épico", "Lendário", "Mítico"), weights=pesos_raridade, k=1)[0]
        arma = random.choice([item for item in TODAS_ARMAS if item.get("raridade") == raridade]).copy()
        arma["tipo"] = "equip_arma"
        return {"tipo": "arma", "item": arma}

    def interagir_bau(self, indice, player, particulas=None, idioma="PT"):
        if indice < 0 or indice >= len(self.baus):
            return False

        if self.tipo == "MIMICO":
            if self.inimigos or self.bau_resolvido:
                return False
            dificuldade = obter_multiplicadores_andar(self.andar)
            hp = int(100 * dificuldade["multiplicador_hp_inimigo"])
            self.inimigos.append({
                "tipo": "mimico",
                "nome": t("bau_mimico", idioma),
                "rect": self.baus[indice]["rect"].copy(),
                "hp": hp,
                "hp_max": hp,
                "dano_contato": arredondar_para_5(22 * dificuldade["multiplicador_dano_inimigo"]),
                "chance_critico": 0.15,
                "bioma_id": self.bioma_id,
                "mimico_agressivo": True,
            })
            self.baus.clear()
            self.bau_resolvido = True
            self.limpa = False
            if particulas:
                particulas.criar_texto_dano(player.rect.centerx, player.rect.y - 18, t("bau_mimico_revelado", idioma), VERMELHO)
            return True

        bau = self.baus[indice]
        recompensa = bau["conteudo"]
        if recompensa["tipo"] == "arma" and len(player.mochila_itens) >= 9:
            if particulas:
                particulas.criar_texto_dano(player.rect.centerx, player.rect.y - 18, t("mochila_cheia", idioma), AMARELO)
            return False
        if recompensa["tipo"] == "ouro":
            player.ganhar_ouro(recompensa["valor"])
            mensagem = f"+{recompensa['valor']} {t('ouro', idioma)}"
            cor = AMARELO
        elif recompensa["tipo"] == "cura":
            cura = max(5, arredondar_para_5(player.hp_max * recompensa["valor"]))
            player.hp = min(player.hp_max, player.hp + cura)
            mensagem = f"+{cura} HP"
            cor = VERDE
        elif recompensa["tipo"].startswith("buff_"):
            buffs = getattr(player, "buffs_run", None)
            if buffs is None:
                player.buffs_run = {}
                buffs = player.buffs_run
            chave = recompensa["tipo"].replace("buff_", "")
            buffs[chave] = buffs.get(chave, 0) + recompensa["valor"]
            if chave == "vida":
                player.hp_max += int(recompensa["valor"])
                player.hp = min(player.hp_max, player.hp + int(recompensa["valor"]))
            elif chave == "mana":
                player.mana_max += int(recompensa["valor"])
                player.mana = min(player.mana_max, player.mana + int(recompensa["valor"]))
            mensagem = t("recompensa_" + recompensa["tipo"], idioma)
            cor = CIANO
        elif recompensa["tipo"] == "reliquia":
            self._aplicar_reliquia(player, recompensa["nome"])
            mensagem = t("reliquia_" + recompensa["nome"], idioma)
            cor = ROXO
        else:
            player.mochila_itens.append(recompensa["item"])
            registrar_item_no_index(recompensa["item"]["nome"])
            mensagem = recompensa["item"]["nome"]
            cor = RARIDADE_CORES.get(recompensa["item"]["raridade"], BRANCO)

        self.baus.clear()
        self.bau_resolvido = True
        self.limpa = True
        if particulas:
            particulas.criar_texto_dano(player.rect.centerx, player.rect.y - 18, mensagem, cor)
        return True

    @staticmethod
    def _aplicar_reliquia(player, nome):
        conceder_reliquia(player, nome)
        if nome == "berserker":
            player.buffs_run["dano"] = player.buffs_run.get("dano", 0) + 0.20
            player.buffs_run["defesa"] = player.buffs_run.get("defesa", 0) - 0.10
        elif nome == "vitalidade":
            player.hp_max += 50
            player.hp = min(player.hp_max, player.hp + 50)
            player.buffs_run["velocidade"] = player.buffs_run.get("velocidade", 0) - 0.5
        else:
            player.mana_max += 30
            player.mana = min(player.mana_max, player.mana + 30)
            player.buffs_run["dano"] = player.buffs_run.get("dano", 0) - 0.08

    def spawnar_boss_direto(self, secreto=False):
        self.inimigos.clear()
        dificuldade = obter_multiplicadores_andar(self.andar)
        efeitos_modificadores = calcular_efeitos_modificadores(
            CONFIG_JOGO.get("modificadores_run", [])
        )
        bioma_boss = 15 if secreto else self.bioma_id
        hp_boss = arredondar_para_5(
            1100
            * dificuldade['multiplicador_hp_inimigo']
            * efeitos_modificadores["vida_inimigos"]
            * (2 if secreto else 1)
        )
        self.inimigos.append({
            'tipo': 'boss',
            'rect': pygame.Rect(LARGURA//2 - 40, ALTURA//2 - 40, 80, 80),
            'hp': hp_boss,
            'hp_max': hp_boss,
            'dano_contato': arredondar_para_5(
                34
                * dificuldade['multiplicador_dano_inimigo']
                * efeitos_modificadores["dano_inimigos"]
            ),
            'multiplicador_velocidade': efeitos_modificadores["velocidade_inimigos"],
            'eh_boss': True,
            'nome': t("chefe_secreto_nome", CONFIG_JOGO.get("idioma", "PT")) if secreto else nome_chefe_localizado(self.bioma_id, CONFIG_JOGO.get("idioma", "PT")),
            'rage_ativado': False,
            'bioma_id': bioma_boss,
            'secreto': secreto,
            'fases_total': 3 if secreto else {3: 2, 6: 2, 8: 3, 10: 3, 11: 2, 12: 2, 13: 2, 14: 2, 15: 3}.get(self.bioma_id, 1),
            'fase_atual': 1,
            'fase_transicao_fim': 0,
            'ultimo_ataque_especial': 0,
            'padrao_ataque': bioma_boss,
            'ultimo_ataque_aviso': "",
            'efeito_especial': ("queimadura", "veneno", "atordoamento", "lentidao", "veneno", "fraqueza", "lentidao", "queimadura", "fraqueza", "queimadura", "queimadura", "vulnerabilidade", "fraqueza", "atordoamento", "maldicao")[max(0, min(14, bioma_boss - 1))],
        })
        self.boss_ativo = True
        self.fase_chefe = 1
        self.limpa = False

    def spawnar_proxima_onda(self):
        if self.limpa: return
        if len(self.inimigos) > 0: return

        if self.tipo in ("CHEFE", "TREINO_CHEFE"):
            self.spawnar_boss_direto()
        elif self.tipo == "MIMICO":
            self.limpa = True
        else:
            if self.onda_atual < self.total_ondas:
                self.onda_atual += 1
                qtd_mobs = random.randint(3, 5)
                dificuldade = obter_multiplicadores_andar(self.andar)
                efeitos_modificadores = calcular_efeitos_modificadores(
                    CONFIG_JOGO.get("modificadores_run", [])
                )
                qtd_mobs = max(
                    qtd_mobs,
                    round(qtd_mobs * efeitos_modificadores["quantidade_inimigos"]),
                )
                mult_hp = (
                    dificuldade['multiplicador_hp_inimigo']
                    * efeitos_modificadores["vida_inimigos"]
                )
                mult_dano = (
                    dificuldade['multiplicador_dano_inimigo']
                    * efeitos_modificadores["dano_inimigos"]
                )
                
                for _ in range(qtd_mobs):
                    rx = random.randint(150, LARGURA - 150)
                    ry = random.randint(150, ALTURA - 150)
                    tipo_mob = self.ordem_tipos_inimigos[
                        self.indice_tipo_inimigo % len(self.ordem_tipos_inimigos)
                    ]
                    self.indice_tipo_inimigo += 1
                    perfis = {
                        "melee": (40, 10, 25),
                        "tank": (100, 25, 38),
                        "ranged": (30, 10, 25),
                        "support": (35, 10, 28),
                        "mage": (38, 13, 27),
                        "summoner": (55, 8, 30),
                        "assassin": (32, 12, 24),
                        "bomber": (45, 20, 28),
                        "trapper": (36, 11, 26),
                        "duelist": (48, 15, 27),
                    }
                    hp_base, dano_base, tamanho = perfis[tipo_mob]
                    hp = arredondar_para_5(hp_base * mult_hp)
                    inimigo = {
                        "tipo": tipo_mob,
                        "nome": nome_inimigo_localizado(tipo_mob, self.bioma_id, CONFIG_JOGO.get("idioma", "PT")),
                        "tipo_inimigo": tipo_mob,
                        "bioma_id": self.bioma_id,
                        "rect": pygame.Rect(rx, ry, tamanho, tamanho),
                        "hp": arredondar_para_5(hp),
                        "hp_max": arredondar_para_5(hp),
                        "dano_contato": arredondar_para_5(dano_base * mult_dano),
                        "multiplicador_velocidade": efeitos_modificadores["velocidade_inimigos"],
                        "chance_critico": 0.08,
                    }
                    chance_elite = min(0.16, 0.05 + self.andar * 0.005)
                    if random.random() < min(
                        0.75,
                        chance_elite * efeitos_modificadores["chance_elite"],
                    ):
                        modificador = random.choice(("blindado", "frenetico", "vampirico", "toxina"))
                        inimigo.update({
                            "elite": True,
                            "modificador_elite": modificador,
                            "multiplicador_velocidade": max(
                                efeitos_modificadores["velocidade_inimigos"],
                                1.35 if modificador == "frenetico" else 1.0,
                            ),
                            "gemas_elite": max(
                                5,
                                arredondar_para_5(
                                    (5 + self.andar) * efeitos_modificadores["gemas_elite"]
                                ),
                            ),
                            "hp": arredondar_para_5(hp * (1.8 if modificador == "blindado" else 1.5)),
                        })
                        inimigo["hp_max"] = inimigo["hp"]
                        inimigo["dano_contato"] = arredondar_para_5(
                            inimigo["dano_contato"] * (1.35 if modificador in ("frenetico", "vampirico") else 1.2)
                        )
                    if random.random() < 0.035:
                        inimigo["raro"] = True
                        inimigo["hp"] = arredondar_para_5(inimigo["hp"] * 2.0)
                        inimigo["hp_max"] = inimigo["hp"]
                        inimigo["dano_contato"] = arredondar_para_5(
                            inimigo["dano_contato"] * 1.4
                        )
                        inimigo["multiplicador_velocidade"] = max(
                            inimigo.get("multiplicador_velocidade", 1.0), 1.2
                        )
                    if tipo_mob in ("ranged", "mage", "trapper"):
                        inimigo["ultimo_tiro"] = 0
                    elif tipo_mob == "support":
                        inimigo["ultima_cura"] = 0
                    elif tipo_mob == "summoner":
                        inimigo["ultima_invocacao"] = 0
                        inimigo["invocacoes_feitas"] = 0
                    elif tipo_mob == "assassin":
                        inimigo["proxima_investida"] = 0
                    elif tipo_mob == "duelist":
                        inimigo["proxima_investida"] = 0
                    elif tipo_mob == "bomber":
                        inimigo["dano_explosao"] = arredondar_para_5(dano_base * 1.5 * mult_dano)
                        inimigo["raio_explosao"] = 95
                    self.inimigos.append(inimigo)
            else:
                self.limpa = True

    @staticmethod
    def _desenhar_titulo_sala(tela, texto, cor):
        titulo = FONTE_GRANDE.render(texto, True, cor)
        tela.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 100))

    def desenhar_conteudo_especial(self, tela, player, evento_tecla, particulas=None, status_manager=None, player2=None):
        if self.tipo == "LOJA":
            if not self.itens_ofertados:
                self.itens_ofertados = random.sample(TODAS_ARMAS, min(5, len(TODAS_ARMAS)))
                self.loja_comprados = [False] * len(self.itens_ofertados)

            idioma = CONFIG_JOGO.get("idioma", "PT")
            txt_t = FONTE_GRANDE.render(t("loja", idioma), True, AMARELO)
            tela.blit(txt_t, (LARGURA//2 - txt_t.get_width()//2, 80))
            
            y_pos = 160
            for i, item in enumerate(self.itens_ofertados):
                comprado = self.loja_comprados[i]
                txt_status = "[ESGOTADO]" if comprado else f"[Custo: ${item['custo']}]"
                equipamento = {
                    "equip_arma": t("equipamento_arma", idioma),
                    "equip_amulet": t("equipamento_amulet", idioma),
                    "equip_capacete": t("equipamento_capacete", idioma),
                    "equip_peitoral": t("equipamento_peitoral", idioma),
                    "equip_calca": t("equipamento_calca", idioma),
                }.get(item["tipo"], t("equipamento_item", idioma))
                cor_txt = CINZA_CLARO if comprado else RARIDADE_CORES.get(item.get('raridade', 'Comum'), BRANCO)
                txt_item = FONTE_SYS.render(
                    f"[{i+1}] {item['nome']} · {equipamento} · {item.get('raridade','Comum')} · {txt_status}",
                    True, cor_txt,
                )
                tela.blit(txt_item, (LARGURA//2 - txt_item.get_width()//2, y_pos))
                y_pos += 45

            if evento_tecla and evento_tecla.unicode.isdigit():
                tecla_num = int(evento_tecla.unicode) - 1
                if 0 <= tecla_num < len(self.itens_ofertados) and not self.loja_comprados[tecla_num]:
                    item = self.itens_ofertados[tecla_num]
                    if player.ouro >= item['custo']:
                        if item['tipo'] == 'cura':
                            player.ouro -= item['custo']
                            self.loja_comprados[tecla_num] = True
                            cura = max(5, arredondar_para_5(item['valor']))
                            player.hp = min(player.hp_max, player.hp + cura)
                            if particulas: particulas.criar_texto_dano(player.rect.centerx, player.rect.y - 15, f"+{cura} HP", VERDE)
                        elif len(player.mochila_itens) < 9:
                            player.ouro -= item['custo']
                            self.loja_comprados[tecla_num] = True
                            player.mochila_itens.append(item)
                            registrar_item_no_index(item["nome"])

        elif self.tipo == "FERREIRO":
            idioma = CONFIG_JOGO.get("idioma", "PT")
            self._desenhar_titulo_sala(tela, t("sala_ferreiro", idioma), AMARELO)
            for i, item in enumerate(self.ofertas_ferreiro):
                comprado = self.ferreiro_comprados[i]
                status = t("esgotado", idioma) if comprado else f"{item['custo']} {t('ouro', idioma)}"
                equipamento = {
                    "equip_arma": t("equipamento_arma", idioma),
                    "equip_amulet": t("equipamento_amulet", idioma),
                    "equip_capacete": t("equipamento_capacete", idioma),
                    "equip_peitoral": t("equipamento_peitoral", idioma),
                    "equip_calca": t("equipamento_calca", idioma),
                }.get(item["tipo"], t("equipamento_item", idioma))
                texto = f"[{i + 1}] {item['nome']} · {equipamento} · {item['raridade']} · {status}"
                linha = FONTE_SYS.render(texto, True, CINZA_CLARO if comprado else RARIDADE_CORES.get(item["raridade"], BRANCO))
                tela.blit(linha, (LARGURA // 2 - linha.get_width() // 2, 175 + i * 48))
            if evento_tecla and evento_tecla.unicode.isdigit():
                indice = int(evento_tecla.unicode) - 1
                if 0 <= indice < len(self.ofertas_ferreiro) and not self.ferreiro_comprados[indice]:
                    item = self.ofertas_ferreiro[indice]
                    if player.ouro >= item["custo"] and len(player.mochila_itens) < 9:
                        player.ouro -= item["custo"]
                        player.mochila_itens.append(item.copy())
                        self.ferreiro_comprados[indice] = True
                        registrar_item_no_index(item["nome"])
                    elif particulas:
                        particulas.criar_texto_dano(player.rect.centerx, player.rect.y - 15, t("mochila_cheia", idioma), AMARELO)

        elif self.tipo == "FORJA":
            idioma = CONFIG_JOGO.get("idioma", "PT")
            self._desenhar_titulo_sala(tela, t("sala_forja", idioma), CIANO)
            arma = player.equipado_arma
            if arma:
                nivel = int(arma.get("nivel_forja", 0))
                preco = custo_forja(arma)
                linhas = (
                    f"{arma['nome']}  +{nivel}/5",
                    t("forja_bonus", idioma),
                    f"[1] {t('forja_melhorar', idioma)} · {preco} {t('ouro', idioma)}"
                    if nivel < 5 else t("forja_maximo", idioma),
                    f"[2] {t('forja_criar_arma', idioma)} · 3 {t('fragmentos', idioma)} ({getattr(player, 'fragmentos_run', 0)})",
                )
                for i, texto in enumerate(linhas):
                    cor = BRANCO if i < 2 else DOURADO_UI if nivel < 5 else CINZA_CLARO
                    linha = FONTE_SYS.render(texto, True, cor)
                    tela.blit(linha, (LARGURA // 2 - linha.get_width() // 2, 175 + i * 42))
                if evento_tecla and evento_tecla.key == pygame.K_1 and nivel < 5 and player.ouro >= preco:
                    if aplicar_forja(arma):
                        player.ouro -= preco
                        if particulas:
                            particulas.criar_texto_dano(player.rect.centerx, player.rect.y - 15, t("forja_sucesso", idioma), CIANO)
                elif (
                    evento_tecla and evento_tecla.key == pygame.K_2
                    and getattr(player, "fragmentos_run", 0) >= 3
                    and len(player.mochila_itens) < 9
                ):
                    armas_craft = [
                        item for item in TODAS_ARMAS
                        if item.get("raridade") in ("Raro", "Épico", "Lendário")
                    ]
                    arma_craft = dict(random.choice(armas_craft), tipo="equip_arma")
                    player.fragmentos_run -= 3
                    player.mochila_itens.append(arma_craft)
                    registrar_item_no_index(arma_craft["nome"])
                    registrar_progresso(carregar_dados(), "craft")
                    if particulas:
                        particulas.criar_texto_dano(
                            player.rect.centerx, player.rect.y - 15,
                            t("forja_sucesso", idioma), CIANO,
                        )
            else:
                texto = FONTE_SYS.render(t("forja_sem_arma", idioma), True, CINZA_CLARO)
                tela.blit(texto, (LARGURA // 2 - texto.get_width() // 2, 220))

        elif self.tipo == "MAGIA":
            idioma = CONFIG_JOGO.get("idioma", "PT")
            self._desenhar_titulo_sala(tela, t("sala_magia", idioma), ROXO)
            arma = player.equipado_arma
            if arma:
                encantamentos = arma.setdefault("encantamentos", [])
                preco = custo_encantamento(arma)
                texto_arma = FONTE_SYS.render(arma["nome"], True, BRANCO)
                tela.blit(texto_arma, (LARGURA // 2 - texto_arma.get_width() // 2, 175))
                if encantamentos:
                    resumo = " · ".join(f"{e['nome']} ({e['raridade']})" for e in encantamentos[-2:])
                    linha = FONTE_SYS.render(resumo, True, DOURADO_UI)
                    tela.blit(linha, (LARGURA // 2 - linha.get_width() // 2, 215))
                if len(encantamentos) < 3:
                    texto = FONTE_SYS.render(f"[1] {t('encantar_arma', idioma)} · {preco} {t('ouro', idioma)}", True, CIANO)
                    tela.blit(texto, (LARGURA // 2 - texto.get_width() // 2, 270))
                    if evento_tecla and evento_tecla.key == pygame.K_1 and player.ouro >= preco:
                        encantamento = sortear_encantamento()
                        encantamentos.append(encantamento)
                        player.ouro -= preco
                        if particulas:
                            particulas.criar_texto_dano(player.rect.centerx, player.rect.y - 15, f"{encantamento['raridade']}: {encantamento['nome']}", RARIDADE_CORES[encantamento["raridade"]])
                else:
                    texto = FONTE_SYS.render(t("encantamento_limite", idioma), True, CINZA_CLARO)
                    tela.blit(texto, (LARGURA // 2 - texto.get_width() // 2, 270))
            else:
                texto = FONTE_SYS.render(t("forja_sem_arma", idioma), True, CINZA_CLARO)
                tela.blit(texto, (LARGURA // 2 - texto.get_width() // 2, 220))

        elif self.tipo in ("RECOMPENSA", "MIMICO"):
            idioma = CONFIG_JOGO.get("idioma", "PT")
            txt_t = FONTE_GRANDE.render(t("sala_recompensa", idioma), True, AMARELO)
            tela.blit(txt_t, (LARGURA//2 - txt_t.get_width()//2, 80))

            for indice, bau in enumerate(self.baus):
                cor_bau = (139, 69, 19)
                pygame.draw.rect(tela, cor_bau, bau['rect'], border_radius=4)
                pygame.draw.rect(tela, AMARELO, bau['rect'], 2, border_radius=4)
                recompensa = bau["conteudo"]
                if recompensa["tipo"] == "ouro":
                    texto_conteudo = f"{t('bau_ouro', idioma)}: {recompensa['valor']}"
                elif recompensa["tipo"] == "cura":
                    texto_conteudo = t("bau_cura", idioma)
                elif recompensa["tipo"].startswith("buff_"):
                    texto_conteudo = t("recompensa_" + recompensa["tipo"], idioma)
                elif recompensa["tipo"] == "reliquia":
                    texto_conteudo = t("reliquia_" + recompensa["nome"], idioma)
                else:
                    item = recompensa["item"]
                    texto_conteudo = f"{item['nome']} ({t('raridade_' + item['raridade'].lower(), idioma)})"
                texto = _render_texto_quebrado(texto_conteudo, 230)
                for linha_indice, linha in enumerate(texto):
                    tela.blit(linha, (bau["rect"].centerx - linha.get_width() // 2, bau["rect"].y - 39 + linha_indice * 16))
                dica = FONTE_SYS.render(f"[{indice + 1}] / [E]", True, AMARELO)
                tela.blit(dica, (bau["rect"].centerx - dica.get_width() // 2, bau["rect"].bottom + 6))

        elif self.tipo == "RESGATE":
            idioma = CONFIG_JOGO.get("idioma", "PT")
            self._desenhar_titulo_sala(tela, t("npc_resgate_titulo", idioma), CIANO)
            npc = NPCS.get(self.npc_id)
            if not npc:
                linha = FONTE_SYS.render(t("evento_concluido", idioma), True, CINZA_CLARO)
                tela.blit(linha, (LARGURA // 2 - linha.get_width() // 2, 210))
                return
            detalhes = (
                f"{npc['simbolo']}  {npc['nome']}",
                f"[1] {t('npc_resgatar', idioma)}",
                f"[2] {t('npc_deixar', idioma)}",
            )
            for indice, texto in enumerate(detalhes):
                linha = FONTE_SYS.render(texto, True, BRANCO if indice else DOURADO_UI)
                tela.blit(linha, (LARGURA // 2 - linha.get_width() // 2, 180 + indice * 44))
            if evento_tecla and evento_tecla.key in (pygame.K_1, pygame.K_2):
                if evento_tecla.key == pygame.K_1:
                    resgatar_npc(self.npc_id)
                self.sala_resolvida = True
                self.limpa = True

        elif self.tipo == "NPC_ENCONTRO":
            idioma = CONFIG_JOGO.get("idioma", "PT")
            npc = NPCS.get(self.npc_id)
            if not npc:
                self.sala_resolvida = True
                return
            self._desenhar_titulo_sala(tela, t("npc_reencontro", idioma), DOURADO_UI)
            nome = FONTE_SYS.render(npc["nome"], True, CIANO)
            tela.blit(nome, (LARGURA // 2 - nome.get_width() // 2, 170))
            reputacao = nivel_reputacao(self.npc_id)
            reputacao_txt = FONTE_SYS.render(
                f"{t('npc_reputacao', idioma)}: {reputacao}/5", True, DOURADO_UI
            )
            tela.blit(reputacao_txt, (LARGURA // 2 - reputacao_txt.get_width() // 2, 202))
            for indice, chave in enumerate(("npc_recompensa", "npc_sem_recompensa")):
                linha = FONTE_SYS.render(f"[{indice + 1}] {t(chave, idioma)}", True, BRANCO)
                tela.blit(linha, (LARGURA // 2 - linha.get_width() // 2, 246 + indice * 48))
            if evento_tecla and evento_tecla.key in (pygame.K_1, pygame.K_2):
                registrar_reencontro(self.npc_id)
                if evento_tecla.key == pygame.K_1:
                    novo_nivel = nivel_reputacao(self.npc_id)
                    player.ganhar_ouro(preco_redondo(80 + self.andar * 5 + novo_nivel * 30))
                    player.hp = min(
                        player.hp_max,
                        player.hp + arredondar_para_5(player.hp_max * (0.25 + novo_nivel * 0.02)),
                    )
                self.sala_resolvida = True
                self.limpa = True

        elif self.tipo == "ENIGMA":
            idioma = CONFIG_JOGO.get("idioma", "PT")
            self._desenhar_titulo_sala(tela, t("enigma_titulo", idioma), DOURADO_UI)
            linhas = (
                t("enigma_pergunta", idioma),
                f"[1] {t('enigma_opcao_1', idioma)}",
                f"[2] {t('enigma_opcao_2', idioma)}",
                f"[3] {t('enigma_opcao_3', idioma)}",
            )
            if self.enigma_resolvido:
                linhas = (t("enigma_concluido", idioma),)
            for indice, texto in enumerate(linhas):
                linha = FONTE_SYS.render(texto, True, BRANCO if indice else CIANO)
                tela.blit(linha, (LARGURA // 2 - linha.get_width() // 2, 170 + indice * 45))
            if evento_tecla and evento_tecla.unicode in ("1", "2", "3") and not self.enigma_resolvido:
                if int(evento_tecla.unicode) == self.enigma_resposta:
                    self.enigma_resolvido = True
                    self.sala_resolvida = True
                    self.limpa = True
                    dados = carregar_dados()
                    cosmetico = sortear_cosmetico_bloqueado(dados)
                    if cosmetico:
                        desbloquear_cosmetico(dados, cosmetico)
                    else:
                        dados["gemas"] = int(dados.get("gemas", 0)) + 100
                    salvar_dados(dados)
                    registrar_progresso(dados, "enigmas")
                    conceder_reliquia(player, "arcana")
                    if particulas:
                        premio = t("enigma_recompensa" if cosmetico else "enigma_recompensa_gemas", idioma)
                        particulas.criar_texto_dano(
                            player.rect.centerx, player.rect.y - 25, premio, DOURADO_UI, True
                        )
                elif particulas:
                    particulas.criar_texto_dano(
                        player.rect.centerx, player.rect.y - 20,
                        t("enigma_tente_novamente", idioma), VERMELHO,
                    )

        elif self.tipo == "REVIVER_P2":
            idioma = CONFIG_JOGO.get("idioma", "PT")
            self._desenhar_titulo_sala(tela, t("sala_reviver", idioma), CIANO)
            if self.sala_resolvida:
                texto = FONTE_SYS.render(t("evento_concluido", idioma), True, CINZA_CLARO)
                tela.blit(texto, (LARGURA // 2 - texto.get_width() // 2, 205))
                return
            chave_texto = "reviver_p2" if player2 is not None and player2.hp <= 0 else "reviver_sem_jogador"
            texto = FONTE_SYS.render(t(chave_texto, idioma), True, BRANCO)
            tela.blit(texto, (LARGURA // 2 - texto.get_width() // 2, 190))
            if evento_tecla and evento_tecla.key in (pygame.K_1, pygame.K_e):
                if player2 is None or player2.hp > 0:
                    return
                if player.ouro < 100:
                    aviso = FONTE_SYS.render(t("reviver_sem_ouro", idioma), True, VERMELHO)
                    tela.blit(aviso, (LARGURA // 2 - aviso.get_width() // 2, 230))
                    return
                player.ouro -= 100
                player2.hp = max(1, arredondar_para_5(player2.hp_max * 0.5))
                player2.rect.center = (player.rect.centerx + 45, player.rect.centery)
                player2.em_run = True
                self.sala_resolvida = True

        elif self.tipo == "EVENTO":
            idioma = CONFIG_JOGO.get("idioma", "PT")
            titulo_evento = (
                f"{t('evento_titulo', idioma)} · "
                f"{nome_bioma_localizado(self.bioma_id, idioma)}"
            )
            titulo = FONTE_GRANDE.render(titulo_evento, True, ROXO)
            tela.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 100))
            textos = (
                t("evento_opcao_1", idioma),
                t("evento_opcao_2", idioma),
                t("evento_opcao_3", idioma),
            ) if not self.evento_resolvido else (t("evento_concluido", idioma),)
            for indice, texto in enumerate(textos):
                linha = FONTE_SYS.render(texto, True, BRANCO if not self.evento_resolvido else CINZA_CLARO)
                tela.blit(linha, (LARGURA // 2 - linha.get_width() // 2, 190 + indice * 48))
            if evento_tecla and not self.evento_resolvido:
                if evento_tecla.key == pygame.K_1 and player.hp > 35:
                    player.hp -= 30
                    fim_evento = pygame.time.get_ticks() + 20000
                    bonus_dano = (0.15, 0.20, 0.25)[self.bioma_id % 3]
                    risco_dano = (0.10, 0.15, 0.20)[(self.bioma_id + 1) % 3]
                    for alvo in (player, player2):
                        if alvo and alvo.hp > 0:
                            alvo.evento_bioma_ativo = {
                                "fim": fim_evento, "dano": bonus_dano,
                                "dano_recebido": risco_dano,
                            }
                    self.evento_resolvido = True
                elif evento_tecla.key == pygame.K_2:
                    player.ganhar_ouro(60)
                    fim_evento = pygame.time.get_ticks() + 20000
                    bonus_velocidade = (0.15, 0.20, 0.25)[(self.bioma_id + 1) % 3]
                    for alvo in (player, player2):
                        if alvo and alvo.hp > 0:
                            alvo.evento_bioma_ativo = {
                                "fim": fim_evento, "velocidade": bonus_velocidade,
                                "dano": -0.1,
                            }
                    self.evento_resolvido = True
                elif evento_tecla.key == pygame.K_3:
                    self.evento_resolvido = True
                if self.evento_resolvido:
                    self.limpa = True

        elif self.tipo == "RELIQUIA":
            idioma = CONFIG_JOGO.get("idioma", "PT")
            titulo = FONTE_GRANDE.render(t("reliquia_titulo", idioma), True, ROXO)
            tela.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 100))
            texto = t("reliquia_oferta", idioma) if not self.reliquia_resolvida else t("evento_concluido", idioma)
            linha = FONTE_SYS.render(texto, True, BRANCO)
            tela.blit(linha, (LARGURA // 2 - linha.get_width() // 2, 180))
            if not self.reliquia_resolvida:
                for indice, chave in enumerate(("reliquia_berserker", "reliquia_vitalidade", "reliquia_arcana")):
                    linha = FONTE_SYS.render(f"[{indice + 1}] {t(chave, idioma)}", True, CIANO)
                    tela.blit(linha, (LARGURA // 2 - linha.get_width() // 2, 225 + indice * 42))
                if evento_tecla and evento_tecla.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                    escolha = ("berserker", "vitalidade", "arcana")[evento_tecla.key - pygame.K_1]
                    self._aplicar_reliquia(player, escolha)
                    self.reliquia_resolvida = True
                    self.limpa = True

        elif self.tipo == "EXCLUSIVA_BIOMA":
            idioma = CONFIG_JOGO.get("idioma", "PT")
            variantes = ("santuario", "prova", "eco")
            variante = variantes[self.exclusiva_variante]
            titulo = f"{nome_bioma_localizado(self.bioma_id, idioma)} · {t('sala_exclusiva_' + variante, idioma)}"
            self._desenhar_titulo_sala(tela, titulo, CIANO)
            if self.sala_resolvida:
                texto = FONTE_SYS.render(t("evento_concluido", idioma), True, CINZA_CLARO)
                tela.blit(texto, (LARGURA // 2 - texto.get_width() // 2, 205))
                return
            for indice in range(2):
                chave = f"sala_exclusiva_{variante}_{indice + 1}"
                linha = FONTE_SYS.render(f"[{indice + 1}] {t(chave, idioma)}", True, BRANCO)
                tela.blit(linha, (LARGURA // 2 - linha.get_width() // 2, 190 + indice * 48))
            if not evento_tecla or evento_tecla.key not in (pygame.K_1, pygame.K_2):
                return
            if self.exclusiva_variante == 0:
                if evento_tecla.key == pygame.K_1:
                    player.hp = min(player.hp_max, player.hp + arredondar_para_5(player.hp_max * 0.30))
                else:
                    player.buffs_run["dano"] = player.buffs_run.get("dano", 0) + 0.12
            elif self.exclusiva_variante == 1:
                if evento_tecla.key == pygame.K_1:
                    player.mana = min(player.mana_max, player.mana + arredondar_para_5(player.mana_max * 0.5))
                else:
                    player.buffs_run["defesa"] = player.buffs_run.get("defesa", 0) + 0.10
            elif evento_tecla.key == pygame.K_1:
                player.buffs_run["velocidade"] = player.buffs_run.get("velocidade", 0) + 0.5
            else:
                player.ganhar_ouro(preco_redondo(50 + self.andar * 5))
            self.sala_resolvida = True
            self.limpa = True

        elif self.tipo in ("BIBLIOTECA", "SANTUARIO", "FONTE", "PORTAL"):
            idioma = CONFIG_JOGO.get("idioma", "PT")
            chave_titulo = {
                "BIBLIOTECA": "sala_biblioteca",
                "SANTUARIO": "sala_santuario",
                "FONTE": "sala_fonte",
                "PORTAL": "sala_portal",
            }[self.tipo]
            self._desenhar_titulo_sala(tela, t(chave_titulo, idioma), ROXO)
            if self.sala_resolvida:
                texto = FONTE_SYS.render(t("evento_concluido", idioma), True, CINZA_CLARO)
                tela.blit(texto, (LARGURA // 2 - texto.get_width() // 2, 205))
                return
            opcoes = {
                "BIBLIOTECA": ("biblioteca_opcao_1", "biblioteca_opcao_2"),
                "SANTUARIO": ("santuario_opcao_1", "santuario_opcao_2"),
                "FONTE": ("fonte_opcao_1", "fonte_opcao_2"),
                "PORTAL": ("portal_opcao_1", "portal_opcao_2"),
            }[self.tipo]
            for indice, chave_texto in enumerate(opcoes):
                linha = FONTE_SYS.render(f"[{indice + 1}] {t(chave_texto, idioma)}", True, BRANCO)
                tela.blit(linha, (LARGURA // 2 - linha.get_width() // 2, 180 + indice * 50))
            if not evento_tecla or evento_tecla.key not in (pygame.K_1, pygame.K_2):
                return
            escolha = evento_tecla.key - pygame.K_1
            if self.tipo == "BIBLIOTECA":
                if escolha == 0:
                    player.buffs_run["dano"] = player.buffs_run.get("dano", 0) + 0.15
                    player.buffs_run["defesa"] = player.buffs_run.get("defesa", 0) - 0.05
                else:
                    player.mana_max += 40
                    player.mana = min(player.mana_max, player.mana + 40)
            elif self.tipo == "SANTUARIO":
                if escolha == 0:
                    player.hp = min(player.hp_max, player.hp + arredondar_para_5(player.hp_max * 0.4))
                else:
                    player.buffs_run["defesa"] = player.buffs_run.get("defesa", 0) + 0.12
            elif self.tipo == "FONTE":
                if player.ouro < 50:
                    if particulas:
                        particulas.criar_texto_dano(player.rect.centerx, player.rect.y - 15, t("ouro_insuficiente", idioma), AMARELO)
                    return
                player.ouro -= 50
                if escolha == 0:
                    player.hp = min(player.hp_max, player.hp + arredondar_para_5(player.hp_max * 0.75))
                else:
                    player.mana = min(player.mana_max, player.mana + arredondar_para_5(player.mana_max * 0.75))
            else:
                if len(player.mochila_itens) >= 9:
                    if particulas:
                        particulas.criar_texto_dano(player.rect.centerx, player.rect.y - 15, t("mochila_cheia", idioma), AMARELO)
                    return
                item = random.choice(TODOS_AMULETOS if escolha else [
                    arma for arma in TODAS_ARMAS if arma.get("raridade") in ("Raro", "Épico")
                ]).copy()
                item["tipo"] = "equip_amulet" if escolha else "equip_arma"
                player.mochila_itens.append(item)
                registrar_item_no_index(item["nome"])
            self.sala_resolvida = True
            self.limpa = True

        elif self.tipo == "CACADA":
            idioma = CONFIG_JOGO.get("idioma", "PT")
            self._desenhar_titulo_sala(tela, t("sala_cacada", idioma), VERMELHO)
            texto = FONTE_SYS.render(t("sala_cacada_descricao", idioma), True, BRANCO)
            tela.blit(texto, (LARGURA // 2 - texto.get_width() // 2, 165))
            if not self.inimigos and not self.sala_resolvida:
                self.sala_resolvida = True
                self.limpa = True
                player.ganhar_ouro(preco_redondo(100 + self.andar * 10))
                texto_fim = FONTE_SYS.render(t("sala_cacada_recompensa", idioma), True, DOURADO_UI)
                tela.blit(texto_fim, (LARGURA // 2 - texto_fim.get_width() // 2, 205))

        elif self.tipo == "CASSINO":
            txt_t = FONTE_GRANDE.render("CASSINO", True, ROXO)
            tela.blit(txt_t, (LARGURA//2 - txt_t.get_width()//2, 100))
            
            txt_inst = FONTE_SYS.render("[G] Apostar 30 Gold (25% de chance de ganhar)", True, BRANCO)
            txt_res = FONTE_SYS.render(self.cassino_msg, True, AMARELO if "GANHOU" in self.cassino_msg else VERMELHO if "PERDEU" in self.cassino_msg else BRANCO)
            
            tela.blit(txt_inst, (LARGURA//2 - txt_inst.get_width()//2, 170))
            tela.blit(txt_res, (LARGURA//2 - txt_res.get_width()//2, 230))

            if evento_tecla and evento_tecla.key == pygame.K_g:
                if player.ouro >= 30:
                    player.ouro -= 30
                    self.cassino_cliq += 1
                    if random.random() < 0.25:  # 25% de chance de ganhar
                        player.ganhar_ouro(90)
                        self.cassino_msg = "VOCÊ GANHOU +90 DE OURO!"
                    else:
                        self.cassino_msg = "VOCÊ PERDEU!"
                else:
                    self.cassino_msg = "OURO INSUFICIENTE!"

        elif self.tipo == "SACRIFICIO":
            txt_t = FONTE_GRANDE.render("ALTAR DE SACRIFÍCIO", True, VERMELHO)
            tela.blit(txt_t, (LARGURA//2 - txt_t.get_width()//2, 100))
            
            if not self.sacrificio_feito:
                txt_1 = FONTE_SYS.render("[1] -15 HP Max por +50 Gold", True, BRANCO)
                txt_2 = FONTE_SYS.render("[2] -25 HP Max por +8 Dano Arma", True, BRANCO)
                txt_3 = FONTE_SYS.render("[3] -30 HP Max por +15% Mana Max", True, BRANCO)
                txt_4 = FONTE_SYS.render("[4] -50 HP Max por +200 Gold", True, BRANCO)
                txt_5 = FONTE_SYS.render("[5] -75 HP Max por +25 Dano Arma", True, BRANCO)
                txt_6 = FONTE_SYS.render("[6] IGNORAR", True, CINZA_CLARO)
                
                tela.blit(txt_1, (LARGURA//2 - txt_1.get_width()//2, 170))
                tela.blit(txt_2, (LARGURA//2 - txt_2.get_width()//2, 210))
                tela.blit(txt_3, (LARGURA//2 - txt_3.get_width()//2, 250))
                tela.blit(txt_4, (LARGURA//2 - txt_4.get_width()//2, 290))
                tela.blit(txt_5, (LARGURA//2 - txt_5.get_width()//2, 330))
                tela.blit(txt_6, (LARGURA//2 - txt_6.get_width()//2, 370))

                if evento_tecla:
                    if evento_tecla.key == pygame.K_1 and player.hp_max > 30:
                        player.hp_max -= 15; player.hp = min(player.hp, player.hp_max); player.ganhar_ouro(50); self.sacrificio_feito = True
                    elif evento_tecla.key == pygame.K_2 and player.hp_max > 40:
                        player.hp_max -= 25; player.hp = min(player.hp, player.hp_max)
                        if player.equipado_arma: player.equipado_arma['dano'] += 8
                        self.sacrificio_feito = True
                    elif evento_tecla.key == pygame.K_3 and player.hp_max > 45:
                        player.hp_max -= 30; player.hp = min(player.hp, player.hp_max); player.mana_max += 50; player.mana = min(player.mana_max, player.mana + 50); self.sacrificio_feito = True
                    elif evento_tecla.key == pygame.K_4 and player.hp_max > 50:
                        player.hp_max -= 50; player.hp = min(player.hp, player.hp_max); player.ganhar_ouro(200); self.sacrificio_feito = True
                    elif evento_tecla.key == pygame.K_5 and player.hp_max > 75:
                        player.hp_max -= 75; player.hp = min(player.hp, player.hp_max)
                        if player.equipado_arma: player.equipado_arma['dano'] += 25
                        self.sacrificio_feito = True
                    elif evento_tecla.key == pygame.K_6:
                        self.sacrificio_feito = True
            else:
                txt_feito = FONTE_SYS.render("Altar finalizado. Você pode sair da sala.", True, CINZA_CLARO)
                tela.blit(txt_feito, (LARGURA//2 - txt_feito.get_width()//2, 210))

        elif self.tipo == "TREINO_CHEFE":
            idioma = CONFIG_JOGO.get("idioma", "PT")
            self._desenhar_titulo_sala(tela, t("treino_chefe_titulo", idioma), ROXO)
            texto = FONTE_SYS.render(t("treino_chefe_descricao", idioma), True, CINZA_CLARO)
            tela.blit(texto, (LARGURA // 2 - texto.get_width() // 2, 150))

# --- Certifica-te de que está indentado dentro da classe Sala ---
    def desenhar_inimigos_e_moedas(self, tela, player, particulas=None, estatisticas_run=None, audio_manager=None, players=None):
        jogadores_coleta = [alvo for alvo in (players or [player]) if alvo.hp > 0] or [player]
        for inimigo in self.inimigos:
            if 'x' in inimigo and 'y' in inimigo:
                pos_x, pos_y = int(inimigo['x']), int(inimigo['y'])
            elif 'rect' in inimigo:
                pos_x, pos_y = inimigo['rect'].centerx, inimigo['rect'].centery
            else:
                continue
            pygame.draw.circle(tela, (255, 0, 0), (pos_x, pos_y), 12)
        velocidade_atracao = 12.0 if self.limpa else 4.0
        raio_alcance = 9999 if self.limpa else 70

        for m in self.moedas_no_chao[:]:
            mx, my = m['rect'].center
            coletor = min(jogadores_coleta, key=lambda alvo: math.dist(alvo.rect.center, (mx, my)))
            px, py = coletor.rect.center
            dist = math.hypot(px - mx, py - my)
            
            if dist < raio_alcance and dist > 0:
                m['rect'].x += int((px - mx) / dist * velocidade_atracao)
                m['rect'].y += int((py - my) / dist * velocidade_atracao)

            eh_gema = m.get('tipo') == 'gema_ciano'
            eh_item = m.get("tipo") == "item"
            cor_moeda = (220, 90, 255) if eh_item else CIANO if eh_gema else AMARELO
            raio = 8 if eh_item else 7 if eh_gema else 6
            pygame.draw.circle(tela, cor_moeda, m['rect'].center, raio)
            pygame.draw.circle(tela, (8, 8, 14), m['rect'].center, raio, 2)

            if coletor.rect.colliderect(m['rect']):
                if eh_item:
                    if len(coletor.mochila_itens) >= 9:
                        if particulas:
                            particulas.criar_texto_dano(
                                coletor.rect.centerx, coletor.rect.y - 15,
                                t("mochila_cheia", CONFIG_JOGO.get("idioma", "PT")), AMARELO,
                            )
                        continue
                    item = m["item"]
                    coletor.mochila_itens.append(item.copy())
                    registrar_item_no_index(item["nome"])
                    if particulas:
                        particulas.criar_texto_dano(
                            coletor.rect.centerx, coletor.rect.y - 15, item["nome"], cor_moeda,
                        )
                elif eh_gema:
                    dados = carregar_dados()
                    valor_gemas = arredondar_para_5(
                        m['valor'] * getattr(coletor, "multiplicador_gemas", 1.0)
                        * getattr(coletor, "multiplicador_recompensas", 1.0)
                    )
                    dados['gemas'] = dados.get('gemas', 0) + valor_gemas
                    salvar_dados(dados)
                    if isinstance(estatisticas_run, dict):
                        estatisticas_run["gemas_coletadas"] = (
                            estatisticas_run.get("gemas_coletadas", 0) + valor_gemas
                        )
                    registrar_progresso(dados, "gemas", valor_gemas)
                    if particulas:
                        particulas.criar_texto_dano(coletor.rect.centerx, coletor.rect.y - 15, f"+{valor_gemas} Gemas!", CIANO)
                else:
                    coletor.ganhar_ouro(m['valor'])
                self.moedas_no_chao.remove(m)

        raio_alcance_orbe = 9999 if self.limpa else 80
        for orbe in self.orbes_cura[:]:
            ox, oy = orbe['rect'].center
            coletor = min(jogadores_coleta, key=lambda alvo: math.dist(alvo.rect.center, (ox, oy)))
            px, py = coletor.rect.center
            dist = math.hypot(px - ox, py - oy)

            if dist < raio_alcance_orbe and dist > 0:
                orbe['rect'].x += int((px - ox) / dist * velocidade_atracao)
                orbe['rect'].y += int((py - oy) / dist * velocidade_atracao)

            pygame.draw.circle(tela, VERDE, orbe['rect'].center, 7)
            pygame.draw.circle(tela, BRANCO, orbe['rect'].center, 7, 1)

            if coletor.rect.colliderect(orbe['rect']):
                cura = max(
                    1,
                    arredondar_para_5(
                        orbe['cura'] * getattr(coletor, "multiplicador_cura_orbes_run", 1.0)
                    ),
                )
                coletor.hp = min(coletor.hp_max, coletor.hp + cura)
                if particulas:
                    particulas.criar_texto_dano(
                        coletor.rect.centerx, coletor.rect.y - 15, f"+{cura} HP", VERDE
                    )
                if audio_manager:
                    audio_manager.tocar_som("cura")
                self.orbes_cura.remove(orbe)

        for inimigo in self.inimigos:
            tipo = inimigo.get('tipo', 'melee')
            r = inimigo['rect']
            imagem = sprite_inimigo(inimigo.get("bioma_id", self.bioma_id), tipo, r.size)
            tela.blit(imagem, r)
            if inimigo.get("raro"):
                pygame.draw.rect(tela, (26, 8, 40), r.inflate(8, 8), 4, border_radius=5)
                pygame.draw.rect(tela, (220, 90, 255), r.inflate(5, 5), 2, border_radius=5)
            if tipo == "mimico":
                pygame.draw.rect(tela, (220, 165, 45), r, 2)

            if inimigo.get("nome"):
                idioma = CONFIG_JOGO.get("idioma", "PT")
                if inimigo.get("secreto"):
                    nome = t("chefe_secreto_nome", idioma)
                elif inimigo.get("tipo_inimigo"):
                    nome = nome_inimigo_localizado(inimigo["tipo_inimigo"], inimigo.get("bioma_id", self.bioma_id), idioma)
                elif tipo == "boss":
                    nome = nome_chefe_localizado(inimigo.get("bioma_id", self.bioma_id), idioma)
                elif tipo == "mimico":
                    nome = t("bau_mimico", idioma)
                else:
                    nome = inimigo["nome"]
                if inimigo.get("raro"):
                    nome = f"{t('inimigo_raro', idioma)} · {nome}"
                linhas = _render_texto_quebrado(nome, max(90, r.width + 80))
                if inimigo.get("elite"):
                    pygame.draw.rect(tela, AMARELO, r.inflate(6, 6), 2, border_radius=5)
                    chave_modificador = f"mod_elite_{inimigo.get('modificador_elite', '')}"
                    modificador = t(chave_modificador, idioma)
                    nome = f"{t('inimigo_elite', idioma)} {modificador}: {nome}"
                    linhas = _render_texto_quebrado(nome, max(90, r.width + 100))
                topo_nome = r.y - 8 - len(linhas) * 15
                for linha_indice, linha in enumerate(linhas):
                    tela.blit(linha, (r.centerx - linha.get_width() // 2, topo_nome + linha_indice * 15))

            if tipo != 'boss':
                hp_perc = max(0, inimigo['hp'] / inimigo['hp_max'])
                pygame.draw.rect(tela, VERMELHO, (r.x, r.y - 8, r.width, 4))
                pygame.draw.rect(tela, (0, 255, 0), (r.x, r.y - 8, int(r.width * hp_perc), 4))

def desenhar_minimapa(tela, mapa_salas, sala_atual):
    largura_box, altura_box = 158, 158
    origem_box_x = LARGURA - largura_box - 20
    origem_box_y = 20

    fundo_mapa = pygame.Surface((largura_box, altura_box), pygame.SRCALPHA)
    fundo_mapa.fill((12, 12, 22, 228))
    tela.blit(fundo_mapa, (origem_box_x, origem_box_y))
    pygame.draw.rect(tela, (7, 7, 13), (origem_box_x, origem_box_y, largura_box, altura_box), 3, border_radius=8)
    pygame.draw.rect(tela, (92, 82, 122), (origem_box_x, origem_box_y, largura_box, altura_box), 1, border_radius=8)

    centro_x = origem_box_x + (largura_box // 2) - 9
    centro_y = origem_box_y + (altura_box // 2) - 9
    tam_quad = 18
    espaco = 4

    for (gx, gy), s in mapa_salas.items():
        dif_x = gx - sala_atual.grid_x
        dif_y = gy - sala_atual.grid_y

        px = centro_x + (dif_x * (tam_quad + espaco))
        py = centro_y + (dif_y * (tam_quad + espaco))

        if origem_box_x + 4 <= px <= origem_box_x + largura_box - 20 and origem_box_y + 4 <= py <= origem_box_y + altura_box - 20:
            if s.revelada:
                cor = VERDE if s == sala_atual else CINZA_CLARO
                if s.tipo == "LOJA": cor = AMARELO
                elif s.tipo == "CHEFE": cor = VERMELHO_ESCURO
                elif s.tipo == "CASSINO": cor = ROXO
                elif s.tipo == "SACRIFICIO": cor = VERMELHO
                elif s.tipo == "RECOMPENSA": cor = LARANJA
                elif s.tipo == "MIMICO": cor = LARANJA
                elif s.tipo == "EVENTO": cor = CIANO
                elif s.tipo == "RELIQUIA": cor = ROXO
                elif s.tipo in ("BIBLIOTECA", "PORTAL"): cor = ROXO
                elif s.tipo == "SANTUARIO": cor = VERDE
                elif s.tipo in ("FONTE", "EXCLUSIVA_BIOMA"): cor = CIANO
                elif s.tipo in ("RESGATE", "NPC_ENCONTRO"): cor = CIANO
                elif s.tipo == "REVIVER_P2": cor = ROXO
                elif s.tipo == "CACADA": cor = VERMELHO
                elif s.tipo == "TREINO_CHEFE": cor = ROXO
                elif s.tipo == "ENIGMA": cor = DOURADO_UI
                pygame.draw.rect(tela, cor, (px, py, tam_quad, tam_quad), border_radius=3)
                pygame.draw.rect(tela, (8, 8, 14), (px, py, tam_quad, tam_quad), 2, border_radius=3)
            else:
                pygame.draw.rect(tela, (68, 62, 80), (px, py, tam_quad, tam_quad), border_radius=3)
                pygame.draw.rect(tela, (7, 7, 13), (px, py, tam_quad, tam_quad), 2, border_radius=3)

def todas_salas_exploradas(mapa_salas):
    if not mapa_salas:
        return False
    exploradas = sum(1 for sala in mapa_salas.values() if sala.revelada)
    return exploradas / len(mapa_salas) >= 0.7

def gerar_andar(bioma_id=1, andar=1):
    qtd_salas = random.choice([8, 9, 10])
    salas = {}
    s_ini = Sala(0, 0, "INICIAL", bioma_id, andar)
    s_ini.revelar()
    salas[(0, 0)] = s_ini
    
    lista_pos = [(0, 0)]
    direcoes = [('NORTE', (0, -1)), ('SUL', (0, 1)), ('LESTE', (1, 0)), ('OESTE', (-1, 0))]
    opostos = {'NORTE': 'SUL', 'SUL': 'NORTE', 'LESTE': 'OESTE', 'OESTE': 'LESTE'}

    while len(salas) < qtd_salas:
        px, py = random.choice(lista_pos)
        nome_dir, (dx, dy) = random.choice(direcoes)
        nx, ny = px + dx, py + dy
        if (nx, ny) not in salas:
            nova = Sala(nx, ny, "DESCONHECIDO", bioma_id, andar)
            salas[(nx, ny)] = nova
            lista_pos.append((nx, ny))
            salas[(px, py)].vizinhos[nome_dir] = nova
            nova.vizinhos[opostos[nome_dir]] = salas[(px, py)]

    for pos1, s1 in salas.items():
        for pos2, s2 in salas.items():
            if pos1 != pos2:
                dx = pos2[0] - pos1[0]
                dy = pos2[1] - pos1[1]
                if dx == 1 and dy == 0: s1.vizinhos['LESTE'] = s2
                elif dx == -1 and dy == 0: s1.vizinhos['OESTE'] = s2
                elif dx == 0 and dy == 1: s1.vizinhos['SUL'] = s2
                elif dx == 0 and dy == -1: s1.vizinhos['NORTE'] = s2

    pos_ordenadas = sorted(salas.keys(), key=lambda p: abs(p[0]) + abs(p[1]))
    pos_chefe = pos_ordenadas[-1]
    tipos_disponiveis = [
        "LOJA", "FERREIRO", "FORJA", "MAGIA", "CASSINO", "SACRIFICIO",
        "RECOMPENSA", "MIMICO", "EVENTO", "RELIQUIA", "BIBLIOTECA",
        "SANTUARIO", "FONTE", "PORTAL", "CACADA", "EXCLUSIVA_BIOMA", "ENIGMA",
    ]
    dados_npcs = carregar_dados()
    if dados_npcs.get("chefes_derrotados"):
        tipos_disponiveis.append("TREINO_CHEFE")
    npcs_resgatados = dados_npcs.get("npcs_resgatados", [])
    if len(npcs_resgatados) < len(NPCS) and random.random() < 0.7:
        tipos_disponiveis.append("RESGATE")
    if npc_para_reencontro():
        tipos_disponiveis.append("NPC_ENCONTRO")
    quantidade_especiais = random.randint(2, min(4, len(pos_ordenadas) - 2))
    pos_especiais = random.sample(
        [pos for pos in pos_ordenadas if pos not in ((0, 0), pos_chefe)],
        k=quantidade_especiais,
    )
    tipos_especiais = random.sample(tipos_disponiveis, k=quantidade_especiais)
    if "EXCLUSIVA_BIOMA" not in tipos_especiais and random.random() < 0.55:
        tipos_especiais[-1] = "EXCLUSIVA_BIOMA"
    if len(npcs_resgatados) < len(NPCS) and "RESGATE" not in tipos_especiais:
        tipos_especiais[0] = "RESGATE"
    elif npc_para_reencontro() and "NPC_ENCONTRO" not in tipos_especiais:
        tipos_especiais[0] = "NPC_ENCONTRO"
    if CONFIG_JOGO.get("coop_local") and andar % 5 == 0:
        tipos_especiais[0] = "REVIVER_P2"

    for pos, sala in salas.items():
        sala.bioma_id = bioma_id
        if pos == (0, 0):
            continue
        if pos == pos_chefe:
            sala.tipo = "CHEFE"
            sala.limpa = True
            sala.total_ondas = 0
            sala.segredo_chefe_disponivel = random.random() < 0.35
        elif pos in pos_especiais:
            sala.tipo = tipos_especiais[pos_especiais.index(pos)]
            sala.limpa = sala.tipo not in ("TREINO_CHEFE", "ENIGMA")
            sala.total_ondas = 0
        else:
            sala.tipo = "NORMAL"
            sala.limpa = False
            sala.total_ondas = random.randint(3, 5)

    return s_ini, salas


def _render_texto_quebrado(texto, largura):
    palavras = str(texto).split()
    linhas = []
    atual = ""
    for palavra in palavras:
        candidato = f"{atual} {palavra}".strip()
        if atual and FONTE_SYS.size(candidato)[0] > largura:
            linhas.append(FONTE_SYS.render(atual, True, BRANCO))
            atual = palavra
        else:
            atual = candidato
    if atual:
        linhas.append(FONTE_SYS.render(atual, True, BRANCO))
    return linhas