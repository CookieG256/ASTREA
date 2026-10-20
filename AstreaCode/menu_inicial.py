# menu_inicial.py
import pygame
from config import (
    LARGURA, ALTURA, BRANCO, CINZA, CINZA_CLARO, AMARELO, VERDE, VERMELHO, AZUL,
    FUNDO_UI, PAINEL_UI, PAINEL_UI_CLARO, BORDA_UI, DOURADO_UI, CIANO_UI, ROXO_UI,
    FONTE_SYS, FONTE_PEQUENA, FONTE_GRANDE, FONTE_TITULO,
)
from save import (
    carregar_dados,
    salvar_dados,
    perfil_atual,
    selecionar_perfil,
    PERFIS_DISPONIVEIS,
)
from idiomas import t
from loja_pets import LojaPets
from registros_run import obter_melhores_runs_por_dificuldade
from personagens import ARMAS_INICIAIS, RACES_AND_CLASSES, STAT_LABELS, stats_selecao
from cosmeticos import COSMETICOS, COSMETICO_PADRAO, desbloquear_cosmetico
from version import VERSION
from modificadores import (
    MODIFICADORES_RUN,
    ROTULOS_EFEITOS_MODIFICADORES,
    obter_efeitos_modificadores,
)

RACA_LABELS = {
    "Humano": "raca_humano", "Elfo": "raca_elfo", "Anão": "raca_anao",
    "Ciborgue": "raca_ciborgue", "Robô": "raca_robo", "Demônio": "raca_demonio",
}
CLASSE_LABELS = {
    "Guerreiro": "classe_guerreiro", "Espadachim": "classe_espadachim",
    "Mago": "classe_mago", "Atirador": "classe_atirador",
    "Caçador": "classe_cacador", "Ladrão": "classe_ladrao",
}


