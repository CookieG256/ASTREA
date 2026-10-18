import random

from config import obter_modo_dificuldade


_AFIXOS = {
    "Comum": (
        ("Afiada", {"dano_percentual": 0.04}),
        ("Ligeira", {"cadencia_percentual": 0.04}),
        ("Precisa", {"critico": 0.02}),
        ("Leve", {"velocidade_projetil": 0.05}),
        ("Sanguessuga", {"roubo_vida": 0.02}),
        ("Econômica", {"mana_percentual": -0.05}),
        ("Longa", {"alcance_percentual": 0.05}),
        ("Firme", {"dano_percentual": 0.03, "critico": 0.01}),
        ("Rúnica", {"mana_percentual": -0.03, "dano_percentual": 0.02}),
        ("Caçadora", {"dano_percentual": 0.05}),
    ),
    "Incomum": (
        ("Flamejante", {"dano_percentual": 0.08, "efeito": "queimadura"}),
        ("Congelante", {"dano_percentual": 0.05, "efeito": "congelamento"}),
        ("Tóxica", {"dano_percentual": 0.06, "efeito": "veneno"}),
        ("Vampírica", {"roubo_vida": 0.05}),
        ("Tempestuosa", {"cadencia_percentual": 0.08}),
        ("Perfurante", {"dano_percentual": 0.10}),
        ("Arcana", {"mana_percentual": -0.10}),
        ("Veloz", {"velocidade_projetil": 0.12}),
    ),
    "Raro": (
        ("Sangrenta", {"dano_percentual": 0.10, "efeito": "sangramento"}),
        ("Glacial", {"dano_percentual": 0.08, "efeito": "congelamento"}),
        ("Solar", {"dano_percentual": 0.14}),
        ("Voraz", {"roubo_vida": 0.08}),
        ("Mortal", {"critico": 0.07}),
        ("Eterea", {"cadencia_percentual": 0.12, "dano_percentual": 0.05}),
    ),
    "Épico": (
        ("Abissal", {"dano_percentual": 0.20, "efeito": "fraqueza"}),
        ("Dracônica", {"dano_percentual": 0.24}),
        ("Sifão Arcano", {"roubo_vida": 0.10, "mana_percentual": -0.10}),
        ("Relâmpago", {"cadencia_percentual": 0.18, "velocidade_projetil": 0.20}),
    ),
    "Lendário": (
        ("Devoradora de Almas", {"dano_percentual": 0.30, "roubo_vida": 0.15}),
        ("Soberana", {"dano_percentual": 0.35, "critico": 0.10}),
    ),
    "Mítico": (
        ("Ruptura Cósmica", {"dano_percentual": 0.50, "critico": 0.15, "roubo_vida": 0.20}),
    ),
}

assert {raridade: len(nomes) for raridade, nomes in _AFIXOS.items()} == {
    "Comum": 10, "Incomum": 8, "Raro": 6, "Épico": 4, "Lendário": 2, "Mítico": 1
}

_PESOS = {
    "EASY": (62, 25, 9, 3, 0.8, 0.2),
    "NORMAL": (50, 27, 13, 7, 2.5, 0.5),
    "HARD": (38, 28, 18, 10, 4.5, 1.5),
    "HARDCORE": (30, 27, 21, 13, 6.5, 3),
}
_RARIDADES = ("Comum", "Incomum", "Raro", "Épico", "Lendário", "Mítico")


def sortear_encantamento(dificuldade=None):
    modo = dificuldade or obter_modo_dificuldade()
    pesos = _PESOS.get(modo, _PESOS["EASY"])
    raridade = random.choices(_RARIDADES, weights=pesos, k=1)[0]
    nome, efeitos = random.choice(_AFIXOS[raridade])
    return {"nome": nome, "raridade": raridade, **efeitos}


def aplicar_forja(arma):
    nivel = max(0, int(arma.get("nivel_forja", 0)))
    if nivel >= 5:
        return False
    arma["nivel_forja"] = nivel + 1
    arma["dano"] = max(1, round(arma["dano"] * 1.08))
    arma["cadencia"] = max(100, round(arma.get("cadencia", 400) * 0.985))
    return True


def custo_forja(arma):
    return 100 * (max(0, int(arma.get("nivel_forja", 0))) + 1)


def custo_encantamento(arma):
    return 150 + 75 * len(arma.get("encantamentos", []))
