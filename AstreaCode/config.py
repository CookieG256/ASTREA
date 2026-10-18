# config.py
import math
import pygame

LARGURA = 900
ALTURA = 600

PRETO = (15, 15, 20)
BRANCO = (240, 240, 240)
CINZA = (50, 50, 60)
CINZA_CLARO = (140, 140, 150)
VERMELHO = (230, 50, 50)
VERMELHO_ESCURO = (130, 10, 10)
VERDE = (50, 220, 100)
AZUL = (50, 120, 230)
AMARELO = (240, 200, 50)
ROXO = (160, 60, 240)
CIANO = (0, 255, 255)
VERDE_CLARO = (150, 255, 150)
LARANJA = (255, 140, 0)

FUNDO_UI = (13, 16, 29)
PAINEL_UI = (24, 29, 48)
PAINEL_UI_CLARO = (35, 42, 66)
BORDA_UI = (74, 89, 125)
DOURADO_UI = (238, 190, 91)
CIANO_UI = (87, 207, 202)
ROXO_UI = (133, 112, 206)
CONTORNO_TEXTO = (0, 0, 0)

RARIDADE_CORES = {
    "Comum": BRANCO,
    "Incomum": VERDE,
    "Raro": AZUL,
    "Épico": ROXO,
    "Lendário": AMARELO,
    "Mítico": VERMELHO_ESCURO,
}

pygame.font.init()


class FonteContornada:
    def __init__(self, fonte, contorno=CONTORNO_TEXTO):
        self.fonte = fonte
        self.contorno = contorno

    def render(self, texto, antialias, cor, fundo=None):
        texto_base = self.fonte.render(str(texto), antialias, cor)
        texto_contorno = self.fonte.render(str(texto), antialias, self.contorno)
        margem = 2
        superficie = pygame.Surface(
            (texto_base.get_width() + margem * 2, texto_base.get_height() + margem * 2),
            pygame.SRCALPHA,
        )
        if fundo is not None:
            superficie.fill(fundo)
        centro = (margem, margem)
        for deslocamento in (
            (-1, -1), (0, -1), (1, -1),
            (-1, 0),             (1, 0),
            (-1, 1),  (0, 1),  (1, 1),
        ):
            superficie.blit(
                texto_contorno,
                (centro[0] + deslocamento[0], centro[1] + deslocamento[1]),
            )
        superficie.blit(texto_base, centro)
        return superficie

    def __getattr__(self, atributo):
        return getattr(self.fonte, atributo)


_FONTE_UI = "Georgia"
FONTE_SYS = FonteContornada(pygame.font.SysFont(_FONTE_UI, 15, bold=True))
FONTE_PEQUENA = FonteContornada(pygame.font.SysFont(_FONTE_UI, 12, bold=True))
FONTE_GRANDE = FonteContornada(pygame.font.SysFont(_FONTE_UI, 32, bold=True))
FONTE_TITULO = FonteContornada(pygame.font.SysFont(_FONTE_UI, 48, bold=True))

BIOMAS_ESTETICA = {
    1: {"nome": "Campo Verdejante", "piso": (40, 90, 40), "parede": (20, 60, 20)},
    2: {"nome": "Floresta Sombria", "piso": (30, 60, 40), "parede": (15, 40, 25)},
    3: {"nome": "Caverna de Cristal", "piso": (50, 70, 100), "parede": (30, 45, 75)},
    4: {"nome": "Deserto Ardente", "piso": (160, 130, 70), "parede": (110, 85, 40)},
    5: {"nome": "Pântano Venenoso", "piso": (50, 80, 50), "parede": (25, 45, 25)},
    6: {"nome": "Ruínas Antigas", "piso": (90, 85, 80), "parede": (60, 55, 50)},
    7: {"nome": "Montanha Gélida", "piso": (120, 140, 170), "parede": (70, 90, 120)},
    8: {"nome": "Templo Volcânico", "piso": (100, 35, 30), "parede": (60, 20, 15)},
    9: {"nome": "Torre Sombria", "piso": (45, 30, 60), "parede": (25, 15, 40)},
    10: {"nome": "Abismo do Dragão", "piso": (30, 15, 15), "parede": (15, 5, 5)},
    11: {"nome": "Mar de Cinzas", "piso": (75, 55, 55), "parede": (40, 25, 30)},
    12: {"nome": "Jardins Celestes", "piso": (65, 90, 115), "parede": (35, 50, 80)},
    13: {"nome": "Necrópole Dourada", "piso": (100, 80, 55), "parede": (55, 40, 35)},
    14: {"nome": "Fenda Astral", "piso": (55, 35, 90), "parede": (25, 15, 55)},
    15: {"nome": "Coração do Vazio", "piso": (35, 20, 45), "parede": (15, 5, 25)},
}

