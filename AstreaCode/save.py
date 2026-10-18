# save.py
import json
import os

ARQUIVO_SAVE = "save_roguelike.json"

def carregar_dados():
    if os.path.exists(ARQUIVO_SAVE):
        try:
            with open(ARQUIVO_SAVE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    dados_iniciais = {
        "gemas": 50, # Começa com algumas gemas para teste na loja
        "upgrades_permanentes": {
            "hp_extra": 0,
            "mana_extra": 0,
            "dano_extra": 0
        },
        "index_descobertas": {
            "armas": {"pistola": True},
            "artefatos": {"moeda_sorte": True},
            "itens": {},
            "inimigos": {},
            "mobs": {}
        }
    }
    salvar_dados(dados_iniciais)
    return dados_iniciais

def salvar_dados(dados):
    try:
        with open(ARQUIVO_SAVE, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)
    except Exception:
        pass