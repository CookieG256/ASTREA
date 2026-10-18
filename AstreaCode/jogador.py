# jogador.py
import pygame
from config import ROXO, CIANO_UI, LARGURA, ALTURA, CONFIG_JOGO, arredondar_para_5, obter_modo_dificuldade
from save import carregar_dados
from banco_itens import TODAS_ARMAS
from personagens import ARMAS_INICIAIS, RACES_AND_CLASSES, stats_selecao
from cosmeticos import COSMETICOS, COSMETICO_PADRAO, obtener_cosmeticos_equipados


def configurar_municao_arma(arma):
    if not arma or arma.get("tipo_arma") != "ranged":
        return
    if "municao_max" not in arma:
        dano = max(1, arma.get("dano", 15))
        arma["municao_max"] = 12 if arma.get("nome") == "Pistola" else max(4, min(16, int(180 / dano)))
    arma.setdefault("municao", arma["municao_max"])
    arma.setdefault("recarga_ms", 1400)
    arma.setdefault("recarregando_ate", 0)


def cadencia_ataque_arma(arma):
    cadencia = arma.get("cadencia", 400)
    if arma.get("tipo_arma") == "mage":
        return max(120, int(cadencia * 0.75))
    return cadencia


def atualizar_municao_arma(arma, tempo_atual):
    if not arma or arma.get("tipo_arma") != "ranged":
        return False
    configurar_municao_arma(arma)
    fim_recarga = arma["recarregando_ate"]
    if arma["municao"] <= 0 and not fim_recarga:
        fim_recarga = tempo_atual + arma["recarga_ms"]
        arma["recarregando_ate"] = fim_recarga
    if fim_recarga and tempo_atual >= fim_recarga:
        arma["municao"] = arma["municao_max"]
        arma["recarregando_ate"] = 0
        return False
    return bool(fim_recarga)


def dash_invulneravel(jogador, tempo_atual):
    return (
        jogador.em_dash
        or tempo_atual < getattr(jogador, "dash_invulneravel_ate", 0)
    )


def custo_mana_ataque(arma):
    return 4 if arma and arma.get("tipo_arma") == "mage" else 0