BIOMAS_NOMES = {
    "PT": (
        "Campo Verdejante", "Floresta Sombria", "Caverna de Cristal",
        "Deserto Ardente", "Pântano Venenoso", "Ruínas Antigas",
        "Montanha Gélida", "Templo Vulcânico", "Torre Sombria",
        "Abismo do Dragão", "Mar de Cinzas", "Jardins Celestes",
        "Necrópole Dourada", "Fenda Astral", "Coração do Vazio",
    ),
    "EN": (
        "Verdant Fields", "Shadow Forest", "Crystal Cavern",
        "Scorching Desert", "Venomous Swamp", "Ancient Ruins",
        "Frozen Mountain", "Volcanic Temple", "Shadow Tower",
        "Dragon's Abyss", "Sea of Ashes", "Celestial Gardens",
        "Golden Necropolis", "Astral Rift", "Heart of the Void",
    ),
    "ES": (
        "Campos Frondosos", "Bosque Sombrío", "Caverna de Cristal",
        "Desierto Abrasador", "Pantano Venenoso", "Ruinas Antiguas",
        "Montaña Helada", "Templo Volcánico", "Torre Sombría",
        "Abismo del Dragón", "Mar de Cenizas", "Jardines Celestiales",
        "Necrópolis Dorada", "Grieta Astral", "Corazón del Vacío",
    ),
}

BIOMAS_INIMIGOS = {
    1: {"melee": "Lobo Selvagem", "tank": "Javali de Guerra", "ranged": "Falcão Caçador", "support": "Druida do Campo", "mage": "Espírito da Colina", "summoner": "Xamã de Raízes"},
    2: {"melee": "Aranha Venenosa", "tank": "Treant Ancião", "ranged": "Corvo Sombrio", "support": "Fada Curandeira", "mage": "Bruxa da Floresta", "summoner": "Invocador de Esporos"},
    3: {"melee": "Morcego de Cristal", "tank": "Golem de Quartzo", "ranged": "Escorpião das Cavernas", "support": "Oráculo Subterrâneo", "mage": "Mago de Cristal", "summoner": "Invocador de Morcegos"},
    4: {"melee": "Escorpião do Deserto", "tank": "Besouro Colossal", "ranged": "Abutre Caçador", "support": "Curandeiro das Dunas", "mage": "Feiticeiro de Areia", "summoner": "Invocador de Escaravelhos"},
    5: {"melee": "Sanguessuga do Pântano", "tank": "Sapo Blindado", "ranged": "Mosquito Gigante", "support": "Curandeira do Brejo", "mage": "Bruxo Venenoso", "summoner": "Invocador de Lodo"},
    6: {"melee": "Sentinela Quebrada", "tank": "Gárgula de Pedra", "ranged": "Arqueiro Espectral", "support": "Monge das Ruínas", "mage": "Mago Rúnico", "summoner": "Invocador de Espectros"},
    7: {"melee": "Lobo Gélido", "tank": "Yeti Blindado", "ranged": "Coruja da Nevasca", "support": "Xamã Glacial", "mage": "Mago do Gelo", "summoner": "Invocador de Elementais"},
    8: {"melee": "Salamandra Ígnea", "tank": "Golem de Magma", "ranged": "Morcego de Brasa", "support": "Sacerdote das Chamas", "mage": "Feiticeiro Vulcânico", "summoner": "Invocador de Cinzas"},
    9: {"melee": "Assassino Umbral", "tank": "Cavaleiro das Trevas", "ranged": "Atirador do Vazio", "support": "Cultista Sombrio", "mage": "Mago das Sombras", "summoner": "Invocador de Sombras"},
    10: {"melee": "Draconato Guerreiro", "tank": "Dragão de Escamas Negras", "ranged": "Serpente Abissal", "support": "Oráculo do Abismo", "mage": "Mago Dracônico", "summoner": "Invocador de Dracos"},
    11: {"melee": "Carniçal das Cinzas", "tank": "Colosso Carbonizado", "ranged": "Corvo de Brasa", "support": "Monge das Cinzas", "mage": "Piromante Cinzento", "summoner": "Invocador de Brasas"},
    12: {"melee": "Sentinela Celeste", "tank": "Guardião Alado", "ranged": "Arqueiro Solar", "support": "Querubim Curador", "mage": "Oráculo das Nuvens", "summoner": "Invocador de Harpias"},
    13: {"melee": "Saqueador Sepulcral", "tank": "Guardião Mumificado", "ranged": "Escaravelho Real", "support": "Sacerdote Funerário", "mage": "Lich Dourado", "summoner": "Invocador de Ossos"},
    14: {"melee": "Errante Astral", "tank": "Construto Dimensional", "ranged": "Caçador de Fendas", "support": "Tecelã do Éter", "mage": "Mago do Paradoxo", "summoner": "Invocador de Ecos"},
    15: {"melee": "Devorador do Vazio", "tank": "Arauto do Fim", "ranged": "Estilhaço Vivo", "support": "Oráculo Nulo", "mage": "Arquimago Abissal", "summoner": "Invocador de Singularidades"},
}

