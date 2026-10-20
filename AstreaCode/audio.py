import array
import math
import pygame


_MUSICAS = {
    "menu": (196.0, 246.94, 293.66),
    "bioma_1": (174.61, 220.0, 261.63),
    "bioma_2": (146.83, 185.0, 220.0),
    "bioma_3": (110.0, 164.81, 220.0),
    "bioma_4": (130.81, 164.81, 196.0),
    "bioma_5": (123.47, 155.56, 185.0),
    "bioma_6": (164.81, 207.65, 246.94),
    "bioma_7": (138.59, 174.61, 207.65),
    "bioma_8": (103.83, 130.81, 155.56),
    "bioma_9": (116.54, 146.83, 174.61),
    "bioma_10": (98.0, 123.47, 146.83),
}

_VARIACOES_MUSICA = {
    "exploracao": (1.0, 0.0),
    "perigo": (1.12, 1.5),
    "vida_baixa": (0.82, -2.0),
    "chefe": (0.72, -3.0),
    "chefe_fase": (1.28, 2.5),
}

_BASES_MUSICA = tuple(_MUSICAS.values())
for _bioma_id in range(11, 16):
    _MUSICAS[f"bioma_{_bioma_id}"] = _BASES_MUSICA[(_bioma_id - 1) % len(_BASES_MUSICA)]

_EFEITOS = {
    "menu": (880, 660, 0.07),
    "tiro": (760, 240, 0.09),
    "melee": (170, 65, 0.13),
    "corte": (1200, 220, 0.2),
    "dano": (180, 90, 0.18),
    "critico": (520, 1040, 0.2),
    "magia": (440, 1320, 0.22),
    "cura": (523, 784, 0.25),
    "bau": (330, 880, 0.3),
    "invocacao": (110, 440, 0.35),
    "dash": (620, 180, 0.12),
    "porta": (180, 320, 0.2),
    "morte_inimigo": (260, 100, 0.15),
    "heartbeat": (72, 48, 0.28),
}


class GerenciadorAudio:
    def __init__(self):
        self.ativo = True
        self.volume_sfx = 0.8
        self.volume_musica = 0.5
        self._sons = {}
        self._musicas = {}
        self._musica_atual = None
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=1)
            pygame.mixer.set_num_channels(max(16, pygame.mixer.get_num_channels()))
            self._canal_musica = pygame.mixer.Channel(15)
            for nome, (inicio, fim, duracao) in _EFEITOS.items():
                self._sons[nome] = self._criar_tom(inicio, fim, duracao)
            for nome, frequencias in _MUSICAS.items():
                self._musicas[nome] = self._criar_ambiente(frequencias)
        except pygame.error:
            self.ativo = False

    @staticmethod
    def _normalizar_volume(valor, padrao):
        try:
            volume = float(valor)
        except (TypeError, ValueError):
            volume = padrao
        if volume > 1:
            volume /= 10
        return max(0.0, min(1.0, volume))

    def atualizar_volumes(self, config):
        self.volume_sfx = self._normalizar_volume(config.get("volume_sfx", 0.8), 0.8)
        self.volume_musica = self._normalizar_volume(config.get("volume_musica", 0.5), 0.5)
        if self._musica_atual and self.ativo:
            self._canal_musica.set_volume(self.volume_musica)

    def _criar_tom(self, frequencia_inicio, frequencia_fim, duracao):
        sample_rate = 22050
        amostras = array.array("h")
        total = int(sample_rate * duracao)
        for indice in range(total):
            progresso = indice / max(1, total - 1)
            frequencia = frequencia_inicio + (frequencia_fim - frequencia_inicio) * progresso
            envelope = min(1.0, indice / 250) * max(0.0, 1.0 - progresso) ** 0.7
            valor = int(11000 * envelope * math.sin(2 * math.pi * frequencia * indice / sample_rate))
            amostras.append(valor)
        return pygame.mixer.Sound(buffer=amostras.tobytes())

    def _criar_ambiente(self, frequencias):
        sample_rate = 22050
        duracao = 3.0
        total = int(sample_rate * duracao)
        amostras = array.array("h")
        for indice in range(total):
            tempo = indice / sample_rate
            onda = sum(
                math.sin(2 * math.pi * frequencia * tempo + fase)
                for fase, frequencia in enumerate(frequencias)
            ) / len(frequencias)
            modulacao = 0.68 + 0.32 * math.sin(2 * math.pi * tempo / duracao)
            valor = int(2300 * onda * modulacao)
            amostras.append(valor)
        return pygame.mixer.Sound(buffer=amostras.tobytes())

    def tocar_som(self, tipo):
        if not self.ativo:
            return
        som = self._sons.get(tipo)
        if som:
            som.set_volume(self.volume_sfx)
            som.play()

    def tocar_musica(self, faixa):
        if not self.ativo or faixa not in self._musicas:
            return
        if self._musica_atual == faixa and self._canal_musica.get_busy():
            return
        self._canal_musica.play(self._musicas[faixa], loops=-1)
        self._canal_musica.set_volume(self.volume_musica)
        self._musica_atual = faixa

    def tocar_musica_dinamica(self, bioma_id, situacao):
        if not self.ativo:
            return
        situacao = situacao if situacao in _VARIACOES_MUSICA else "exploracao"
        base = _MUSICAS.get(f"bioma_{bioma_id}", _MUSICAS["bioma_1"])
        escala, deslocamento = _VARIACOES_MUSICA[situacao]
        frequencias = tuple(
            max(55.0, frequencia * escala + deslocamento)
            for frequencia in base
        )
        faixa = f"bioma_{bioma_id}_{situacao}"
        if faixa not in self._musicas:
            self._musicas[faixa] = self._criar_ambiente(frequencias)
        self.tocar_musica(faixa)

    def parar_musica(self):
        if self.ativo:
            self._canal_musica.stop()
        self._musica_atual = None
