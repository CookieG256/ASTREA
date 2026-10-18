import pygame

from config import LARGURA, ALTURA, obter_multiplicadores_andar, arredondar_para_5
from idiomas import t


_EFEITOS = {
    1: ("ambiente_vento", "slow", 5000),
    2: ("ambiente_sombra", "dark", 0),
    3: ("ambiente_cristal", "damage", 5),
    4: ("ambiente_calor", "damage", 5),
    5: ("ambiente_toxico", "poison", 3000),
    6: ("ambiente_ruinas", "slow", 3500),
    7: ("ambiente_gelo", "slow", 3500),
    8: ("ambiente_lava", "damage", 10),
    9: ("ambiente_escuridao", "dark", 0),
    10: ("ambiente_vazio", "damage", 10),
    11: ("ambiente_cinzas", "damage", 5),
    12: ("ambiente_gravidade", "slow", 3000),
    13: ("ambiente_necrose", "poison", 3000),
    14: ("ambiente_fenda", "damage", 10),
    15: ("ambiente_colapso", "damage", 15),
}


def aplicar_ambiente(bioma_id, andar, player, status_manager, tempo_atual, particulas=None, lang="PT"):
    chave, tipo, valor = _EFEITOS.get(int(bioma_id), _EFEITOS[1])
    reliquias = {
        reliquia.get("nome")
        for reliquia in getattr(player, "reliquias_run", [])
        if isinstance(reliquia, dict)
    }
    if bioma_id in (2, 9):
        if "arcana" in reliquias and tempo_atual >= getattr(player, "proximo_tick_ambiente", 0):
            player.proximo_tick_ambiente = tempo_atual + 6500
            player.mana = min(player.mana_max, player.mana + 8)
            if particulas:
                particulas.criar_texto_dano(
                    player.rect.centerx, player.rect.y - 18, "+8 MP · ARCANA", (150, 130, 255)
                )
        return t(chave, lang), tipo

    proximo = getattr(player, "proximo_tick_ambiente", 0)
    if not proximo:
        player.proximo_tick_ambiente = tempo_atual + 6500
        return t(chave, lang), tipo
    if tempo_atual < proximo:
        return t(chave, lang), tipo

    player.proximo_tick_ambiente = tempo_atual + 6500
    if tipo == "damage":
        mult_dano = obter_multiplicadores_andar(andar)["multiplicador_dano_inimigo"]
        reducao_reliquia = 0.5 if "vitalidade" in reliquias else 1.0
        dano_base = max(5, arredondar_para_5(
            valor * min(1.5, mult_dano) * 0.25
        ))
        dano = max(1, int(dano_base * reducao_reliquia))
        player.hp = max(1, player.hp - dano)
        if particulas:
            particulas.criar_texto_dano(
                player.rect.centerx, player.rect.y - 18, f"{t(chave, lang)} -{dano}", (220, 100, 150)
            )
    elif tipo == "poison":
        duracao = int(valor * (0.7 if "vitalidade" in reliquias else 1.0))
        status_manager.adicionar_efeito("veneno", "debuff", duracao, 0)
        if particulas:
            particulas.criar_texto_dano(player.rect.centerx, player.rect.y - 18, t(chave, lang), (120, 210, 100))
    elif tipo == "slow":
        duracao = int(valor * (0.7 if "vitalidade" in reliquias else 1.0))
        status_manager.adicionar_efeito("lentidao", "debuff", duracao, 0.2)
        if particulas:
            particulas.criar_texto_dano(player.rect.centerx, player.rect.y - 18, t(chave, lang), (160, 190, 230))
    return t(chave, lang), tipo


def desenhar_ambiente(tela, bioma_id, tempo_atual):
    if int(bioma_id) not in (2, 9, 14):
        return
    intensidade = 55 if bioma_id == 2 else 90 if bioma_id == 9 else 35
    import math

    pulso = int(12 * (1 + math.sin(tempo_atual / 700)))
    mascara = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    pygame.draw.rect(mascara, (8, 5, 22, min(140, intensidade + pulso)), (60, 60, LARGURA - 120, ALTURA - 120))
    tela.blit(mascara, (0, 0))
