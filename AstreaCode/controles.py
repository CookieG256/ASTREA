import pygame


ACOES = (
    "cima", "baixo", "esquerda", "direita",
    "ataque", "dash", "interagir", "magia_1", "magia_2", "magia_3", "magia_4",
    "defesa",
)

PADROES = {
    "P1": {
        "cima": pygame.K_w, "baixo": pygame.K_s,
        "esquerda": pygame.K_a, "direita": pygame.K_d,
        "ataque": pygame.K_SPACE, "dash": pygame.K_q, "interagir": pygame.K_e,
        "magia_1": pygame.K_h, "magia_2": pygame.K_j,
        "magia_3": pygame.K_k, "magia_4": pygame.K_l,
        "defesa": pygame.K_LCTRL,
        "dispositivo": "teclado",
    },
    "P2": {
        "cima": pygame.K_UP, "baixo": pygame.K_DOWN,
        "esquerda": pygame.K_LEFT, "direita": pygame.K_RIGHT,
        "ataque": pygame.K_KP0, "dash": pygame.K_RSHIFT,
        "interagir": pygame.K_KP_ENTER, "magia_1": pygame.K_KP1,
        "magia_2": pygame.K_KP2, "magia_3": pygame.K_KP3,
        "magia_4": pygame.K_KP4, "defesa": pygame.K_KP_MULTIPLY,
        "dispositivo": "teclado",
    },
}


def padroes_controles():
    return {jogador: dict(acoes) for jogador, acoes in PADROES.items()}


def restaurar_controles(config, jogador):
    if jogador not in PADROES:
        raise ValueError(f"Jogador desconhecido: {jogador}")
    controles = config.setdefault("controles", {})
    controles[jogador] = dict(PADROES[jogador])
    return controles[jogador]


def normalizar_controles(config):
    resultado = padroes_controles()
    informados = config.get("controles", {})
    for jogador in ("P1", "P2"):
        acoes = informados.get(jogador, {}) if isinstance(informados, dict) else {}
        for acao in ACOES:
            valor = acoes.get(acao)
            if isinstance(valor, int):
                resultado[jogador][acao] = valor
        botoes = acoes.get("botoes", {})
        if isinstance(botoes, dict):
            resultado[jogador]["botoes"] = {
                acao: int(valor) for acao, valor in botoes.items()
                if acao in ACOES and isinstance(valor, int) and valor >= 0
            }
        if acoes.get("dispositivo") in ("teclado", "controle"):
            resultado[jogador]["dispositivo"] = acoes["dispositivo"]
    config["controles"] = resultado
    config.setdefault("coop_local", False)
    config.setdefault("fullscreen", False)
    return resultado


def estado_acoes_teclado(teclas, controles):
    return {acao: bool(teclas[controles[acao]]) for acao in ACOES}


def traduzir_tecla_acao(tecla, controles, jogador="P1"):
    nomes = {
        "interagir": pygame.K_e,
        "dash": pygame.K_q,
        "magia_1": pygame.K_h,
        "magia_2": pygame.K_j,
        "magia_3": pygame.K_k,
        "magia_4": pygame.K_l,
    }
    for acao, nome_padrao in nomes.items():
        if controles[jogador].get(acao) == tecla:
            return nome_padrao
    return tecla


def estado_analogico(joystick, controles=None, deadzone=0.25):
    if joystick is None or not joystick.get_init():
        return {}
    x = joystick.get_axis(0) if joystick.get_numaxes() > 0 else 0.0
    y = joystick.get_axis(1) if joystick.get_numaxes() > 1 else 0.0
    acoes = {
        "esquerda": x < -deadzone, "direita": x > deadzone,
        "cima": y < -deadzone, "baixo": y > deadzone,
    }
    controles = controles or {}
    for acao in ACOES[4:]:
        indice = int(controles.get("botoes", {}).get(acao, {
            "ataque": 0, "dash": 1, "interagir": 2,
            "magia_1": 3, "magia_2": 4, "magia_3": 5, "magia_4": 6,
            "defesa": 7,
        }.get(acao, 0)))
        acoes[acao] = bool(indice < joystick.get_numbuttons() and joystick.get_button(indice))
    return acoes


def nome_tecla(codigo):
    try:
        nome = pygame.key.name(codigo)
    except (TypeError, ValueError):
        return "?"
    return nome.upper() or "?"
