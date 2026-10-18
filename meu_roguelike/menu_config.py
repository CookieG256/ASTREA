import pygame

from config import (
    LARGURA, ALTURA, BRANCO, FUNDO_UI, PAINEL_UI, PAINEL_UI_CLARO,
    BORDA_UI, DOURADO_UI, ROXO_UI, FONTE_SYS, FONTE_GRANDE, CIANO_UI
)
from controles import ACOES, normalizar_controles, nome_tecla, restaurar_controles
from idiomas import t
from save import carregar_dados, salvar_dados


def _volume_normalizado(valor, padrao):
    try:
        resultado = float(valor)
    except (TypeError, ValueError):
        resultado = padrao
    if resultado > 1:
        resultado /= 10
    return max(0.0, min(1.0, resultado))


class MenuConfiguracoes:
    def __init__(self):
        self.pagina = "principal"
        self.topico = "audio"
        self.aguardando = None
        self.btns = {}

    @staticmethod
    def _botao(tela, rect, texto, pos_mouse, cor_texto=BRANCO):
        hover = rect.collidepoint(pos_mouse)
        pygame.draw.rect(tela, PAINEL_UI_CLARO if hover else PAINEL_UI, rect, border_radius=8)
        pygame.draw.rect(tela, ROXO_UI if hover else BORDA_UI, rect, 2 if hover else 1, border_radius=8)
        label = FONTE_SYS.render(texto, True, DOURADO_UI if hover else cor_texto)
        tela.blit(label, (rect.centerx - label.get_width() // 2, rect.centery - label.get_height() // 2))

    def _salvar_config(self, config_jogo):
        dados = carregar_dados()
        dados["configuracoes"] = {
            chave: valor for chave, valor in config_jogo.items()
            if chave in ("idioma", "modo_tiro", "volume_musica", "volume_sfx", "modo_dificuldade",
                         "classe_jogador", "coop_local", "fullscreen", "controles",
                         "mostrar_missoes", "mostrar_efeitos")
        }
        salvar_dados(dados)

    def desenhar(self, tela, config_jogo, pos_mouse):
        tela.fill(FUNDO_UI)
        lang = config_jogo.get("idioma", "PT")
        titulo = FONTE_GRANDE.render(t("config", lang), True, DOURADO_UI)
        tela.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 35))
        self.btns = {}

        if self.pagina == "principal":
            normalizar_controles(config_jogo)
            topicos = (
                ("audio", "config_audio"),
                ("gameplay", "config_gameplay"),
                ("idioma", "config_idioma"),
                ("extras", "config_extras"),
                ("coop", "config_coop"),
                ("controles", "config_controles"),
            )
            for indice, (chave, texto) in enumerate(topicos):
                coluna = indice % 3
                linha = indice // 3
                rect = pygame.Rect(55 + coluna * 265, 88 + linha * 42, 255, 34)
                self.btns[f"topico:{chave}"] = rect
                self._botao(tela, rect, t(texto, lang), pos_mouse,
                            DOURADO_UI if chave == self.topico else BRANCO)

            valores = {
                "audio": (
                    ("musica", f"{t('volume_musica', lang)}: {round(_volume_normalizado(config_jogo.get('volume_musica', 0.6), 0.6) * 10)}/10"),
                    ("sfx", f"{t('volume_sfx', lang)}: {round(_volume_normalizado(config_jogo.get('volume_sfx', 0.6), 0.6) * 10)}/10"),
                ),
                "gameplay": (
                    ("modo", f"{t('modo_tiro', lang)}: {t(config_jogo.get('modo_tiro', 'AUTOMATICO'), lang)}"),
                    ("mostrar_missoes", f"{t('mostrar_missoes', lang)}: {t('ativado' if config_jogo.get('mostrar_missoes', True) else 'desativado', lang)} · T"),
                    ("mostrar_efeitos", f"{t('mostrar_efeitos', lang)}: {t('ativado' if config_jogo.get('mostrar_efeitos', True) else 'desativado', lang)} · Y"),
                ),
                "idioma": (("idioma", f"{t('idioma', lang)}: {lang}"),),
                "extras": (("fullscreen", f"{t('tela_cheia', lang)}: {t('ativado' if config_jogo.get('fullscreen') else 'desativado', lang)}"),),
                "coop": (("coop", f"{t('coop_local', lang)}: {t('ativado' if config_jogo.get('coop_local') else 'desativado', lang)}"),),
                "controles": (("controles", t("mapear_controles", lang)),),
            }
            titulo_topico = FONTE_SYS.render(t(f"config_{self.topico}", lang), True, CIANO_UI)
            tela.blit(titulo_topico, (LARGURA // 2 - titulo_topico.get_width() // 2, 190))
            for indice, (chave, texto) in enumerate(valores[self.topico]):
                rect = pygame.Rect(LARGURA // 2 - 230, 230 + indice * 54, 460, 42)
                self.btns[chave] = rect
                self._botao(tela, rect, texto, pos_mouse)
            rect = pygame.Rect(LARGURA // 2 - 105, ALTURA - 58, 210, 40)
            self.btns["voltar"] = rect
            self._botao(tela, rect, t("voltar", lang), pos_mouse, DOURADO_UI)
            return

        controles = normalizar_controles(config_jogo)
        for coluna, jogador in enumerate(("P1", "P2")):
            x = 75 + coluna * 390
            cabecalho = FONTE_SYS.render(
                f"{t('jogador_um' if jogador == 'P1' else 'jogador_dois', lang)} · {t('dispositivo_' + controles[jogador]['dispositivo'], lang)}",
                True, DOURADO_UI,
            )
            tela.blit(cabecalho, (x + 8, 82))
            disp = pygame.Rect(x + 236, 76, 124, 32)
            self.btns[f"{jogador}:dispositivo"] = disp
            self._botao(tela, disp, t("alternar_dispositivo", lang), pos_mouse)
            for indice, acao in enumerate(ACOES):
                rect = pygame.Rect(x, 116 + indice * 31, 350, 27)
                self.btns[f"{jogador}:{acao}"] = rect
                aguardando = self.aguardando == (jogador, acao)
                if controles[jogador]["dispositivo"] == "controle" and acao in ("cima", "baixo", "esquerda", "direita"):
                    valor = t("analógico", lang)
                elif controles[jogador]["dispositivo"] == "controle":
                    botoes = controles[jogador].get("botoes", {})
                    valor = f"BTN {int(botoes.get(acao, 0)) + 1}"
                else:
                    valor = nome_tecla(controles[jogador][acao])
                texto = t("pressione_tecla", lang) if aguardando else f"{t('acao_' + acao, lang)}: {valor}"
                self._botao(tela, rect, texto, pos_mouse)
            reset = pygame.Rect(x, 470, 350, 32)
            self.btns[f"{jogador}:restaurar"] = reset
            self._botao(tela, reset, t("restaurar_controles", lang), pos_mouse, DOURADO_UI)
        voltar = pygame.Rect(LARGURA // 2 - 105, ALTURA - 48, 210, 36)
        self.btns["voltar"] = voltar
        self._botao(tela, voltar, t("voltar", lang), pos_mouse, DOURADO_UI)
        if self.aguardando:
            aviso = FONTE_SYS.render(t("aguardando_controle", lang), True, DOURADO_UI)
            tela.blit(aviso, (LARGURA // 2 - aviso.get_width() // 2, ALTURA - 92))

    def tratar_clique(self, pos_mouse, config_jogo):
        normalizar_controles(config_jogo)
        if self.pagina == "principal":
            for chave, rect in self.btns.items():
                if chave.startswith("topico:") and rect.collidepoint(pos_mouse):
                    self.topico = chave.split(":", 1)[1]
                    return None
            for chave, rect in self.btns.items():
                if not rect.collidepoint(pos_mouse):
                    continue
                if chave == "modo":
                    config_jogo["modo_tiro"] = "MANUAL" if config_jogo.get("modo_tiro") == "AUTOMATICO" else "AUTOMATICO"
                elif chave == "idioma":
                    idiomas = ("PT", "ES", "EN")
                    atual = config_jogo.get("idioma", "PT")
                    config_jogo["idioma"] = idiomas[(idiomas.index(atual) + 1) % len(idiomas)]
                elif chave in ("musica", "sfx"):
                    chave_config = "volume_musica" if chave == "musica" else "volume_sfx"
                    valor = _volume_normalizado(config_jogo.get(chave_config, 0.6), 0.6)
                    config_jogo[chave_config] = 0.0 if valor >= 1.0 else round(valor + 0.2, 1)
                elif chave in ("mostrar_missoes", "mostrar_efeitos"):
                    config_jogo[chave] = not config_jogo.get(chave, True)
                elif chave == "fullscreen":
                    config_jogo["fullscreen"] = not config_jogo.get("fullscreen", False)
                    self._salvar_config(config_jogo)
                    return "TELA_CHEIA"
                elif chave == "coop":
                    config_jogo["coop_local"] = not config_jogo.get("coop_local", False)
                elif chave == "controles":
                    self.pagina = "controles"
                elif chave == "voltar":
                    self._salvar_config(config_jogo)
                    self.pagina = "principal"
                    return "VOLTAR"
                self._salvar_config(config_jogo)
                return None
            return None

        if self.btns.get("voltar", pygame.Rect(0, 0, 0, 0)).collidepoint(pos_mouse):
            self.aguardando = None
            self.pagina = "principal"
            return None
        for jogador in ("P1", "P2"):
            reset = self.btns.get(f"{jogador}:restaurar")
            if reset and reset.collidepoint(pos_mouse):
                restaurar_controles(config_jogo, jogador)
                self.aguardando = None
                self._salvar_config(config_jogo)
                return None
            dispositivo = self.btns.get(f"{jogador}:dispositivo")
            if dispositivo and dispositivo.collidepoint(pos_mouse):
                estado = config_jogo["controles"][jogador]
                estado["dispositivo"] = "controle" if estado["dispositivo"] == "teclado" else "teclado"
                self._salvar_config(config_jogo)
                return None
            for acao in ACOES:
                rect = self.btns.get(f"{jogador}:{acao}")
                if rect and rect.collidepoint(pos_mouse):
                    self.aguardando = (jogador, acao)
                    return None
        return None

    def capturar_tecla(self, evento, config_jogo):
        if not self.aguardando:
            return False
        if evento.key == pygame.K_ESCAPE:
            self.aguardando = None
            return True
        jogador, acao = self.aguardando
        config_jogo["controles"][jogador]["dispositivo"] = "teclado"
        config_jogo["controles"][jogador][acao] = int(evento.key)
        self.aguardando = None
        self._salvar_config(config_jogo)
        return True

    def capturar_botao_controle(self, evento, config_jogo):
        if not self.aguardando:
            return False
        jogador, acao = self.aguardando
        estado = config_jogo["controles"][jogador]
        estado["dispositivo"] = "controle"
        estado.setdefault("botoes", {})[acao] = int(evento.button)
        self.aguardando = None
        self._salvar_config(config_jogo)
        return True