def draw_icon_button(surface, rect, color, icon_text_or_image, hover_state, tooltip="", font=None):
    sombra = rect.move(0, 3)
    pygame.draw.rect(surface, (4, 5, 12), sombra, border_radius=9)
    pygame.draw.rect(
        surface,
        tuple(min(255, canal + (24 if hover_state else 0)) for canal in color),
        rect,
        border_radius=9,
    )
    pygame.draw.rect(surface, BRANCO if hover_state else BORDA_UI, rect, 2 if hover_state else 1, border_radius=9)
    if hasattr(icon_text_or_image, "get_size"):
        imagem = icon_text_or_image
        surface.blit(imagem, (rect.centerx - imagem.get_width() // 2, rect.centery - imagem.get_height() // 2))
    else:
        fonte = font or FONTE_GRANDE
        icone = fonte.render(str(icon_text_or_image), True, BRANCO)
        surface.blit(icone, (rect.centerx - icone.get_width() // 2, rect.centery - icone.get_height() // 2))
    if hover_state and tooltip:
        fonte_tooltip = FONTE_PEQUENA
        texto = fonte_tooltip.render(tooltip, True, BRANCO)
        caixa = pygame.Rect(0, 0, texto.get_width() + 16, texto.get_height() + 10)
        caixa.centerx = rect.centerx
        caixa.bottom = rect.top - 6
        caixa.clamp_ip(surface.get_rect())
        pygame.draw.rect(surface, PAINEL_UI, caixa, border_radius=5)
        pygame.draw.rect(surface, BORDA_UI, caixa, 1, border_radius=5)
        surface.blit(texto, (caixa.centerx - texto.get_width() // 2, caixa.centery - texto.get_height() // 2))

UPGRADES_CONFIG = {
    "hp_max": {"chave_nome": "up_hp_max", "max": 15, "custo_base": 10, "fator": 5},
    "mana_max": {"chave_nome": "up_mana_max", "max": 15, "custo_base": 10, "fator": 5},
    "defesa": {"chave_nome": "up_defesa", "max": 15, "custo_base": 12, "fator": 6},
    "dano": {"chave_nome": "up_dano", "max": 15, "custo_base": 15, "fator": 7},
    "crit": {"chave_nome": "up_crit", "max": 15, "custo_base": 15, "fator": 8},
    "dano_crit": {"chave_nome": "up_dano_crit", "max": 15, "custo_base": 12, "fator": 6},
    "velocidade": {"chave_nome": "up_velocidade", "max": 15, "custo_base": 10, "fator": 5},
    "esquiva": {"chave_nome": "up_esquiva", "max": 15, "custo_base": 15, "fator": 8},
    "drop_ouro": {"chave_nome": "up_drop_ouro", "max": 15, "custo_base": 10, "fator": 4},
    "menos_cd": {"chave_nome": "up_menos_cd", "max": 5, "custo_base": 30, "fator": 20}
}

class MenuInicial:
    def __init__(self):
        self.btn_jogar = pygame.Rect(LARGURA // 2 - 145, 185, 290, 52)
        self.btn_cosmeticos = pygame.Rect(LARGURA // 2 - 145, 245, 290, 44)
        self.btn_personagem = pygame.Rect(LARGURA // 2 - 145, 297, 290, 44)
        self.btn_sair = pygame.Rect(LARGURA // 2 - 145, 349, 290, 44)
        self.btn_discord = pygame.Rect(LARGURA - 210, ALTURA - 48, 196, 34)
        self.icon_buttons = {
            "config": (pygame.Rect(LARGURA - 58, ALTURA // 2 - 153, 42, 42), (80, 80, 90), "⚙", "config"),
            "index": (pygame.Rect(LARGURA - 58, ALTURA // 2 - 102, 42, 42), (230, 126, 34), "▤", "index"),
            "loja": (pygame.Rect(LARGURA - 58, ALTURA // 2 - 51, 42, 42), (26, 188, 156), "▣", "loja"),
            "conquistas": (pygame.Rect(LARGURA - 58, ALTURA // 2, 42, 42), (185, 145, 54), "★", "conquistas"),
            "missoes_titulo": (pygame.Rect(LARGURA - 58, ALTURA // 2 + 51, 42, 42), ROXO_UI, "≡", "missoes_titulo"),
            "historia": (pygame.Rect(LARGURA - 58, ALTURA // 2 + 102, 42, 42), ROXO_UI, "✧", "historia_titulo"),
            "npcs": (pygame.Rect(LARGURA - 58, ALTURA // 2 + 153, 42, 42), (37, 130, 122), "♟", "npcs_resgatados_titulo"),
        }
        self.selecao_personagem = False
        self.tela_modificadores = False
        self.tela_cosmeticos = False
        self.tela_perfis = False
        self.btn_perfil = pygame.Rect(14, 18, 176, 34)
        self.btn_voltar_perfis = pygame.Rect(LARGURA // 2 - 110, 466, 220, 38)
        self.rects_perfis = {}
        self.cosmetico_slot = "P1"
        self.rects_cosmeticos = {}
        self.btn_cosmetico_p1 = pygame.Rect(LARGURA // 2 - 155, 175, 145, 36)
        self.btn_cosmetico_p2 = pygame.Rect(LARGURA // 2 + 10, 175, 145, 36)
        self.btn_voltar_cosmeticos = pygame.Rect(LARGURA // 2 - 110, ALTURA - 58, 220, 38)
        self.modificadores_run = set()
        self.btn_mod_vidro = pygame.Rect(LARGURA // 2 - 225, 445, 215, 34)
        self.btn_mod_horda = pygame.Rect(LARGURA // 2 + 10, 445, 215, 34)
        self.rects_racas = {}
        self.rects_classes = {}
        self.btn_confirmar_personagem = pygame.Rect(LARGURA // 2 - 120, 535, 240, 42)

        self.sub_modo = False
        self.btn_easy = pygame.Rect(LARGURA//2 - 120, 190, 240, 40)
        self.btn_normal = pygame.Rect(LARGURA//2 - 120, 240, 240, 40)
        self.btn_hard = pygame.Rect(LARGURA//2 - 120, 290, 240, 40)
        self.btn_hardcore = pygame.Rect(LARGURA//2 - 120, 340, 240, 40)
        self.btn_abrir_modificadores = pygame.Rect(LARGURA // 2 - 120, 390, 240, 38)
        self.btn_voltar_modo = pygame.Rect(LARGURA//2 - 120, 438, 240, 35)

        self.tela_loja = False
        self.aba_loja = "UPGRADES"
        self.btn_aba_upgrades = pygame.Rect(LARGURA//2 - 220, 65, 210, 36)
        self.btn_aba_pets = pygame.Rect(LARGURA//2 + 10, 65, 210, 36)
        self.btn_voltar_loja = pygame.Rect(LARGURA//2 - 100, 535, 200, 40)
        self.loja_pets = LojaPets()
        self.rects_upgrades = {}
        self.rects_modificadores = {}
        self.btn_voltar_modificadores = pygame.Rect(LARGURA // 2 - 120, ALTURA - 48, 240, 36)
        self._melhores_runs = {}
        self._ultima_atualizacao_runs = -1000

    def desenhar(self, tela, pos_mouse, gemas, config_jogo):
        tela.fill(FUNDO_UI)
        for faixa in range(24):
            cor_faixa = (
                FUNDO_UI[0] + faixa // 4,
                FUNDO_UI[1] + faixa // 5,
                FUNDO_UI[2] + faixa,
            )
            pygame.draw.rect(
                tela, cor_faixa,
                (0, faixa * ALTURA // 24, LARGURA, ALTURA // 24 + 1),
            )
        for indice in range(9):
            x = 45 + indice * 103
            y = 90 + (indice * 67) % 420
            pygame.draw.circle(tela, (48, 57, 82), (x, y), 2)
            pygame.draw.circle(tela, (38, 47, 70), (LARGURA - x, ALTURA - y), 1)
        pygame.draw.circle(tela, (33, 39, 63), (LARGURA // 2, 165), 105, 1)
        pygame.draw.circle(tela, (33, 39, 63), (LARGURA // 2, 165), 88, 1)
        dados = carregar_dados()
        lang = config_jogo.get('idioma', 'PT')

        rect_gemas = pygame.Rect(LARGURA - 286, 18, 170, 36)
        pygame.draw.rect(tela, PAINEL_UI, rect_gemas, border_radius=18)
        pygame.draw.rect(tela, BORDA_UI, rect_gemas, 1, border_radius=18)
        txt_gemas = FONTE_SYS.render(f"✦ {t('gemas', lang)}: {gemas}", True, CIANO_UI)
        tela.blit(txt_gemas, (rect_gemas.centerx - txt_gemas.get_width() // 2, rect_gemas.centery - txt_gemas.get_height() // 2))

        if not self.tela_loja:
            txt_t = FONTE_TITULO.render(t("titulo_jogo", lang), True, ROXO_UI)
            txt_t = pygame.transform.smoothscale(txt_t, (int(txt_t.get_width() * 1.25), int(txt_t.get_height() * 1.25)))
            halo = FONTE_TITULO.render(t("titulo_jogo", lang), True, (72, 48, 125))
            halo = pygame.transform.smoothscale(halo, (txt_t.get_width(), txt_t.get_height()))
            tela.blit(halo, (LARGURA//2 - halo.get_width()//2 + 2, 31))
            tela.blit(txt_t, (LARGURA//2 - txt_t.get_width()//2, 28))
            for indice in range(42):
                x = (indice * 197 + 43) % LARGURA
                y = (indice * 113 + 21) % ALTURA
                pygame.draw.circle(tela, (82, 70, 123) if indice % 4 else (150, 126, 220), (x, y), 1)
            pygame.draw.ellipse(tela, (47, 37, 78), pygame.Rect(210, 58, 480, 82), 1)
            pygame.draw.ellipse(tela, (34, 29, 60), pygame.Rect(245, 72, 410, 55), 1)
            pygame.draw.line(tela, BORDA_UI, (LARGURA // 2 - 105, 132), (LARGURA // 2 + 105, 132), 1)

            painel_recordes = pygame.Rect(14, ALTURA - 130, 255, 94)
            pygame.draw.rect(tela, PAINEL_UI, painel_recordes, border_radius=8)
            pygame.draw.rect(tela, BORDA_UI, painel_recordes, 1, border_radius=8)
            titulo_recordes = FONTE_PEQUENA.render(t("melhores_runs", lang), True, DOURADO_UI)
            tela.blit(titulo_recordes, (painel_recordes.x + 8, painel_recordes.y + 4))
            agora = pygame.time.get_ticks()
            if agora - self._ultima_atualizacao_runs >= 1000:
                self._melhores_runs = obter_melhores_runs_por_dificuldade()
                self._ultima_atualizacao_runs = agora
            for indice, (modo, registro) in enumerate(self._melhores_runs.items()):
                if registro:
                    resumo = t("registro_run_curto", lang).format(
                        andar=registro.get("andar", 1),
                        gemas=registro.get("gemas", 0),
                    )
                else:
                    resumo = t("sem_registro", lang)
                linha = FONTE_PEQUENA.render(
                    f"{t('dificuldade_' + modo.lower(), lang)}: {resumo}",
                    True, BRANCO,
                )
                tela.blit(linha, (painel_recordes.x + 8, painel_recordes.y + 22 + indice * 16))

            if not (self.tela_modificadores or self.selecao_personagem or self.tela_cosmeticos or self.tela_perfis or self.sub_modo):
                versao = FONTE_PEQUENA.render(f"ASTREA {VERSION}", True, CINZA_CLARO)
                tela.blit(versao, (14, ALTURA - versao.get_height() - 4))
                self._desenhar_botao_principal(
                    tela,
                    self.btn_discord,
                    "Discord",
                    (88, 101, 242),
                    pos_mouse,
                )

            if not (self.tela_modificadores or self.selecao_personagem or self.tela_cosmeticos or self.tela_perfis or self.sub_modo):
                for chave, (rect, cor, icone, chave_tooltip) in self.icon_buttons.items():
                    draw_icon_button(tela, rect, cor, icone, rect.collidepoint(pos_mouse), t(chave_tooltip, lang))

            if self.tela_perfis:
                titulo_perfis = FONTE_TITULO.render(t("perfis_titulo", lang), True, ROXO_UI)
                tela.blit(titulo_perfis, (LARGURA // 2 - titulo_perfis.get_width() // 2, 145))
                self.rects_perfis = {}
                for indice, perfil in enumerate(PERFIS_DISPONIVEIS):
                    rect = pygame.Rect(LARGURA // 2 - 150, 210 + indice * 58, 300, 46)
                    self.rects_perfis[perfil] = rect
                    ativo = perfil == perfil_atual()
                    hover = rect.collidepoint(pos_mouse)
                    pygame.draw.rect(tela, PAINEL_UI_CLARO if hover or ativo else PAINEL_UI, rect, border_radius=8)
                    pygame.draw.rect(tela, CIANO_UI if ativo else BORDA_UI, rect, 2 if ativo else 1, border_radius=8)
                    texto = FONTE_SYS.render(
                        f"{t('perfil_local', lang)} {indice + 1}" + (f"  ·  {t('perfil_ativo', lang)}" if ativo else ""),
                        True, BRANCO,
                    )
                    tela.blit(texto, (rect.centerx - texto.get_width() // 2, rect.centery - texto.get_height() // 2))
                self._desenhar_botao_principal(
                    tela, self.btn_voltar_perfis, t("voltar", lang), ROXO_UI, pos_mouse
                )
            if self.tela_modificadores:
                self._desenhar_modificadores(tela, pos_mouse, lang, config_jogo)
            elif self.selecao_personagem:
                self._desenhar_selecao_personagem(tela, pos_mouse, config_jogo, lang)
            elif self.tela_cosmeticos:
                self._desenhar_cosmeticos(tela, pos_mouse, lang)
            elif not self.sub_modo and not self.tela_perfis:
                self._desenhar_botao_principal(
                    tela, self.btn_perfil, f"{t('perfil_local', lang)} {perfil_atual()[-1]}",
                    ROXO_UI, pos_mouse,
                )
                self._desenhar_botao_principal(tela, self.btn_jogar, t("jogar", lang), CIANO_UI, pos_mouse, True)
                self._desenhar_botao_principal(
                    tela, self.btn_cosmeticos, t("cosmeticos_titulo", lang), (180, 105, 225), pos_mouse
                )
                self._desenhar_botao_principal(
                    tela,
                    self.btn_personagem,
                    t("selecionar_personagem", lang),
                    ROXO_UI,
                    pos_mouse,
                )
                self._desenhar_botao_principal(
                    tela, self.btn_sair, t("sair", lang), (192, 57, 43), pos_mouse
                )
            elif self.sub_modo:
                for btn, chave_txt, cor_base in [
                    (self.btn_easy, "dificuldade_easy", VERDE),
                    (self.btn_normal, "dificuldade_normal", AZUL),
                    (self.btn_hard, "dificuldade_hard", AMARELO),
                    (self.btn_hardcore, "dificuldade_hardcore", VERMELHO),
                ]:
                    hovered = btn.collidepoint(pos_mouse)
                    cor = PAINEL_UI_CLARO if hovered else PAINEL_UI
                    pygame.draw.rect(tela, (4, 6, 13), btn.move(0, 3), border_radius=8)
                    pygame.draw.rect(tela, cor, btn, border_radius=8)
                    pygame.draw.rect(tela, cor_base, btn, 2 if hovered else 1, border_radius=8)
                    txt = FONTE_SYS.render(t(chave_txt, lang), True, DOURADO_UI if hovered else BRANCO)
                    tela.blit(txt, (btn.centerx - txt.get_width()//2, btn.centery - txt.get_height()//2))
                self._desenhar_botao_principal(
                    tela, self.btn_abrir_modificadores,
                    t("modificador_titulo", lang), ROXO_UI, pos_mouse,
                )
                self._desenhar_botao_principal(
                    tela, self.btn_voltar_modo, t("voltar", lang), CINZA, pos_mouse
                )
        else:
            txt_l = FONTE_GRANDE.render(t("loja_upgrades", lang), True, CIANO_UI)
            tela.blit(txt_l, (LARGURA//2 - txt_l.get_width()//2, 20))
            for rect, chave, aba in (
                (self.btn_aba_upgrades, "aba_upgrades", "UPGRADES"),
                (self.btn_aba_pets, "aba_pets", "PETS"),
            ):
                ativa = self.aba_loja == aba
                hovered = rect.collidepoint(pos_mouse)
                cor = PAINEL_UI_CLARO if hovered or ativa else PAINEL_UI
                pygame.draw.rect(tela, cor, rect, border_radius=8)
                pygame.draw.rect(tela, ROXO_UI if ativa else BORDA_UI, rect, 2 if ativa else 1, border_radius=8)
                texto = FONTE_SYS.render(t(chave, lang), True, DOURADO_UI if ativa or hovered else BRANCO)
                tela.blit(texto, (rect.centerx - texto.get_width() // 2, rect.centery - texto.get_height() // 2))

            if self.aba_loja == "UPGRADES":
                ups_salvos = dados.get('upgrades_nivel', {})
                y_p = 112
                self.rects_upgrades = {}

                for chave, cfg in UPGRADES_CONFIG.items():
                    lvl_atual = ups_salvos.get(chave, 0)
                    max_l = cfg['max']
                    custo = cfg['custo_base'] + (lvl_atual * cfg['fator'])
                    nome_up = t(cfg['chave_nome'], lang)

                    txt_st = f"MAX (Lvl {max_l})" if lvl_atual >= max_l else f"Lvl {lvl_atual}/{max_l} - {t('gemas', lang)}: {custo}"
                    rect_b = pygame.Rect(LARGURA//2 - 240, y_p, 480, 36)
                    self.rects_upgrades[chave] = (rect_b, custo, lvl_atual >= max_l)

                    hovered = rect_b.collidepoint(pos_mouse)
                    cor = PAINEL_UI_CLARO if hovered else PAINEL_UI
                    pygame.draw.rect(tela, cor, rect_b, border_radius=8)
                    pygame.draw.rect(tela, DOURADO_UI if hovered else BORDA_UI, rect_b, 1, border_radius=8)

                    txt_u = FONTE_SYS.render(f"{nome_up}: {txt_st}", True, DOURADO_UI if hovered else BRANCO)
                    tela.blit(txt_u, (rect_b.centerx - txt_u.get_width()//2, rect_b.centery - txt_u.get_height()//2))
                    y_p += 44
            else:
                self.rects_upgrades = {}
                self.loja_pets.desenhar(tela, dados, pos_mouse, lang)

            hovered = self.btn_voltar_loja.collidepoint(pos_mouse)
            cor_v = PAINEL_UI_CLARO if hovered else PAINEL_UI
            pygame.draw.rect(tela, cor_v, self.btn_voltar_loja, border_radius=8)
            pygame.draw.rect(tela, DOURADO_UI if hovered else BORDA_UI, self.btn_voltar_loja, 1, border_radius=8)
            txt_v = FONTE_SYS.render(t("voltar_menu", lang), True, DOURADO_UI if hovered else BRANCO)
            tela.blit(txt_v, (self.btn_voltar_loja.centerx - txt_v.get_width()//2, self.btn_voltar_loja.centery - txt_v.get_height()//2))

    @staticmethod
    def _desenhar_botao_principal(tela, rect, texto, cor, pos_mouse, destaque=False):
        hover = rect.collidepoint(pos_mouse)
        pygame.draw.rect(tela, (4, 5, 12), rect.move(0, 4), border_radius=13)
        pygame.draw.rect(tela, PAINEL_UI_CLARO if hover else PAINEL_UI, rect, border_radius=13)
        pygame.draw.rect(tela, cor, rect, 3 if hover or destaque else 2, border_radius=13)
        if hover or destaque:
            pygame.draw.rect(tela, cor, rect.inflate(8, 8), 1, border_radius=15)
        label = FONTE_GRANDE if destaque else FONTE_SYS
        texto_render = label.render(texto, True, BRANCO)
        tela.blit(texto_render, (rect.centerx - texto_render.get_width() // 2, rect.centery - texto_render.get_height() // 2))

    def _desenhar_selecao_personagem(self, tela, pos_mouse, config_jogo, lang):
        painel = pygame.Rect(80, 155, LARGURA - 160, 360)
        pygame.draw.rect(tela, PAINEL_UI, painel, border_radius=14)
        pygame.draw.rect(tela, BORDA_UI, painel, 1, border_radius=14)
        stats_hover = None
        for chave, titulo, opcoes, destino, selecionada in (
            ("races", t("personagem_racas", lang), RACES_AND_CLASSES["races"], self.rects_racas, "raca_jogador"),
            ("classes", t("personagem_classes", lang), RACES_AND_CLASSES["classes"], self.rects_classes, "classe_jogador"),
        ):
            titulo_render = FONTE_GRANDE.render(titulo, True, CIANO_UI if chave == "races" else ROXO_UI)
            x_base = 120 if chave == "races" else LARGURA // 2 + 20
            tela.blit(titulo_render, (x_base, 170))
            destino.clear()
            nomes = list(opcoes)
            for indice, nome in enumerate(nomes):
                coluna, linha = indice % 2, indice // 2
                rect = pygame.Rect(x_base + coluna * 165, 220 + linha * 66, 155, 54)
                destino[nome] = rect
                ativo = config_jogo.get(selecionada, "Humano" if chave == "races" else "Guerreiro") == nome
                hover = rect.collidepoint(pos_mouse)
                pygame.draw.rect(tela, PAINEL_UI_CLARO if hover or ativo else FUNDO_UI, rect, border_radius=8)
                pygame.draw.rect(tela, CIANO_UI if ativo else BORDA_UI, rect, 2 if ativo else 1, border_radius=8)
                icone = FONTE_GRANDE.render(opcoes[nome]["icon"], True, DOURADO_UI if ativo else BRANCO)
                chave_label = RACA_LABELS.get(nome) if chave == "races" else CLASSE_LABELS.get(nome)
                label = FONTE_SYS.render(t(chave_label, lang) if chave_label else nome, True, BRANCO)
                tela.blit(icone, (rect.x + 10, rect.centery - icone.get_height() // 2))
                tela.blit(label, (rect.x + 47, rect.centery - label.get_height() // 2))
                if hover:
                    stats_hover = opcoes[nome]["stats"]

        raca = config_jogo.get("raca_jogador", "Humano")
        classe = config_jogo.get("classe_jogador", "Guerreiro")
        stats = stats_selecao(raca, classe)
        linhas = (
            f"{t(RACA_LABELS.get(raca, 'raca_humano'), lang)} {RACES_AND_CLASSES['races'].get(raca, RACES_AND_CLASSES['races']['Humano'])['icon']}  ·  "
            f"{t(CLASSE_LABELS.get(classe, 'classe_guerreiro'), lang)} {RACES_AND_CLASSES['classes'].get(classe, RACES_AND_CLASSES['classes']['Guerreiro'])['icon']}",
            "  ".join(f"{STAT_LABELS[chave]} ×{valor:.2f}" for chave, valor in stats.items()),
            f"{t('arma_inicial', lang)}: {ARMAS_INICIAIS.get(classe, ARMAS_INICIAIS['Guerreiro'])}",
        )
        for indice, texto in enumerate(linhas):
            render = FONTE_PEQUENA.render(texto, True, DOURADO_UI if indice == 0 else BRANCO)
            tela.blit(render, (LARGURA // 2 - render.get_width() // 2, 424 + indice * 24))
        self._desenhar_botao_principal(
            tela, self.btn_confirmar_personagem, t("confirmar_personagem", lang), CIANO_UI, pos_mouse
        )
        if stats_hover:
            self._desenhar_tooltip_stats(tela, pos_mouse, stats_hover, lang)

    @staticmethod
    def _desenhar_tooltip_stats(tela, pos_mouse, stats, lang):
        linhas = [
            f"{t('stat_' + chave, lang)} ×{valor:.2f}"
            for chave, valor in stats.items()
        ]
        largura = max(FONTE_PEQUENA.size(linha)[0] for linha in linhas) + 18
        altura = len(linhas) * 19 + 12
        caixa = pygame.Rect(pos_mouse[0] + 14, pos_mouse[1] + 12, largura, altura)
        caixa.clamp_ip(tela.get_rect())
        pygame.draw.rect(tela, PAINEL_UI, caixa, border_radius=6)
        pygame.draw.rect(tela, DOURADO_UI, caixa, 1, border_radius=6)
        for indice, linha in enumerate(linhas):
            label = FONTE_PEQUENA.render(linha, True, BRANCO)
            tela.blit(label, (caixa.x + 9, caixa.y + 6 + indice * 19))

    def _desenhar_modificadores(self, tela, pos_mouse, lang, config_jogo):
        titulo = FONTE_TITULO.render(t("modificador_titulo", lang), True, ROXO_UI)
        tela.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 85))
        instrucao = FONTE_PEQUENA.render(t("modificador_instrucao", lang), True, BRANCO)
        tela.blit(instrucao, (LARGURA // 2 - instrucao.get_width() // 2, 140))
        selecionados = set(config_jogo.get("modificadores_run", []))
        self.rects_modificadores = {}
        margem = 22
        largura = (LARGURA - margem * 4) // 3
        altura = 132
        for indice, (chave, dados) in enumerate(MODIFICADORES_RUN.items()):
            coluna, linha = indice % 3, indice // 3
            rect = pygame.Rect(
                margem + coluna * (largura + margem),
                176 + linha * 151,
                largura,
                altura,
            )
            self.rects_modificadores[chave] = rect
            ativo = chave in selecionados
            hover = rect.collidepoint(pos_mouse)
            pygame.draw.rect(
                tela, PAINEL_UI_CLARO if hover or ativo else PAINEL_UI,
                rect, border_radius=10,
            )
            pygame.draw.rect(
                tela, CIANO_UI if ativo else (ROXO_UI if hover else BORDA_UI),
                rect, 2 if ativo else 1, border_radius=10,
            )
            nome = FONTE_SYS.render(t(dados["nome"], lang), True, DOURADO_UI if ativo else BRANCO)
            tela.blit(nome, (rect.x + 12, rect.y + 12))
            selo = FONTE_PEQUENA.render(
                t("modificador_ativo" if ativo else "modificador_inativo", lang),
                True, CIANO_UI if ativo else CINZA_CLARO,
            )
            tela.blit(selo, (rect.right - selo.get_width() - 12, rect.y + 14))
            self._desenhar_texto_quebrado(
                tela, t(dados["descricao"], lang), rect.x + 12, rect.y + 43,
                rect.width - 24, rect.height - 48,
            )
        resumo_rect = pygame.Rect(22, 466, LARGURA - 44, 76)
        pygame.draw.rect(tela, PAINEL_UI, resumo_rect, border_radius=8)
        pygame.draw.rect(tela, BORDA_UI, resumo_rect, 1, border_radius=8)
        titulo_resumo = FONTE_PEQUENA.render(
            t("modificador_resumo", lang), True, DOURADO_UI
        )
        tela.blit(titulo_resumo, (resumo_rect.x + 12, resumo_rect.y + 7))
        efeitos = obter_efeitos_modificadores(selecionados)
        linhas_efeitos = []
        if not selecionados:
            linhas_efeitos.append(t("modificador_sem_ativos", lang))
        else:
            for chave, rotulo in ROTULOS_EFEITOS_MODIFICADORES.items():
                valor = efeitos[chave]
                if chave == "chance_elite":
                    if valor:
                        linhas_efeitos.append(
                            f"{t(rotulo, lang)} +{valor * 100:.0f}%"
                        )
                elif valor != 1.0:
                    numero = f"{valor:.2f}"
                    if lang in ("PT", "ES"):
                        numero = numero.replace(".", ",")
                    linhas_efeitos.append(f"{t(rotulo, lang)} ×{numero}")
        self._desenhar_texto_quebrado(
            tela, "  ·  ".join(linhas_efeitos),
            resumo_rect.x + 12, resumo_rect.y + 29,
            resumo_rect.width - 24, resumo_rect.height - 34,
        )
        self._desenhar_botao_principal(
            tela, self.btn_voltar_modificadores, t("voltar", lang), ROXO_UI, pos_mouse
        )

    @staticmethod
    def _desenhar_texto_quebrado(tela, texto, x, y, largura, altura):
        palavras = texto.split()
        linhas = []
        linha = ""
        for palavra in palavras:
            tentativa = f"{linha} {palavra}".strip()
            if FONTE_PEQUENA.size(tentativa)[0] <= largura:
                linha = tentativa
            else:
                if linha:
                    linhas.append(linha)
                linha = palavra
        if linha:
            linhas.append(linha)
        max_linhas = max(1, altura // 17)
        for indice, texto_linha in enumerate(linhas[:max_linhas]):
            render = FONTE_PEQUENA.render(texto_linha, True, BRANCO)
            tela.blit(render, (x, y + indice * 17))

    def _desenhar_cosmeticos(self, tela, pos_mouse, lang):
        dados = carregar_dados()
        desbloqueados = set(dados.get("cosmeticos_desbloqueados", []))
        desbloqueados.add(COSMETICO_PADRAO)
        equipados = dados.get("cosmeticos_equipados", {})
        equipado = equipados.get(self.cosmetico_slot, COSMETICO_PADRAO) if isinstance(equipados, dict) else COSMETICO_PADRAO
        titulo = FONTE_TITULO.render(t("cosmeticos_titulo", lang), True, ROXO_UI)
        tela.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 115))
        for slot, rect, chave in (
            ("P1", self.btn_cosmetico_p1, "jogador_1"),
            ("P2", self.btn_cosmetico_p2, "jogador_2"),
        ):
            ativo = self.cosmetico_slot == slot
            hover = rect.collidepoint(pos_mouse)
            pygame.draw.rect(tela, PAINEL_UI_CLARO if hover or ativo else PAINEL_UI, rect, border_radius=7)
            pygame.draw.rect(tela, CIANO_UI if ativo else BORDA_UI, rect, 2 if ativo else 1, border_radius=7)
            texto = FONTE_SYS.render(t(chave, lang), True, BRANCO)
            tela.blit(texto, (rect.centerx - texto.get_width() // 2, rect.centery - texto.get_height() // 2))

        self.rects_cosmeticos = {}
        for indice, (cosmetico_id, item) in enumerate(COSMETICOS.items()):
            coluna, linha = indice % 2, indice // 2
            rect = pygame.Rect(LARGURA // 2 - 225 + coluna * 235, 226 + linha * 78, 220, 68)
            self.rects_cosmeticos[cosmetico_id] = rect
            adquirido = cosmetico_id in desbloqueados
            ativo = cosmetico_id == equipado and adquirido
            hover = rect.collidepoint(pos_mouse)
            cor_fundo = PAINEL_UI_CLARO if hover or ativo else PAINEL_UI
            pygame.draw.rect(tela, cor_fundo, rect, border_radius=9)
            pygame.draw.rect(tela, item["cor"] if adquirido else BORDA_UI, rect, 2 if ativo or hover else 1, border_radius=9)
            pygame.draw.circle(tela, item["cor"] if adquirido else CINZA, (rect.x + 24, rect.centery), 9)
            nome = item["nome"].get(lang, item["nome"]["PT"])
            status = t("equipado", lang) if ativo else t("cosmetico_adquirido", lang) if adquirido else t("cosmetico_bloqueado", lang)
            label = FONTE_SYS.render(nome, True, BRANCO if adquirido else CINZA_CLARO)
            tela.blit(label, (rect.x + 42, rect.y + 5))
            bonus = item["bonus"]
            if bonus:
                if "multiplicador_gemas" in bonus:
                    texto_bonus = t("cosmetico_buff_gemas", lang).format(valor=round((bonus["multiplicador_gemas"] - 1) * 100))
                elif "multiplicador_dano_cosmetico" in bonus:
                    texto_bonus = t("cosmetico_buff_dano", lang).format(valor=round((bonus["multiplicador_dano_cosmetico"] - 1) * 100))
                elif "hp_max" in bonus:
                    texto_bonus = t("cosmetico_buff_vida", lang).format(valor=round((bonus["hp_max"] - 1) * 100))
                else:
                    texto_bonus = t("cosmetico_buff_dash", lang).format(valor=round((1 - bonus["dash_cooldown"]) * 100))
            else:
                texto_bonus = t("cosmetico_visual", lang)
            status_render = FONTE_PEQUENA.render(status, True, DOURADO_UI if ativo else CINZA_CLARO)
            descricao = FONTE_PEQUENA.render(texto_bonus, True, CIANO_UI)
            tela.blit(status_render, (rect.x + 42, rect.y + 27))
            tela.blit(descricao, (rect.x + 42, rect.y + 46))
        hover = self.btn_voltar_cosmeticos.collidepoint(pos_mouse)
        pygame.draw.rect(tela, PAINEL_UI_CLARO if hover else PAINEL_UI, self.btn_voltar_cosmeticos, border_radius=8)
        pygame.draw.rect(tela, ROXO_UI if hover else BORDA_UI, self.btn_voltar_cosmeticos, 1, border_radius=8)
        voltar = FONTE_SYS.render(t("voltar", lang), True, BRANCO)
        tela.blit(voltar, (self.btn_voltar_cosmeticos.centerx - voltar.get_width() // 2, self.btn_voltar_cosmeticos.centery - voltar.get_height() // 2))

    def tratar_clique(self, pos_mouse, config_jogo):
        dados = carregar_dados()
        gemas = dados.get('gemas', 0)

        if 'upgrades_nivel' not in dados:
            dados['upgrades_nivel'] = {}

        if not self.tela_loja:
            if self.tela_modificadores:
                if self.btn_voltar_modificadores.collidepoint(pos_mouse):
                    self.tela_modificadores = False
                else:
                    for modificador, rect in self.rects_modificadores.items():
                        if rect.collidepoint(pos_mouse):
                            selecionados = set(config_jogo.get("modificadores_run", []))
                            if modificador in selecionados:
                                selecionados.remove(modificador)
                            else:
                                selecionados.add(modificador)
                            selecionados_ordenados = sorted(selecionados)
                            config_jogo["modificadores_run"] = selecionados_ordenados
                            dados.setdefault("configuracoes", {})[
                                "modificadores_run"
                            ] = selecionados_ordenados
                            salvar_dados(dados)
                            self.modificadores_run = selecionados
                            break
            elif self.selecao_personagem:
                alterou_selecao = False
                if self.btn_confirmar_personagem.collidepoint(pos_mouse):
                    self.selecao_personagem = False
                else:
                    for nome, rect in self.rects_racas.items():
                        if rect.collidepoint(pos_mouse):
                            config_jogo["raca_jogador"] = nome
                            alterou_selecao = True
                            break
                    for nome, rect in self.rects_classes.items():
                        if rect.collidepoint(pos_mouse):
                            config_jogo["classe_jogador"] = nome
                            alterou_selecao = True
                            break
                if alterou_selecao:
                    configuracoes_salvas = dados.setdefault("configuracoes", {})
                    configuracoes_salvas["raca_jogador"] = config_jogo["raca_jogador"]
                    configuracoes_salvas["classe_jogador"] = config_jogo["classe_jogador"]
                    salvar_dados(dados)
            elif self.tela_cosmeticos:
                if self.btn_voltar_cosmeticos.collidepoint(pos_mouse):
                    self.tela_cosmeticos = False
                elif self.btn_cosmetico_p1.collidepoint(pos_mouse):
                    self.cosmetico_slot = "P1"
                elif self.btn_cosmetico_p2.collidepoint(pos_mouse):
                    self.cosmetico_slot = "P2"
                else:
                    unlocked = set(dados.setdefault("cosmeticos_desbloqueados", []))
                    unlocked.add(COSMETICO_PADRAO)
                    desbloquear_cosmetico(dados, COSMETICO_PADRAO)
                    for cosmetico_id, rect in self.rects_cosmeticos.items():
                        if rect.collidepoint(pos_mouse) and cosmetico_id in unlocked:
                            equipados = dados.setdefault("cosmeticos_equipados", {})
                            equipados[self.cosmetico_slot] = cosmetico_id
                            if self.cosmetico_slot == "P1":
                                dados["cosmetico_equipado"] = cosmetico_id
                            config_jogo["cosmeticos_equipados"] = equipados.copy()
                            salvar_dados(dados)
                            break
            elif self.tela_perfis:
                if self.btn_voltar_perfis.collidepoint(pos_mouse):
                    self.tela_perfis = False
                else:
                    for perfil, rect in self.rects_perfis.items():
                        if rect.collidepoint(pos_mouse):
                            selecionar_perfil(perfil)
                            self.tela_perfis = False
                            return "PERFIL_TROCADO"
            elif not self.sub_modo:
                if self.btn_jogar.collidepoint(pos_mouse):
                    self.modificadores_run = set(config_jogo.get("modificadores_run", []))
                    self.sub_modo = True
                elif self.btn_cosmeticos.collidepoint(pos_mouse):
                    self.tela_cosmeticos = True
                    if desbloquear_cosmetico(dados, COSMETICO_PADRAO):
                        salvar_dados(dados)
                elif self.btn_perfil.collidepoint(pos_mouse): self.tela_perfis = True
                elif self.btn_personagem.collidepoint(pos_mouse): self.selecao_personagem = True
                elif self.icon_buttons["npcs"][0].collidepoint(pos_mouse): return "IR_NPCS"
                elif self.icon_buttons["config"][0].collidepoint(pos_mouse): return "IR_CONFIG"
                elif self.icon_buttons["index"][0].collidepoint(pos_mouse): return "IR_INDEX"
                elif self.icon_buttons["loja"][0].collidepoint(pos_mouse): self.tela_loja = True
                elif self.icon_buttons["conquistas"][0].collidepoint(pos_mouse): return "IR_CONQUISTAS"
                elif self.icon_buttons["missoes_titulo"][0].collidepoint(pos_mouse): return "IR_MISSOES"
                elif self.icon_buttons["historia"][0].collidepoint(pos_mouse): return "IR_HISTORIA"
                elif self.btn_discord.collidepoint(pos_mouse): return "ABRIR_DISCORD"
                elif self.btn_sair.collidepoint(pos_mouse): return "SAIR"
            else:
                if self.btn_abrir_modificadores.collidepoint(pos_mouse):
                    self.modificadores_run = set(config_jogo.get("modificadores_run", []))
                    self.tela_modificadores = True
                elif self.btn_easy.collidepoint(pos_mouse):
                    config_jogo["modificadores_run"] = sorted(self.modificadores_run)
                    config_jogo['modo_dificuldade'] = 'EASY'; self.sub_modo = False; return "INICIAR_RUN"
                elif self.btn_normal.collidepoint(pos_mouse):
                    config_jogo["modificadores_run"] = sorted(self.modificadores_run)
                    config_jogo['modo_dificuldade'] = 'NORMAL'; self.sub_modo = False; return "INICIAR_RUN"
                elif self.btn_hard.collidepoint(pos_mouse):
                    config_jogo["modificadores_run"] = sorted(self.modificadores_run)
                    config_jogo['modo_dificuldade'] = 'HARD'; self.sub_modo = False; return "INICIAR_RUN"
                elif self.btn_hardcore.collidepoint(pos_mouse):
                    config_jogo["modificadores_run"] = sorted(self.modificadores_run)
                    config_jogo['modo_dificuldade'] = 'HARDCORE'; self.sub_modo = False; return "INICIAR_RUN"
                elif self.btn_voltar_modo.collidepoint(pos_mouse): self.sub_modo = False
        else:
            if self.btn_voltar_loja.collidepoint(pos_mouse): self.tela_loja = False
            elif self.btn_aba_upgrades.collidepoint(pos_mouse):
                self.aba_loja = "UPGRADES"
            elif self.btn_aba_pets.collidepoint(pos_mouse):
                self.aba_loja = "PETS"
            elif self.aba_loja == "PETS":
                self.loja_pets.tratar_clique(pos_mouse, dados)
            else:
                for chave, (rect_b, custo, maximo) in self.rects_upgrades.items():
                    if rect_b.collidepoint(pos_mouse) and not maximo and gemas >= custo:
                        dados['gemas'] -= custo
                        dados['upgrades_nivel'][chave] = dados['upgrades_nivel'].get(chave, 0) + 1
                        salvar_dados(dados)
                        break
        return None
