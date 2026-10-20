import math
import random

import pygame

from config import AMARELO, BRANCO, CIANO_UI, LARANJA, ROXO_UI, VERDE, VERMELHO
from inimigos import aplicar_dano_inimigo


ATAQUE_CARREGADO_MS = 800
ESCUDO_DURACAO_MS = 3000
JANELA_PARRY_MS = 180
COOLDOWN_ESCUDO_MS = 1200

HABILIDADES_MITICAS = {
    "adaga_sombra": {"slots": (3,), "custos": {3: 0}, "cooldowns": {3: 14000}},
    "espada_berserk": {"slots": (3,), "custos": {3: 25}, "cooldowns": {3: 9000}},
    "pistolas_duplas": {"slots": (3,), "custos": {3: 15}, "cooldowns": {3: 7500}},
    "arco_luz": {"slots": (3,), "custos": {3: 25}, "cooldowns": {3: 10000}},
    "cajado_explosao": {
        "slots": (0, 1, 2, 3),
        "custos": {0: 12, 1: 25, 2: 35, 3: 100},
        "cooldowns": {0: 2200, 1: 6000, 2: 9000, 3: 30000},
    },
    "grimorio_infinito": {"slots": (3,), "custos": {3: 55}, "cooldowns": {3: 18000}},
}

NOMES_HABILIDADES = {
    "adaga_sombra": {3: "Arise!"},
    "espada_berserk": {3: "Corte Devastador"},
    "pistolas_duplas": {3: "Showtime"},
    "arco_luz": {3: "Disparo Estelar"},
    "cajado_explosao": {
        0: "Ignition Spark",
        1: "Impact Wave",
        2: "Meteor Strike",
        3: "EXPLOSION!",
    },
    "grimorio_infinito": {3: "Singularidade Roxa"},
}


class ControleCombate:
    def __init__(self):
        self.inicio_ataque = None
        self.ataque_pendente = False
        self.multiplicador_ataque_pendente = 1.0
        self.escudo_ate = 0
        self.escudo_cooldown_ate = 0
        self.janela_parry_ate = 0
        self.ultimo_parry = -10000
        self.ataque_botao_anterior = False

    def iniciar_ataque(self, agora):
        if self.inicio_ataque is None:
            self.inicio_ataque = agora

    def soltar_ataque(self, agora):
        if self.inicio_ataque is None:
            return
        duracao = max(0, agora - self.inicio_ataque)
        self.multiplicador_ataque_pendente = 1.8 if duracao >= ATAQUE_CARREGADO_MS else 1.0
        self.ataque_pendente = True
        self.inicio_ataque = None

    def atualizar_ataque(self, pressionado, agora):
        if pressionado and not self.ataque_botao_anterior:
            self.iniciar_ataque(agora)
        elif not pressionado and self.ataque_botao_anterior:
            self.soltar_ataque(agora)
        self.ataque_botao_anterior = pressionado

    def consumir_ataque(self):
        if not self.ataque_pendente:
            return 0.0
        self.ataque_pendente = False
        multiplicador = self.multiplicador_ataque_pendente
        self.multiplicador_ataque_pendente = 1.0
        return multiplicador

    def ativar_escudo(self, agora):
        if agora < self.escudo_cooldown_ate:
            return False
        self.escudo_ate = agora + ESCUDO_DURACAO_MS
        self.escudo_cooldown_ate = agora + ESCUDO_DURACAO_MS + COOLDOWN_ESCUDO_MS
        self.janela_parry_ate = agora + JANELA_PARRY_MS
        return True

    def escudo_ativo(self, agora):
        return agora < self.escudo_ate

    def defender_dano(self, dano, agora, atacante=None):
        if not self.escudo_ativo(agora):
            return dano, False, False
        if agora <= self.janela_parry_ate and agora - self.ultimo_parry >= 650:
            self.ultimo_parry = agora
            if atacante is not None:
                atacante["parry_atordoado_ate"] = agora + (2200 if atacante.get("tipo") == "boss" else 1300)
                if atacante.get("tipo") == "boss":
                    atacante["parry_crit_bonus"] = 0.35
            return 0, True, True
        return max(0, round(dano * 0.12)), True, False


