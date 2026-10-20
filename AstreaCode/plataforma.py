import os
import sys

import pygame


IS_MOBILE = (
    sys.platform == "android"
    or "ANDROID_ARGUMENT" in os.environ
    or "P4A_BOOTSTRAP" in os.environ
)


class ControlesTouch:
    ACOES_CONTINUAS = (
        "cima", "baixo", "esquerda", "direita", "ataque", "dash", "defesa"
    )
    TECLAS_PULSO = {
        "interagir": pygame.K_e,
        "magia_1": pygame.K_h,
        "magia_2": pygame.K_j,
        "magia_3": pygame.K_k,
        "magia_4": pygame.K_l,
        "pocao": pygame.K_p,
    }

    def __init__(self):
        self.dedos = {}

    def _layout(self, surface):
        largura, altura = surface.get_size()
        escala = min(largura / 900, altura / 600)
        margem = max(8, int(18 * escala))
        tamanho_direcional = max(38, int(58 * escala))
        espaco_direcional = max(4, int(7 * escala))
        base_x = margem
        base_y = altura - margem - tamanho_direcional * 3 - espaco_direcional * 2

        botoes = {
            "cima": pygame.Rect(
                base_x + tamanho_direcional + espaco_direcional, base_y,
                tamanho_direcional, tamanho_direcional,
            ),
            "esquerda": pygame.Rect(
                base_x, base_y + tamanho_direcional + espaco_direcional,
                tamanho_direcional, tamanho_direcional,
            ),
            "direita": pygame.Rect(
                base_x + (tamanho_direcional + espaco_direcional) * 2,
                base_y + tamanho_direcional + espaco_direcional,
                tamanho_direcional, tamanho_direcional,
            ),
            "baixo": pygame.Rect(
                base_x + tamanho_direcional + espaco_direcional,
                base_y + (tamanho_direcional + espaco_direcional) * 2,
                tamanho_direcional, tamanho_direcional,
            ),
        }

        tamanho_acao = max(34, int(50 * escala))
        espaco_acao = max(4, int(7 * escala))
        acoes = (
            ("magia_1", "magia_2", "interagir"),
            ("magia_3", "magia_4", "ataque"),
            ("dash", "pocao", "defesa"),
        )
        base_x_acao = largura - margem - tamanho_acao * 3 - espaco_acao * 2
        base_y_acao = altura - margem - tamanho_acao * 3 - espaco_acao * 2
        rotulos = {
            "magia_1": "M1", "magia_2": "M2", "magia_3": "M3",
            "magia_4": "M4", "interagir": "E", "ataque": "ATQ",
            "dash": "DASH", "pocao": "P", "defesa": "DEF",
        }
        for linha, grupo in enumerate(acoes):
            for coluna, acao in enumerate(grupo):
                if not acao:
                    continue
                botoes[acao] = pygame.Rect(
                    base_x_acao + coluna * (tamanho_acao + espaco_acao),
                    base_y_acao + linha * (tamanho_acao + espaco_acao),
                    tamanho_acao, tamanho_acao,
                )
        return botoes, rotulos, escala

    def processar_evento(self, event, surface, habilitado):
        if not IS_MOBILE:
            return False, ()

        if event.type == pygame.FINGERUP:
            alvo = self.dedos.pop(event.finger_id, None)
            return alvo is not None, ()

        if event.type == pygame.FINGERDOWN:
            if not habilitado:
                return False, ()
            botoes, _, _ = self._layout(surface)
            pos = (int(event.x * surface.get_width()), int(event.y * surface.get_height()))
            alvo = next(
                (nome for nome, rect in botoes.items() if rect.collidepoint(pos)),
                None,
            )
            if alvo is None:
                return False, ()
            self.dedos[event.finger_id] = alvo
            tecla = self.TECLAS_PULSO.get(alvo)
            return True, (tecla,) if tecla is not None else ()

        if event.type == pygame.FINGERMOTION:
            return event.finger_id in self.dedos, ()
        return False, ()

    def acoes_pressionadas(self, habilitado):
        if not IS_MOBILE:
            return {}
        if not habilitado:
            self.dedos.clear()
            return {}
        alvos = set(self.dedos.values())
        return {acao: acao in alvos for acao in self.ACOES_CONTINUAS}

    def eh_botao_touch(self, pos, surface, habilitado):
        if not IS_MOBILE or not habilitado:
            return False
        botoes, _, _ = self._layout(surface)
        return any(rect.collidepoint(pos) for rect in botoes.values())

    def desenhar(self, surface, habilitado):
        if not IS_MOBILE:
            return
        botoes, rotulos, escala = self._layout(surface)
        if not habilitado:
            self.dedos.clear()
            return

        fonte = pygame.font.Font(None, max(16, int(20 * escala)))
        for acao, rect in botoes.items():
            pressionado = acao in self.dedos.values()
            camada = pygame.Surface(rect.size, pygame.SRCALPHA)
            cor = (100, 180, 240, 190) if pressionado else (15, 20, 32, 135)
            pygame.draw.circle(camada, cor, (rect.width // 2, rect.height // 2), min(rect.size) // 2)
            pygame.draw.circle(
                camada, (225, 235, 255, 210),
                (rect.width // 2, rect.height // 2), min(rect.size) // 2, 2,
            )
            texto = fonte.render(rotulos.get(acao, ""), True, (255, 255, 255))
            camada.blit(
                texto,
                (rect.width // 2 - texto.get_width() // 2,
                 rect.height // 2 - texto.get_height() // 2),
            )
            surface.blit(camada, rect.topleft)