_NOMES_INIMIGOS_EXTRAS = {
    "assassin": (
        "Raposa Veloz", "Pantera Musgosa", "Morcego Cortante", "Escorpião Saltador",
        "Sanguessuga Ágil", "Lâmina Espectral", "Lince da Neve", "Salamandra Saltadora",
        "Espectro Veloz", "Draco Caçador", "Corredor Carbonizado",
        "Falcão Radiante", "Lâmina Sepulcral", "Vulto da Fenda", "Rasgo do Vazio",
    ),
    "bomber": (
        "Besouro Explosivo", "Cogumelo Volátil", "Cristal Instável", "Escaravelho-Bomba",
        "Bolha Tóxica", "Relíquia Instável", "Gelo Estilhaçante", "Núcleo de Magma",
        "Sombra Instável", "Draco Explosivo", "Brasa Instável",
        "Estrela Cadente", "Urna Explosiva", "Bomba de Éter", "Colapso Vivo",
    ),
}
for _bioma_id, _papeis in BIOMAS_INIMIGOS.items():
    _papeis["assassin"] = _NOMES_INIMIGOS_EXTRAS["assassin"][_bioma_id - 1]
    _papeis["bomber"] = _NOMES_INIMIGOS_EXTRAS["bomber"][_bioma_id - 1]
    _bioma_nome = BIOMAS_NOMES["PT"][_bioma_id - 1]
    _papeis["trapper"] = f"Armadilheiro de {_bioma_nome}"
    _papeis["duelist"] = f"Duelista de {_bioma_nome}"

DIFICULDADE_CONFIG = {
    "EASY": {"multiplicador_dano_inimigo": 1.0, "multiplicador_hp_inimigo": 1.0, "multiplicador_velocidade_inimigo": 1.0, "multiplicador_drop_ouro": 1.0},
    "NORMAL": {"multiplicador_dano_inimigo": 1.5, "multiplicador_hp_inimigo": 1.5, "multiplicador_velocidade_inimigo": 1.2, "multiplicador_drop_ouro": 0.8},
    "HARD": {"multiplicador_dano_inimigo": 3.0, "multiplicador_hp_inimigo": 3.0, "multiplicador_velocidade_inimigo": 1.3, "multiplicador_drop_ouro": 0.5},
    "HARDCORE": {"multiplicador_dano_inimigo": 5.0, "multiplicador_hp_inimigo": 5.0, "multiplicador_velocidade_inimigo": 1.5, "multiplicador_drop_ouro": 0.25}
}