def arma_mitica_id(arma):
    return (arma or {}).get("mitica_id")


def dano_habilidade(jogador, arma, multiplicador, calcular_dano):
    dano, critico = calcular_dano(arma, jogador, 1.0)
    return max(5, int(dano * multiplicador)), critico


def _atingir_inimigo(inimigo, dano, critico, agora, audio, estatisticas):
    return aplicar_dano_inimigo(inimigo, dano, critico, agora, audio, estatisticas)


def usar_habilidade_mitica(
    jogador, indice, agora, mouse_pos, inimigos, projeteis, particulas, audio,
    estatisticas, calcular_dano,
):
    arma = getattr(jogador, "equipado_arma", None)
    mitica_id = arma_mitica_id(arma)
    dados = HABILIDADES_MITICAS.get(mitica_id)
    if not dados or indice not in dados["slots"]:
        return False

    cooldowns = getattr(jogador, "cooldowns_miticos", None)
    if cooldowns is None:
        cooldowns = {}
        jogador.cooldowns_miticos = cooldowns
    if agora < cooldowns.get(indice, 0):
        if particulas:
            particulas.criar_texto_dano(
                jogador.rect.centerx, jogador.rect.y - 18,
                f"{(cooldowns[indice] - agora) / 1000:.1f}s", CIANO_UI,
            )
        return True
    custo = dados["custos"][indice]
    if jogador.mana < custo:
        if particulas:
            particulas.criar_texto_dano(
                jogador.rect.centerx, jogador.rect.y - 18, "SEM MANA", CIANO_UI,
            )
        return True

    cooldowns[indice] = agora + dados["cooldowns"][indice]
    jogador.mana -= custo
    dano_base, critico_base = dano_habilidade(
        jogador, arma, 1.0, calcular_dano
    )
    centro = jogador.rect.center

    if mitica_id == "adaga_sombra":
        soldados = getattr(jogador, "soldados_sombra", [])
        soldados.extend(
            {"tipo": tipo, "fim": agora + 12000, "proximo_ataque": 0}
            for tipo in ("tank", "curandeiro", "dps")
        )
        jogador.soldados_sombra = soldados[-3:]
        jogador.bonus_dano_sombra_ate = agora + 12000
        if particulas:
            particulas.criar_texto_dano(*centro, "ARISE!", ROXO_UI)
    elif mitica_id == "espada_berserk":
        for inimigo in inimigos:
            dx = inimigo["rect"].centerx - centro[0]
            dy = inimigo["rect"].centery - centro[1]
            distancia = max(1, math.hypot(dx, dy))
            if distancia <= 190:
                dano = _atingir_inimigo(
                    inimigo, dano_base * 3, True, agora, audio, estatisticas
                )
                inimigo["rect"].x += int(dx / distancia * 75)
                inimigo["rect"].y += int(dy / distancia * 75)
                if particulas:
                    particulas.criar_texto_dano(
                        inimigo["rect"].centerx, inimigo["rect"].y - 12,
                        f"-{dano}!!!", AMARELO, True,
                    )
    elif mitica_id == "pistolas_duplas":
        for tiro in range(16):
            angulo = math.tau * tiro / 16
            projeteis.append({
                "x": centro[0], "y": centro[1],
                "vx": math.cos(angulo) * 11, "vy": math.sin(angulo) * 11,
                "dano": dano_base, "crit": critico_base, "dono": jogador.numero_jogador,
                "arma": arma, "pierce": True, "hit_ids": [],
            })
    elif mitica_id == "arco_luz":
        angulo = math.atan2(mouse_pos[1] - centro[1], mouse_pos[0] - centro[0])
        projeteis.append({
            "x": centro[0], "y": centro[1],
            "vx": math.cos(angulo) * 13, "vy": math.sin(angulo) * 13,
            "dano": dano_base * 2, "crit": True, "dono": jogador.numero_jogador,
            "arma": arma, "pierce": True, "split": True, "hit_ids": [],
        })
    elif mitica_id == "cajado_explosao":
        if indice == 0:
            angulo = math.atan2(mouse_pos[1] - centro[1], mouse_pos[0] - centro[0])
            projeteis.append({
                "x": centro[0], "y": centro[1],
                "vx": math.cos(angulo) * 9, "vy": math.sin(angulo) * 9,
                "dano": dano_base * 1.25, "crit": critico_base,
                "dono": jogador.numero_jogador, "arma": arma, "raio_explosao": 65,
            })
        elif indice == 1:
            for inimigo in inimigos:
                if math.dist(centro, inimigo["rect"].center) <= 175:
                    dano = _atingir_inimigo(
                        inimigo, dano_base * 1.8, critico_base, agora, audio, estatisticas
                    )
                    dx = inimigo["rect"].centerx - centro[0]
                    dy = inimigo["rect"].centery - centro[1]
                    distancia = max(1, math.hypot(dx, dy))
                    inimigo["rect"].x += int(dx / distancia * 65)
                    inimigo["rect"].y += int(dy / distancia * 65)
                    if particulas:
                        particulas.criar_texto_dano(
                            inimigo["rect"].centerx, inimigo["rect"].y - 10,
                            f"-{dano}", LARANJA,
                        )
        elif indice == 2:
            jogador.meteoros_ativos = getattr(jogador, "meteoros_ativos", [])
            jogador.meteoros_ativos.append({
                "pos": tuple(mouse_pos), "detonar": agora + 500,
                "dano": dano_base * 2.2, "raio": 120,
            })
        else:
            jogador.conjuracao_explosao = {
                "inicio": agora,
                "fim": agora + 800,
                "dano": dano_base * 6,
            }
            jogador.imovel_ate = agora + 800
            if particulas:
                particulas.criar_texto_dano(
                    *centro,
                    "EXPLOSION!",
                    LARANJA,
                    True,
                )
            if audio:
                audio.tocar_som("magia")
            return True
    elif mitica_id == "grimorio_infinito":
        jogador.singularidade_ativa = {
            "pos": tuple(mouse_pos), "fim": agora + 1800,
            "dano": dano_base * 2.8, "explodir": True,
        }

    if audio:
        audio.tocar_som("magia" if mitica_id in ("cajado_explosao", "grimorio_infinito") else "critico")
    if mitica_id == "cajado_explosao":
        jogador.poder_mantra = min(
            100, getattr(jogador, "poder_mantra", 0) + 10
        )
    return True


