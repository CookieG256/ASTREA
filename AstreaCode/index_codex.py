import pygame
from config import (
    LARGURA, BRANCO, CINZA, CINZA_CLARO, AMARELO, VERDE, ROXO_UI, VERMELHO,
    FUNDO_UI, PAINEL_UI, PAINEL_UI_CLARO, BORDA_UI, DOURADO_UI,
    FONTE_SYS, FONTE_GRANDE, RARIDADE_CORES,
)
from banco_itens import TODAS_ARMAS, TODOS_AMULETOS, SETS_ARMADURAS
from save import carregar_dados
from idiomas import (
    t, nome_inimigo_localizado, descricao_inimigo_localizada,
    nome_chefe_localizado, descricao_chefe_localizada,
)
from localized_index_items import traduzir_item_index
from pixel_assets import sprite_item, sprite_inimigo


class TelaIndexCodex:
    CATEGORIAS = (
        ("all", "index_filtro_todos"),
        ("melee", "index_filtro_espadas"),
        ("ranged", "index_filtro_armas_fogo"),
        ("mage", "index_filtro_cajados"),
        ("amulets", "index_filtro_amuletos"),
        ("armor", "index_filtro_armaduras"),
    )

    def __init__(self):
        self.btn_voltar = pygame.Rect(LARGURA // 2 - 100, 545, 200, 38)
        self.scroll_y = 0
        self.max_scroll = 0
        self.filtro = "all"
        self.secao = "itens"
        self.btn_secoes = {
            "itens": pygame.Rect(LARGURA // 2 - 150, 50, 140, 30),
            "inimigos": pygame.Rect(LARGURA // 2 + 10, 50, 140, 30),
        }
        largura_btn = 130
        espacamento = 8
        largura_total = len(self.CATEGORIAS) * largura_btn + (len(self.CATEGORIAS) - 1) * espacamento
        x_inicio = (LARGURA - largura_total) // 2
        self.btn_filtros = {
            chave: pygame.Rect(x_inicio + indice * (largura_btn + espacamento), 90, largura_btn, 30)
            for indice, (chave, _) in enumerate(self.CATEGORIAS)
        }

    def _itens_filtrados(self):
        if self.filtro == "amulets":
            return TODOS_AMULETOS
        if self.filtro == "all":
            return TODAS_ARMAS + TODOS_AMULETOS + self._armaduras()
        if self.filtro == "armor":
            return self._armaduras()
        return [item for item in TODAS_ARMAS if item.get("tipo_arma") == self.filtro]

    @staticmethod
    def _armaduras():
        itens = []
        for conjunto, dados in SETS_ARMADURAS.items():
            for parte in ("Capacete", "Peitoral", "Calça"):
                itens.append({
                    "nome": f"{parte} {conjunto}",
                    "raridade": dados["raridade"],
                    "tipo_equipamento": parte.lower(),
                    "desc": (
                        f"+{dados['hp']} HP, +{dados['def']} defesa. "
                        f"Set completo ({conjunto}): {dados['set_completo']}"
                    ),
                })
        return itens

    @staticmethod
    def _quebrar(texto, largura, max_linhas=2):
        linhas = []
        atual = ""
        for palavra in str(texto).split():
            candidato = f"{atual} {palavra}".strip()
            if atual and FONTE_SYS.size(candidato)[0] > largura:
                linhas.append(atual)
                atual = palavra
            else:
                atual = candidato
        if atual:
            linhas.append(atual)
        if len(linhas) > max_linhas:
            linhas = linhas[:max_linhas]
            while linhas[-1] and FONTE_SYS.size(linhas[-1] + "…")[0] > largura:
                linhas[-1] = linhas[-1][:-1]
            linhas[-1] = linhas[-1].rstrip() + "…"
        return linhas

    def _desenhar_tooltip(self, tela, pos_mouse, nome, desc):
        largura_max = min(440, tela.get_width() - 24)
        linhas = self._quebrar(f"{nome}\n{desc}", largura_max - 20, 1000)
        altura = len(linhas) * 18 + 16
        largura = min(
            largura_max,
            max((FONTE_SYS.size(linha)[0] for linha in linhas), default=0) + 20,
        )
        x = pos_mouse[0] + 14
        y = pos_mouse[1] + 14
        if x + largura > tela.get_width() - 8:
            x = pos_mouse[0] - largura - 14
        if y + altura > tela.get_height() - 8:
            y = pos_mouse[1] - altura - 14
        x = max(8, min(x, tela.get_width() - largura - 8))
        y = max(8, min(y, tela.get_height() - altura - 8))
        pygame.draw.rect(tela, (18, 18, 24), (x, y, largura, altura), border_radius=6)
        pygame.draw.rect(tela, AMARELO, (x, y, largura, altura), 1, border_radius=6)
        for indice, linha in enumerate(linhas):
            texto = FONTE_SYS.render(linha, True, AMARELO if indice == 0 else BRANCO)
            tela.blit(texto, (x + 10, y + 8 + indice * 18))

    @staticmethod
    def _inimigos(lang="PT"):
        from config import BIOMAS_INIMIGOS

        entradas = []
        for bioma_id, papeis in BIOMAS_INIMIGOS.items():
            for tipo in papeis:
                entradas.append({
                    "chave": f"{bioma_id}:{tipo}",
                    "tipo": tipo,
                    "bioma_id": bioma_id,
                    "nome": nome_inimigo_localizado(tipo, bioma_id, lang),
                    "desc": descricao_inimigo_localizada(tipo, lang),
                })
            entradas.append({
                "chave": f"{bioma_id}:raro",
                "tipo": "raro",
                "bioma_id": bioma_id,
                "nome": t("index_raro_nome", lang),
                "desc": t("index_raro_desc", lang),
            })
            entradas.append({
                "chave": f"{bioma_id}:boss",
                "tipo": "boss",
                "bioma_id": bioma_id,
                "nome": nome_chefe_localizado(bioma_id, lang),
                "desc": descricao_chefe_localizada(bioma_id, lang),
                "fases": {3: 2, 6: 2, 8: 3, 10: 3, 11: 2, 12: 2, 13: 2, 14: 2, 15: 3}.get(bioma_id, 1),
            })
        return entradas

    def desenhar(self, tela, pos_mouse, config_jogo):
        tela.fill(FUNDO_UI)
        dados = carregar_dados()
        descobertas = dados.get("index_descobertas", {})
        descobertas = descobertas if isinstance(descobertas, dict) else {}
        itens_vistos = descobertas.get("itens", {})
        inimigos_vistos = descobertas.get("inimigos", {})
        itens_vistos = itens_vistos if isinstance(itens_vistos, dict) else {}
        inimigos_vistos = inimigos_vistos if isinstance(inimigos_vistos, dict) else {}
        lang = config_jogo.get("idioma", "PT")

        titulo = FONTE_GRANDE.render(t("titulo_index", lang), True, AMARELO)
        tela.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 10))
        for chave, rect in self.btn_secoes.items():
            ativa = self.secao == chave
            hover = rect.collidepoint(pos_mouse)
            cor = PAINEL_UI_CLARO if hover else ROXO_UI if ativa else PAINEL_UI
            pygame.draw.rect(tela, cor, rect, border_radius=7)
            pygame.draw.rect(tela, ROXO_UI if ativa or hover else BORDA_UI, rect, 2 if ativa or hover else 1, border_radius=7)
            texto = FONTE_SYS.render(t("index_" + chave, lang), True, DOURADO_UI if ativa or hover else BRANCO)
            tela.blit(texto, (rect.centerx - texto.get_width() // 2, rect.centery - texto.get_height() // 2))

        if self.secao == "itens":
            for chave, chave_texto in self.CATEGORIAS:
                rect = self.btn_filtros[chave]
                selecionado = self.filtro == chave
                hover = rect.collidepoint(pos_mouse)
                cor = PAINEL_UI_CLARO if hover else ROXO_UI if selecionado else PAINEL_UI
                pygame.draw.rect(tela, cor, rect, border_radius=7)
                pygame.draw.rect(tela, ROXO_UI if selecionado or hover else BORDA_UI, rect, 2 if selecionado or hover else 1, border_radius=7)
                texto = FONTE_SYS.render(t(chave_texto, lang), True, DOURADO_UI if selecionado or hover else BRANCO)
                tela.blit(texto, (rect.centerx - texto.get_width() // 2, rect.centery - texto.get_height() // 2))

        if self.secao == "itens":
            entradas = [("item", item) for item in self._itens_filtrados()]
        else:
            entradas = [("inimigo", item) for item in self._inimigos(lang)]

        y_inicio, y_fim = 132, 530
        passo = 62
        self.max_scroll = min(0, y_fim - y_inicio - len(entradas) * passo)
        self.scroll_y = max(self.max_scroll, min(0, self.scroll_y))
        clip_anterior = tela.get_clip()
        tela.set_clip(pygame.Rect(0, y_inicio, LARGURA, y_fim - y_inicio))
        y = y_inicio + self.scroll_y
        tooltip = None

        for tipo_entrada, item in entradas:
            rect = pygame.Rect(LARGURA // 2 - 235, y, 470, 56)
            if rect.colliderect(pygame.Rect(0, y_inicio, LARGURA, y_fim - y_inicio)):
                hovered = rect.collidepoint(pos_mouse)
                pygame.draw.rect(
                    tela,
                    PAINEL_UI_CLARO if rect.collidepoint(pos_mouse) else PAINEL_UI,
                    rect,
                    border_radius=7,
                )
                pygame.draw.rect(tela, BORDA_UI, rect, 1, border_radius=7)
                if tipo_entrada == "item":
                    nome_original = item["nome"]
                    nome, desc = traduzir_item_index(item, lang)
                    desbloqueado = bool(
                        itens_vistos.get(nome_original, descobertas.get(nome_original, False))
                    )
                    raridade = item.get("raridade", "Comum")
                    cor = RARIDADE_CORES.get(raridade, BRANCO)
                    icone = sprite_item(item, 32)
                    tela.blit(icone, (rect.x + 9, rect.y + 12))
                    pygame.draw.rect(tela, cor, pygame.Rect(rect.x + 7, rect.y + 10, 36, 36), 2)
                    nome = nome if desbloqueado else t("index_item_desconhecido", lang)
                    desc = desc if desbloqueado else t("index_encontre_item", lang)
                    cor_nome = cor if desbloqueado else BRANCO
                else:
                    desbloqueado = bool(inimigos_vistos.get(item["chave"], False))
                    nome = item["nome"] if desbloqueado else t("index_inimigo_bloqueado", lang)
                    desc = item["desc"] if desbloqueado else t("index_encontre_inimigo", lang)
                    icone = sprite_inimigo(
                        item["bioma_id"], item["tipo"], (32, 32), item.get("sprite")
                    )
                    tela.blit(icone, (rect.x + 10, rect.y + 12))
                    eh_chefe = item["tipo"] == "boss"
                    cor = VERMELHO if eh_chefe else VERDE if desbloqueado else CINZA
                    cor_nome = cor if desbloqueado or eh_chefe else BRANCO
                    pygame.draw.rect(tela, cor, pygame.Rect(rect.x + 7, rect.y + 10, 36, 36), 2)
                    if eh_chefe:
                        pygame.draw.rect(tela, VERMELHO, rect, 2, border_radius=7)

                titulo_item = FONTE_SYS.render(f"{nome}:", True, cor_nome)
                tela.blit(titulo_item, (rect.x + 52, rect.y + 4))
                descricao_curta = self._quebrar(desc, 405, 1)
                texto_desc = FONTE_SYS.render(
                    descricao_curta[0] if descricao_curta else "",
                    True, BRANCO if desbloqueado else CINZA_CLARO,
                )
                tela.blit(texto_desc, (rect.x + 52, rect.y + 24))
                if tipo_entrada == "inimigo" and item["tipo"] == "boss" and desbloqueado:
                    fases = FONTE_SYS.render(f"{item['fases']} FASES", True, VERMELHO)
                    tela.blit(fases, (rect.right - fases.get_width() - 10, rect.y + 4))
                if hovered and desbloqueado:
                    tooltip = (nome, desc)
            y += passo
        tela.set_clip(clip_anterior)
        if tooltip:
            self._desenhar_tooltip(tela, pos_mouse, *tooltip)

        hover_voltar = self.btn_voltar.collidepoint(pos_mouse)
        cor_voltar = PAINEL_UI_CLARO if hover_voltar else PAINEL_UI
        pygame.draw.rect(tela, cor_voltar, self.btn_voltar, border_radius=8)
        pygame.draw.rect(tela, ROXO_UI if hover_voltar else BORDA_UI, self.btn_voltar, 2 if hover_voltar else 1, border_radius=8)
        texto = FONTE_SYS.render(t("voltar_lobby", lang), True, DOURADO_UI if hover_voltar else BRANCO)
        tela.blit(texto, (self.btn_voltar.centerx - texto.get_width() // 2, self.btn_voltar.centery - texto.get_height() // 2))

    def tratar_evento(self, evento, pos_mouse):
        if evento.type == pygame.MOUSEWHEEL:
            self.scroll_y = max(self.max_scroll, min(0, self.scroll_y + evento.y * 30))
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            for chave, rect in self.btn_secoes.items():
                if rect.collidepoint(pos_mouse):
                    if self.secao != chave:
                        self.secao = chave
                        self.scroll_y = 0
                    return None
            if self.secao == "itens":
                for chave, rect in self.btn_filtros.items():
                    if rect.collidepoint(pos_mouse):
                        if self.filtro != chave:
                            self.filtro = chave
                            self.scroll_y = 0
                        return None
            if self.btn_voltar.collidepoint(pos_mouse):
                return "VOLTAR_LOBBY"
        return None

    def tratar_clique(self, pos_mouse):
        return "VOLTAR_LOBBY" if self.btn_voltar.collidepoint(pos_mouse) else None
