MODIFICADORES_RUN = {
    "vidro": {
        "nome": "modificador_vidro_nome",
        "descricao": "modificador_vidro_desc",
        "efeitos": {"recompensa": 1.5, "dano_recebido": 1.5},
    },
    "horda": {
        "nome": "modificador_horda_nome",
        "descricao": "modificador_horda_desc",
        "efeitos": {"quantidade": 1.35, "recompensa": 1.3},
    },
    "predadores": {
        "nome": "modificador_predadores_nome",
        "descricao": "modificador_predadores_desc",
        "efeitos": {
            "hp_inimigo": 1.25,
            "dano_inimigo": 1.2,
            "velocidade_inimigo": 1.15,
            "recompensa": 1.25,
        },
    },
    "escassez": {
        "nome": "modificador_escassez_nome",
        "descricao": "modificador_escassez_desc",
        "efeitos": {"cura": 0.0, "drops": 0.7, "elite": 1.5},
    },
    "frenesi": {
        "nome": "modificador_frenesi_nome",
        "descricao": "modificador_frenesi_desc",
        "efeitos": {
            "velocidade_inimigo": 1.3,
            "dano_inimigo": 1.1,
            "recompensa": 1.2,
        },
    },
    "elites": {
        "nome": "modificador_elites_nome",
        "descricao": "modificador_elites_desc",
        "efeitos": {"chance_elite": 0.12, "recompensa": 1.2},
    },
}

ROTULOS_EFEITOS_MODIFICADORES = {
    "recompensa": "modificador_efeito_recompensa",
    "dano_recebido": "modificador_efeito_dano_recebido",
    "quantidade": "modificador_efeito_quantidade",
    "hp_inimigo": "modificador_efeito_hp_inimigo",
    "dano_inimigo": "modificador_efeito_dano_inimigo",
    "velocidade_inimigo": "modificador_efeito_velocidade_inimigo",
    "cura": "modificador_efeito_cura",
    "drops": "modificador_efeito_drops",
    "elite": "modificador_efeito_elite",
    "chance_elite": "modificador_efeito_chance_elite",
}


def obter_efeitos_modificadores(chaves):
    efeitos = {
        "recompensa": 1.0,
        "dano_recebido": 1.0,
        "quantidade": 1.0,
        "hp_inimigo": 1.0,
        "dano_inimigo": 1.0,
        "velocidade_inimigo": 1.0,
        "cura": 1.0,
        "drops": 1.0,
        "elite": 1.0,
        "chance_elite": 0.0,
    }
    for chave in chaves:
        modificador = MODIFICADORES_RUN.get(chave)
        if not modificador:
            continue
        for efeito, valor in modificador["efeitos"].items():
            if efeito == "chance_elite":
                efeitos[efeito] += valor
            else:
                efeitos[efeito] *= valor
    return efeitos