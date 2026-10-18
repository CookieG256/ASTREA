import random

COSMETICOS = {
    "aura_astral": {
        "nome": {"PT": "Aura Astral", "ES": "Aura Astral", "EN": "Astral Aura"},
        "cor": (75, 220, 255),
        "bonus": {"multiplicador_gemas": 1.05},
    },
    "chama_violeta": {
        "nome": {"PT": "Chama Violeta", "ES": "Llama Violeta", "EN": "Violet Flame"},
        "cor": (205, 95, 255),
        "bonus": {"multiplicador_dano_cosmetico": 1.03},
    },
    "folha_dourada": {
        "nome": {"PT": "Folha Dourada", "ES": "Hoja Dorada", "EN": "Golden Leaf"},
        "cor": (255, 205, 90),
        "bonus": {"hp_max": 1.03},
    },
    "mar_de_estrelas": {
        "nome": {"PT": "Mar de Estrelas", "ES": "Mar de Estrellas", "EN": "Starfield"},
        "cor": (120, 145, 255),
        "bonus": {},
    },
    "rosa_nebulosa": {
        "nome": {"PT": "Rosa Nebulosa", "ES": "Rosa Nebulosa", "EN": "Nebula Rose"},
        "cor": (255, 105, 190),
        "bonus": {"multiplicador_gemas": 1.10},
    },
    "coroa_do_vazio": {
        "nome": {"PT": "Coroa do Vazio", "ES": "Corona del Vacío", "EN": "Void Crown"},
        "cor": (180, 140, 255),
        "bonus": {"dash_cooldown": 0.97},
    },
}

COSMETICO_PADRAO = "mar_de_estrelas"


def desbloquear_cosmetico(dados, cosmetico_id):
    if cosmetico_id not in COSMETICOS:
        return False
    desbloqueados = dados.setdefault("cosmeticos_desbloqueados", [])
    if cosmetico_id in desbloqueados:
        return False
    desbloqueados.append(cosmetico_id)
    return True


def sortear_cosmetico_bloqueado(dados):
    desbloqueados = set(dados.get("cosmeticos_desbloqueados", []))
    disponiveis = [item for item in COSMETICOS if item not in desbloqueados]
    return random.choice(disponiveis) if disponiveis else None


def obtener_cosmeticos_equipados(dados):
    equipados = dados.get("cosmeticos_equipados", {})
    if not isinstance(equipados, dict):
        equipados = {}
    legado = dados.get("cosmetico_equipado")
    return {
        "P1": equipados.get("P1", legado if legado in COSMETICOS else COSMETICO_PADRAO),
        "P2": equipados.get("P2", COSMETICO_PADRAO),
    }
