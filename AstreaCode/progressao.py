import random
from datetime import date

from save import carregar_dados, salvar_dados
from cosmeticos import desbloquear_cosmetico


CONTRATOS = (
    {"objetivo": "abates", "meta": 12, "recompensa": 20},
    {"objetivo": "elites", "meta": 1, "recompensa": 35},
)


def iniciar_contrato(andar):
    contrato = random.choice(CONTRATOS).copy()
    contrato.update({
        "andar": andar,
        "progresso": 0,
        "concluido": False,
        "recompensa": contrato["recompensa"] + max(0, andar - 1) * 2,
    })
    return contrato


def registrar_abate(estatisticas, inimigo):
    contrato = estatisticas.get("contrato")
    if not contrato or contrato.get("concluido"):
        return
    if contrato["objetivo"] == "abates" or (
        contrato["objetivo"] == "elites" and inimigo.get("elite")
    ):
        contrato["progresso"] = min(contrato["meta"], contrato["progresso"] + 1)


def registrar_uso_arma(tipo_arma):
    dados = carregar_dados()
    maestrias = dados.setdefault("maestria_armas", {})
    maestrias[tipo_arma] = int(maestrias.get(tipo_arma, 0)) + 1
    salvar_dados(dados)
    return maestrias[tipo_arma]


def bonus_maestria(tipo_arma):
    usos = carregar_dados().get("maestria_armas", {}).get(tipo_arma, 0)
    return min(0.12, (int(usos) // 25) * 0.02)


def estado_desafio_diario():
    dados = carregar_dados()
    hoje = date.today().isoformat()
    desafio = dados.get("desafio_diario", {})
    if desafio.get("data") != hoje:
        desafio = {"data": hoje, "abates": 0, "concluido": False}
        dados["desafio_diario"] = desafio
        salvar_dados(dados)
    return desafio


def registrar_abate_diario():
    dados = carregar_dados()
    hoje = date.today().isoformat()
    desafio = dados.get("desafio_diario", {})
    if desafio.get("data") != hoje:
        desafio = {"data": hoje, "abates": 0, "concluido": False}
    if not desafio.get("concluido"):
        desafio["abates"] = min(20, int(desafio.get("abates", 0)) + 1)
        if desafio["abates"] >= 20:
            desafio["concluido"] = True
            desbloquear_cosmetico(dados, "aura_astral")
        dados["desafio_diario"] = desafio
        salvar_dados(dados)
    return desafio


def concluir_contrato(estatisticas):
    contrato = estatisticas.get("contrato")
    if not contrato or contrato.get("concluido") or contrato["progresso"] < contrato["meta"]:
        return 0
    contrato["concluido"] = True
    dados = carregar_dados()
    dados["gemas"] = int(dados.get("gemas", 0)) + contrato["recompensa"]
    salvar_dados(dados)
    return contrato["recompensa"]
