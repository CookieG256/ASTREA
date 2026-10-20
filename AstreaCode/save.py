# save.py
import json
from pathlib import Path

ARQUIVO_SAVE = Path("save_roguelike.json")
PASTA_PERFIS = Path("saves")
ARQUIVO_PERFIL_ATUAL = PASTA_PERFIS / "perfil_atual.json"
PERFIS_DISPONIVEIS = ("perfil_1", "perfil_2", "perfil_3", "perfil_4")
_perfil_atual = "perfil_1"


def _caminho_perfil(perfil):
    if perfil not in PERFIS_DISPONIVEIS:
        raise ValueError(f"Perfil inválido: {perfil}")
    return PASTA_PERFIS / f"{perfil}.json"


def _ler_json(caminho):
    if not caminho.exists():
        return None
    with caminho.open("r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def perfil_atual():
    return _perfil_atual


def selecionar_perfil(perfil):
    global _perfil_atual
    caminho = _caminho_perfil(perfil)
    PASTA_PERFIS.mkdir(parents=True, exist_ok=True)
    if not caminho.exists():
        dados = _ler_json(ARQUIVO_SAVE) if perfil == "perfil_1" else None
        _escrever_json(caminho, dados if isinstance(dados, dict) else _dados_iniciais())
    _perfil_atual = perfil
    _escrever_json(ARQUIVO_PERFIL_ATUAL, {"perfil": perfil})


def _inicializar_perfil():
    global _perfil_atual
    metadata = _ler_json(ARQUIVO_PERFIL_ATUAL)
    perfil = metadata.get("perfil") if isinstance(metadata, dict) else None
    if perfil in PERFIS_DISPONIVEIS:
        _perfil_atual = perfil
    selecionar_perfil(_perfil_atual)


def _escrever_json(caminho, dados):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=4)


def _dados_iniciais():
    return {
        "gemas": 50,
        "conquistas": {},
        "estatisticas_conquistas": {},
        "pet_niveis": {},
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


_inicializar_perfil()

def carregar_dados():
    dados = _ler_json(_caminho_perfil(_perfil_atual))
    if isinstance(dados, dict):
        alterado = False
        for chave, padrao in (
            ("conquistas", {}),
            ("estatisticas_conquistas", {}),
            ("pet_niveis", {}),
        ):
            if not isinstance(dados.get(chave), dict):
                dados[chave] = padrao.copy()
                alterado = True
        if alterado:
            salvar_dados(dados)
        return dados
    dados_iniciais = _dados_iniciais()
    salvar_dados(dados_iniciais)
    return dados_iniciais

def salvar_dados(dados):
    _escrever_json(_caminho_perfil(_perfil_atual), dados)