_DIFICULDADE_ALIASES = {
    "CASUAL": "EASY",
    "DIFICIL": "HARD",
}

CONFIG_JOGO = {
    'modo_tiro': 'AUTOMATICO', 
    'volume_sfx': 6,
    'volume_musica': 6,
    'modo_dificuldade': 'EASY',
    'idioma': 'PT',
    'raca_jogador': 'Humano',
    'classe_jogador': 'Guerreiro',
    'coop_local': False,
    'fullscreen': False,
    'mostrar_missoes': True,
    'mostrar_efeitos': True,
    'controles': {
        'P1': {
            'cima': pygame.K_w, 'baixo': pygame.K_s,
            'esquerda': pygame.K_a, 'direita': pygame.K_d,
            'ataque': pygame.K_SPACE, 'dash': pygame.K_q, 'interagir': pygame.K_e,
            'magia_1': pygame.K_h, 'magia_2': pygame.K_j,
            'magia_3': pygame.K_k, 'magia_4': pygame.K_l, 'dispositivo': 'teclado',
        },
        'P2': {
            'cima': pygame.K_UP, 'baixo': pygame.K_DOWN,
            'esquerda': pygame.K_LEFT, 'direita': pygame.K_RIGHT,
            'ataque': pygame.K_KP0, 'dash': pygame.K_RSHIFT, 'interagir': pygame.K_KP_ENTER,
            'magia_1': pygame.K_KP1, 'magia_2': pygame.K_KP2,
            'magia_3': pygame.K_KP3, 'magia_4': pygame.K_KP4, 'dispositivo': 'teclado',
        },
    },
}


def obter_multiplicadores_dificuldade():
    modo = CONFIG_JOGO.get('modo_dificuldade', 'CASUAL')
    modo = _DIFICULDADE_ALIASES.get(modo, modo)
    return DIFICULDADE_CONFIG.get(modo, DIFICULDADE_CONFIG['EASY'])


def obter_modo_dificuldade():
    modo = CONFIG_JOGO.get('modo_dificuldade', 'EASY')
    modo = _DIFICULDADE_ALIASES.get(modo, modo)
    return modo if modo in DIFICULDADE_CONFIG else 'EASY'


def obter_multiplicadores_andar(andar):
    """Difficulty multipliers compounded by the current floor."""
    dificuldade = obter_multiplicadores_dificuldade()
    fator_andar = max(0, int(andar) - 1)
    return {
        **dificuldade,
        "multiplicador_hp_inimigo": dificuldade["multiplicador_hp_inimigo"] * (1 + 0.18 * fator_andar),
        "multiplicador_dano_inimigo": dificuldade["multiplicador_dano_inimigo"] * (1 + 0.12 * fator_andar),
        "multiplicador_velocidade_inimigo": dificuldade["multiplicador_velocidade_inimigo"] * (1 + 0.035 * fator_andar),
        "multiplicador_drop_ouro": dificuldade["multiplicador_drop_ouro"] * (1 + 0.08 * fator_andar),
    }


def arredondar_para_5(valor):
    """Round a numeric game value to the nearest multiple of five."""
    numero = int(math.floor(valor + 0.5))
    if numero < 0:
        return -arredondar_para_5(-numero)
    return ((numero + 2) // 5) * 5


def obter_gemas_chefe(andar):
    """Return boss gem rewards scaled upward by both difficulty and floor."""
    dificuldade = obter_modo_dificuldade()
    multiplicadores = {
        "EASY": 1.0,
        "NORMAL": 1.5,
        "HARD": 2.5,
        "HARDCORE": 4.0,
    }
    andar = max(1, int(andar))
    gemas_base = 10 + 5 * (andar - 1)
    return max(5, arredondar_para_5(gemas_base * multiplicadores[dificuldade]))