def atualizar_conjuracao_mitica(
    jogador, agora, inimigos, particulas, audio, estatisticas
):
    conjuracao = getattr(jogador, "conjuracao_explosao", None)
    if not conjuracao or agora < conjuracao["fim"]:
        return False

    for inimigo in inimigos:
        dano = _atingir_inimigo(
            inimigo, conjuracao["dano"], True, agora, audio, estatisticas
        )
        if particulas:
            particulas.criar_texto_dano(
                inimigo["rect"].centerx,
                inimigo["rect"].y - 12,
                f"-{dano}!!!",
                AMARELO,
                True,
            )
    if particulas:
        particulas.criar_explosao(*jogador.rect.center, LARANJA)
    jogador.conjuracao_explosao = None
    jogador.imovel_ate = agora + 700
    return True


def registrar_baixa_vida(jogador, agora, audio):
    abaixo = jogador.hp > 0 and jogador.hp / max(1, jogador.hp_max) < 0.2
    proximo = getattr(jogador, "heartbeat_proximo", 0)
    if abaixo and agora >= proximo:
        jogador.heartbeat_proximo = agora + 850
        if audio:
            audio.tocar_som("heartbeat")
    return abaixo


def desenhar_efeito_vida_baixa(surface):
    camada = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    camada.fill((20, 0, 0, 55))
    largura, altura = surface.get_size()
    pygame.draw.rect(camada, (110, 0, 0, 55), (0, 0, largura, altura), 28)
    surface.blit(camada, (0, 0))
