RACES_AND_CLASSES = {
    "races": {
        "Humano": {"icon": "H", "stats": {"hp_max": 1.05, "velocidade": 1.0, "dano_multiplier": 1.0, "dash_cooldown": 1.0, "gem_multiplier": 1.05}},
        "Elfo": {"icon": "E", "stats": {"hp_max": 0.9, "velocidade": 1.12, "dano_multiplier": 1.0, "dash_cooldown": 0.9, "gem_multiplier": 1.0}},
        "Anão": {"icon": "A", "stats": {"hp_max": 1.2, "velocidade": 0.88, "dano_multiplier": 1.05, "dash_cooldown": 1.1, "gem_multiplier": 1.0}},
        "Ciborgue": {"icon": "C", "stats": {"hp_max": 1.05, "velocidade": 1.0, "dano_multiplier": 1.08, "dash_cooldown": 0.95, "gem_multiplier": 0.95}},
        "Robô": {"icon": "R", "stats": {"hp_max": 1.15, "velocidade": 0.95, "dano_multiplier": 1.0, "dash_cooldown": 1.0, "gem_multiplier": 1.1}},
        "Demônio": {"icon": "D", "stats": {"hp_max": 0.95, "velocidade": 1.0, "dano_multiplier": 1.12, "dash_cooldown": 1.0, "gem_multiplier": 0.95}},
    },
    "classes": {
        "Guerreiro": {"icon": "G", "stats": {"hp_max": 1.15, "velocidade": 0.95, "dano_multiplier": 1.08, "dash_cooldown": 1.05, "gem_multiplier": 1.0}},
        "Espadachim": {"icon": "E", "stats": {"hp_max": 1.0, "velocidade": 1.05, "dano_multiplier": 1.12, "dash_cooldown": 0.9, "gem_multiplier": 1.0}},
        "Mago": {"icon": "M", "stats": {"hp_max": 0.9, "velocidade": 1.0, "dano_multiplier": 1.15, "dash_cooldown": 1.0, "gem_multiplier": 1.0}},
        "Atirador": {"icon": "A", "stats": {"hp_max": 0.95, "velocidade": 1.05, "dano_multiplier": 1.08, "dash_cooldown": 0.95, "gem_multiplier": 1.0}},
        "Caçador": {"icon": "C", "stats": {"hp_max": 1.0, "velocidade": 1.1, "dano_multiplier": 1.0, "dash_cooldown": 0.9, "gem_multiplier": 1.1}},
        "Ladrão": {"icon": "L", "stats": {"hp_max": 0.9, "velocidade": 1.15, "dano_multiplier": 1.0, "dash_cooldown": 0.85, "gem_multiplier": 1.15}},
    },
}

ARMAS_INICIAIS = {
    "Guerreiro": "Espada Curta de Ferro",
    "Espadachim": "Rapieira de Treino",
    "Mago": "Varinha de Eucalipto",
    "Atirador": "Arco de Caça Simples",
    "Caçador": "Faca de Caça",
    "Ladrão": "Adaga Enferrujada",
}

STAT_LABELS = {
    "hp_max": "Vida",
    "velocidade": "Velocidade",
    "dano_multiplier": "Dano",
    "dash_cooldown": "Recarga do dash",
    "gem_multiplier": "Gemas",
}


def stats_selecao(raca, classe):
    stats = {}
    for chave in ("races", "classes"):
        opcoes = RACES_AND_CLASSES[chave]
        nome = raca if chave == "races" else classe
        escolhido = opcoes.get(nome, next(iter(opcoes.values())))
        for atributo, multiplicador in escolhido["stats"].items():
            stats[atributo] = stats.get(atributo, 1.0) * multiplicador
    return stats
