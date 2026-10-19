MODIFICADORES_RUN = {
    "vidro": {
        "recompensas": 1.50,
        "dano_recebido": 1.50,
    },
    "horda": {
        "recompensas": 1.30,
        "quantidade_inimigos": 1.35,
        "vida_inimigos": 1.35,
        "dano_inimigos": 1.35,
        "velocidade_inimigos": 1.35,
    },
    "frenesi": {
        "recompensas": 1.40,
        "dano_inimigos": 1.20,
        "velocidade_inimigos": 1.25,
    },
    "colossos": {
        "recompensas": 1.35,
        "vida_inimigos": 1.50,
    },
    "cacada": {
        "recompensas": 1.25,
        "chance_elite": 2.0,
        "gemas_elite": 1.50,
    },
    "escassez": {
        "recompensas": 1.50,
        "cura_orbes": 0.50,
    },
}


def calcular_efeitos_modificadores(modificadores):
    efeitos = {
        "recompensas": 1.0,
        "dano_recebido": 1.0,
        "quantidade_inimigos": 1.0,
        "vida_inimigos": 1.0,
        "dano_inimigos": 1.0,
        "velocidade_inimigos": 1.0,
        "chance_elite": 1.0,
        "gemas_elite": 1.0,
        "cura_orbes": 1.0,
    }
    for modificador in modificadores:
        for chave, multiplicador in MODIFICADORES_RUN.get(modificador, {}).items():
            efeitos[chave] *= multiplicador
    return efeitos