class Jogador:
    def __init__(self, x, y, bonus_hp=0, bonus_mana=0, numero_jogador=1):
        upgrades = carregar_dados().get("upgrades_nivel", {})
        if not isinstance(upgrades, dict):
            upgrades = {}
        nivel = lambda chave: max(0, int(upgrades.get(chave, 0)))
        bonus_dificuldade = {
            "EASY": (0, 0.0, 0.0, 0.0, 0.0),
            "NORMAL": (20, 0.08, 0.03, 0.02, 0.2),
            "HARD": (45, 0.16, 0.06, 0.04, 0.35),
            "HARDCORE": (75, 0.25, 0.10, 0.06, 0.5),
        }.get(obter_modo_dificuldade(), (0, 0.0, 0.0, 0.0, 0.0))
        hp_dificuldade, dano_dificuldade, defesa_dificuldade, crit_dificuldade, velocidade_dificuldade = bonus_dificuldade
        self.bonus_dano_percent = nivel("dano") * 0.05 + dano_dificuldade
        self.chance_crit = min(0.5, 0.05 + nivel("crit") * 0.01 + crit_dificuldade)
        self.mult_crit = 1.5 + nivel("dano_crit") * 0.05
        self.defesa_percent = min(0.7, nivel("defesa") * 0.02 + defesa_dificuldade)
        self.imortal = False
        self.tempo_imortal = 0
        self.em_dash = False
        self.rect = pygame.Rect(x, y, 30, 30)
        self.vel_base = 5 + nivel("velocidade") * 0.15 + velocidade_dificuldade
        self.hp_max = 200 + bonus_hp + nivel("hp_max") * 10 + hp_dificuldade
        self.hp = self.hp_max
        self.mana_max = 100 + bonus_mana + nivel("mana_max") * 10
        self.mana = self.mana_max
        self.multiplicador_dano_recebido = 1.0
        self.buffs_run = {"dano": 0.0, "vida": 0, "velocidade": 0.0, "defesa": 0.0}
        self.pet_tipo = None
        self.pet_bonus_dano = 0.0
        self.pet_hp_bonus = 0
        self.pet_mana_bonus = 0
        self.pet_bonus_ouro = 0.0
        self.pet_bonus_defesa = 0.0
        self.pet_bonus_critico = 0.0
        self.pet_bonus_velocidade = 0
        self.ouro = 0
        self.chance_esquiva = min(0.5, 0.05 + nivel("esquiva") * 0.01)
        self.bonus_ouro_permanente = nivel("drop_ouro") * 0.05
        self.movendo = False
        self.slots_inventario = []
        
        self.em_dash = False
        self.tempo_inicio_dash = 0
        self.cooldown_dash = max(400, 1000 - nivel("menos_cd") * 100)
        self.ultimo_dash = 0
        self.duracao_dash = 140
        self.dash_invulneravel_ate = 0
        self.esquivou_tempo = 0
        self.dir_dash_x = 0
        self.dir_dash_y = 0

        self.buff_velocidade_ativo = False
        
        self.equipado_capacete = None
        self.equipado_peitoral = None
        self.equipado_calca = None
        self.numero_jogador = numero_jogador
        self.multiplicador_raca_classe = 1.0
        self.multiplicador_gemas = 1.0
        self.multiplicador_dano_cosmetico = 1.0
        self.equipado_arma = {'nome': 'Pistola', 'tipo_arma': 'ranged', 'dano': 10, 'cadencia': 400, 'raridade': 'Comum', 'municao_max': 16, 'municao': 16, 'recarga_ms': 1200}
        self.classe = CONFIG_JOGO.get("classe_jogador", "VANGUARDA")
        if self.classe == "ARCANISTA":
            self.mana_max += 50
            self.mana = self.mana_max
            self.bonus_dano_percent += 0.10
            self.vel_base = max(1, self.vel_base - 0.5)
        elif self.classe == "RASTREADOR":
            self.hp_max = max(1, self.hp_max - 20)
            self.hp = self.hp_max
            self.vel_base += 0.8
            self.chance_crit = min(0.6, self.chance_crit + 0.08)
        elif self.classe in ("VANGUARDA", "ARCANISTA", "RASTREADOR"):
            self.classe = "VANGUARDA"
            self.hp_max += 50
            self.hp = self.hp_max
            self.defesa_percent = min(0.7, self.defesa_percent + 0.08)
            self.bonus_dano_percent -= 0.05
        elif self.classe in RACES_AND_CLASSES["classes"]:
            multiplicadores = stats_selecao(
                CONFIG_JOGO.get("raca_jogador", "Humano"), self.classe
            )
            self.hp_max = max(1, int(round(self.hp_max * multiplicadores["hp_max"])))
            self.hp = self.hp_max
            self.vel_base *= multiplicadores["velocidade"]
            self.cooldown_dash = max(
                250, int(self.cooldown_dash * multiplicadores["dash_cooldown"])
            )
            self.multiplicador_raca_classe = multiplicadores["dano_multiplier"]
            self.multiplicador_gemas = multiplicadores["gem_multiplier"]
        else:
            self.classe = "Guerreiro"
            multiplicadores = stats_selecao(
                CONFIG_JOGO.get("raca_jogador", "Humano"), self.classe
            )
            self.hp_max = max(1, int(round(self.hp_max * multiplicadores["hp_max"])))
            self.hp = self.hp_max
            self.vel_base *= multiplicadores["velocidade"]
            self.cooldown_dash = max(250, int(self.cooldown_dash * multiplicadores["dash_cooldown"]))
            self.multiplicador_raca_classe = multiplicadores["dano_multiplier"]
            self.multiplicador_gemas = multiplicadores["gem_multiplier"]
        equipados = obtener_cosmeticos_equipados(carregar_dados())
        cosmetico_id = equipados["P2" if numero_jogador == 2 else "P1"]
        self.cosmetico = cosmetico_id if cosmetico_id in COSMETICOS else COSMETICO_PADRAO
        bonus_cosmetico = COSMETICOS[self.cosmetico]["bonus"]
        if "hp_max" in bonus_cosmetico:
            self.hp_max = max(1, int(round(self.hp_max * bonus_cosmetico["hp_max"])))
            self.hp = self.hp_max
        self.multiplicador_gemas *= bonus_cosmetico.get("multiplicador_gemas", 1.0)
        self.multiplicador_dano_cosmetico = bonus_cosmetico.get(
            "multiplicador_dano_cosmetico", 1.0
        )
        if "dash_cooldown" in bonus_cosmetico:
            self.cooldown_dash = max(
                250, int(self.cooldown_dash * bonus_cosmetico["dash_cooldown"])
            )
        nome_arma_inicial = ARMAS_INICIAIS.get(self.classe)
        if nome_arma_inicial:
            arma_inicial = next(
                (arma for arma in TODAS_ARMAS if arma["nome"] == nome_arma_inicial),
                None,
            )
            if arma_inicial:
                self.equipado_arma = dict(arma_inicial, tipo="equip_arma")
                configurar_municao_arma(self.equipado_arma)
        modificadores_run = CONFIG_JOGO.get("modificadores_run", [])
        self.multiplicador_recompensas = (
            (1.5 if "vidro" in modificadores_run else 1.0)
            * (1.3 if "horda" in modificadores_run else 1.0)
        )
        self.multiplicador_dano_recebido_run = (
            1.5 if "vidro" in CONFIG_JOGO.get("modificadores_run", []) else 1.0
        )
        self.dano_recebido_total = 0
        self.evento_bioma_ativo = None
        self.mochila_itens = []
        self.fragmentos_run = 0
        self.amuletos_equipados = []
        self.ultimo_dano_recebido = 0
        self.em_run = False
        
        # Controle de Ataque Melee
        self.atacando_melee = False
        self.tempo_inicio_melee = 0
        self.duracao_melee = 150
        self.angulo_olhando = 0

    def configurar_pet(self, tipo):
        hp_atual = self.hp
        mana_atual = self.mana
        self.hp_max -= self.pet_hp_bonus
        self.mana_max -= self.pet_mana_bonus
        self.bonus_dano_percent -= self.pet_bonus_dano
        self.defesa_percent = max(0.0, self.defesa_percent - self.pet_bonus_defesa)
        self.chance_crit -= self.pet_bonus_critico
        self.vel_base -= self.pet_bonus_velocidade
        self.pet_hp_bonus = 80 if tipo == "dragao" else 40 if tipo == "tartaruga" else 0
        self.pet_mana_bonus = 60 if tipo == "guardiao_astral" else 20 if tipo == "corvo" else 0
        self.pet_bonus_dano = 0.20 if tipo == "dragao" else 0.10 if tipo == "lobo" else 0
        self.pet_bonus_ouro = 0.15 if tipo == "robo" else 0
        self.pet_bonus_defesa = 0.18 if tipo == "guardiao_astral" else 0.10 if tipo == "besouro" else 0
        self.pet_bonus_critico = 0.05 if tipo == "serpente" else 0
        self.pet_bonus_velocidade = 1 if tipo == "lince" else 0
        self.hp_max += self.pet_hp_bonus
        self.mana_max += self.pet_mana_bonus
        self.bonus_dano_percent += self.pet_bonus_dano
        self.defesa_percent += self.pet_bonus_defesa
        self.chance_crit += self.pet_bonus_critico
        self.vel_base += self.pet_bonus_velocidade
        self.hp = min(self.hp_max, hp_atual + max(0, self.pet_hp_bonus))
        self.mana = min(self.mana_max, mana_atual + max(0, self.pet_mana_bonus))
        self.pet_tipo = tipo

    def ganhar_ouro(self, quantidade):
        bonus = getattr(self, "pet_bonus_ouro", 0.0) + self.bonus_ouro_permanente
        mult_recompensa = getattr(self, "multiplicador_recompensas", 1.0)
        self.ouro += max(0, arredondar_para_5(quantidade * (1.0 + bonus) * mult_recompensa))

    def executar_dash(self, teclas, tempo_atual, controles=None):
        if tempo_atual - self.ultimo_dash > self.cooldown_dash and not self.em_dash:
            dx, dy = 0, 0
            if isinstance(teclas, dict):
                if teclas.get("esquerda"): dx -= 1
                if teclas.get("direita"): dx += 1
                if teclas.get("cima"): dy -= 1
                if teclas.get("baixo"): dy += 1
            else:
                controles = controles or {}
                esquerda = teclas[controles.get("esquerda", pygame.K_a)] or (
                    not controles and teclas[pygame.K_LEFT]
                )
                direita = teclas[controles.get("direita", pygame.K_d)] or (
                    not controles and teclas[pygame.K_RIGHT]
                )
                cima = teclas[controles.get("cima", pygame.K_w)] or (
                    not controles and teclas[pygame.K_UP]
                )
                baixo = teclas[controles.get("baixo", pygame.K_s)] or (
                    not controles and teclas[pygame.K_DOWN]
                )
                if esquerda: dx -= 1
                if direita: dx += 1
                if cima: dy -= 1
                if baixo: dy += 1

            if dx != 0 or dy != 0:
                self.dir_dash_x = dx
                self.dir_dash_y = dy
            else:
                self.dir_dash_x = 0
                self.dir_dash_y = -1

            self.em_dash = True
            self.tempo_inicio_dash = tempo_atual
            self.ultimo_dash = tempo_atual
            self.dash_invulneravel_ate = tempo_atual + self.duracao_dash + 1000

    def mover(self, teclas, tempo_atual, multiplicador_velocidade=1.0, controles=None):
        controles = controles or {}
        def pressionada(acao, padrao):
            chave = controles.get(acao, padrao)
            if isinstance(teclas, dict):
                return teclas.get(acao, False)
            if controles:
                return teclas[chave]
            alternativas = {
                "esquerda": (pygame.K_a, pygame.K_LEFT),
                "direita": (pygame.K_d, pygame.K_RIGHT),
                "cima": (pygame.K_w, pygame.K_UP),
                "baixo": (pygame.K_s, pygame.K_DOWN),
            }.get(acao, (padrao,))
            return any(teclas[codigo] for codigo in alternativas)

        self.movendo = False
        
        if self.em_dash:
            if tempo_atual - self.tempo_inicio_dash > self.duracao_dash:
                self.em_dash = False

        if self.em_dash:
            vel_dash = 10
            self.rect.x += self.dir_dash_x * vel_dash
            self.rect.y += self.dir_dash_y * vel_dash
        else:
            vel_atual = self.vel_base * (1.5 if self.buff_velocidade_ativo else 1.0) * multiplicador_velocidade
            if pressionada("esquerda", pygame.K_a):
                self.rect.x -= vel_atual
                self.movendo = True
                self.angulo_olhando = 180
            if pressionada("direita", pygame.K_d):
                self.rect.x += vel_atual
                self.movendo = True
                self.angulo_olhando = 0
            if pressionada("cima", pygame.K_w):
                self.rect.y -= vel_atual
                self.movendo = True
                self.angulo_olhando = 90
            if pressionada("baixo", pygame.K_s):
                self.rect.y += vel_atual
                self.movendo = True
                self.angulo_olhando = 270

        self.rect.clamp_ip(pygame.Rect(80, 80, LARGURA - 160, ALTURA - 160))

    def desenhar(self, tela):
        cor_cosmetico = COSMETICOS.get(self.cosmetico, COSMETICOS[COSMETICO_PADRAO])["cor"]
        cor_base = ROXO if self.numero_jogador == 1 else (40, 190, 185)
        cor = tuple(min(255, int((base + efeito) / 2)) for base, efeito in zip(cor_base, cor_cosmetico))
        if self.em_dash:
            cor = tuple(min(255, canal + 35) for canal in cor)
        pygame.draw.circle(tela, cor_cosmetico, self.rect.center, self.rect.width, 2)
        pygame.draw.rect(tela, cor, self.rect)