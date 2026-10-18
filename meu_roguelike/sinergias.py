SINERGIAS = {
    "melee": ("Anel do Vampiro Menor", "sinergia_vampirismo"),
    "ranged": ("Olho do Falcão", "sinergia_mira"),
    "mage": ("Medalhão de Mana Infinita", "sinergia_mana"),
}


def sinergia_ativa(jogador):
    arma = getattr(jogador, "equipado_arma", None)
    if not arma:
        return None

    tipo_arma = arma.get("tipo_arma")
    sinergia = SINERGIAS.get(tipo_arma)
    if not sinergia:
        return None

    nome_amulet = sinergia[0]
    if any(
        amuleto.get("nome") == nome_amulet
        for amuleto in getattr(jogador, "amuletos_equipados", ())
    ):
        return sinergia[1]
    return None


def custo_mana_com_sinergia(jogador, custo):
    if sinergia_ativa(jogador) == "sinergia_mana":
        return max(1, int(custo * 0.75 + 0.5))
    return custo


def velocidade_projetil_com_sinergia(jogador, velocidade):
    if sinergia_ativa(jogador) == "sinergia_mira":
        return velocidade * 1.25
    return velocidade


def curar_por_sinergia_critica(jogador, eh_critico):
    if eh_critico and sinergia_ativa(jogador) == "sinergia_vampirismo":
        vida_anterior = jogador.hp
        jogador.hp = min(jogador.hp_max, jogador.hp + 5)
        return jogador.hp - vida_anterior
    return 0
