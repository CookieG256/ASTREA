import pygame

from config import (
    LARGURA, ALTURA, BRANCO, FUNDO_UI, ROXO_UI, PAINEL_UI, PAINEL_UI_CLARO,
    BORDA_UI, DOURADO_UI, FONTE_SYS, FONTE_GRANDE,
)
from idiomas import t
from save import salvar_dados
from cosmeticos import desbloquear_cosmetico


_METAS = (
    ("abates", "conquista_abates", (1, 10, 25, 50, 100, 250, 500, 1000)),
    ("elites", "conquista_elites", (1, 3, 5, 10, 25, 50, 100)),
    ("andares", "conquista_andares", (1, 3, 5, 10, 15, 20, 30, 50)),
    ("gemas", "conquista_gemas", (10, 50, 100, 250, 500, 1000, 2500, 5000)),
    ("runs", "conquista_runs", (1, 3, 5, 10, 20, 30, 50, 100)),
    ("chefes_secretos", "conquista_secretos", (1, 3, 5, 10, 25)),
    ("runs_hardcore", "conquista_hardcore", (1, 3, 5, 10, 20, 50)),
)
CATALOGO_CONQUISTAS = tuple(
    (f"{grupo}_{meta}", texto, objetivo, meta)
    for objetivo, texto, metas in _METAS
    for grupo, meta in ((objetivo, valor) for valor in metas)
)


class GerenciadorConquistas:
    def __init__(self, dados_salvos):
        self.dados = dados_salvos
        self.dados.setdefault("conquistas", {})
        self.dados.setdefault("estatisticas_conquistas", {})

    def verificar_e_desbloquear(self, chave, hardcore=False):
        self.dados["conquistas"][chave] = "dourado" if hardcore else "comum"

    def registrar_run(self, estatisticas, dificuldade, cooperativo=False):
        totais = self.dados.setdefault("estatisticas_conquistas", {})
        conquistas = self.dados.setdefault("conquistas", {})
        incrementos = {
            "abates": int(estatisticas.get("mobs_mortos", 0)),
            "elites": int(estatisticas.get("elites_derrotados", 0)),
            "andares": max(1, int(estatisticas.get("andar_morte", 1))),
            "gemas": int(estatisticas.get("gemas_coletadas", 0)),
            "runs": 1,
            "chefes_secretos": int(estatisticas.get("chefes_secretos_derrotados", 0)),
            "runs_hardcore": int(dificuldade == "HARDCORE"),
        }
        for chave, quantidade in incrementos.items():
            totais[chave] = int(totais.get(chave, 0)) + quantidade

        for chave, _, objetivo, meta in CATALOGO_CONQUISTAS:
            if totais.get(objetivo, 0) >= meta:
                desbloqueada = chave not in conquistas
                conquistas.setdefault(
                    chave, "dourado" if dificuldade == "HARDCORE" else "comum"
                )
                if desbloqueada:
                    cosmetico = {
                        "abates_100": "chama_violeta",
                        "andares_15": "folha_dourada",
                        "chefes_secretos_1": "rosa_nebulosa",
                        "runs_hardcore_5": "coroa_do_vazio",
                    }.get(chave)
                    if cosmetico:
                        desbloquear_cosmetico(self.dados, cosmetico)
        totais["runs_coop"] = int(totais.get("runs_coop", 0)) + int(cooperativo)
        salvar_dados(self.dados)


class TelaConquistasBestiario:
    def __init__(self):
        self.btn_voltar = pygame.Rect(LARGURA // 2 - 100, ALTURA - 55, 200, 36)
        self.scroll = 0

    def desenhar(self, tela, conquistas_mgr, pos_mouse, config_jogo):
        lang = config_jogo.get("idioma", "PT")
        tela.fill(FUNDO_UI)
        painel = pygame.Rect(85, 90, LARGURA - 170, ALTURA - 160)
        pygame.draw.rect(tela, PAINEL_UI, painel, border_radius=16)
        pygame.draw.rect(tela, BORDA_UI, painel, 1, border_radius=16)
        titulo = FONTE_GRANDE.render(t("titulo_conquistas", lang), True, DOURADO_UI)
        tela.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 30))

        desbloqueadas = conquistas_mgr.dados.get("conquistas", {})
        totais = conquistas_mgr.dados.get("estatisticas_conquistas", {})
        inicio = max(0, min(self.scroll, len(CATALOGO_CONQUISTAS) - 1))
        clip_anterior = tela.get_clip()
        tela.set_clip(painel.inflate(-12, -12))
        for indice, (chave, categoria, objetivo, meta) in enumerate(
            CATALOGO_CONQUISTAS[inicio:inicio + 12]
        ):
            y = painel.y + 12 + indice * 34
            valor = min(meta, int(totais.get(objetivo, 0)))
            selo = desbloqueadas.get(chave)
            nome = f"{t(categoria, lang)} · {meta}"
            estado = t("selo_dourado" if selo == "dourado" else "selo_comum", lang) if selo else f"{valor}/{meta}"
            cor = DOURADO_UI if selo == "dourado" else BRANCO if selo else (145, 145, 160)
            linha = FONTE_SYS.render(f"{nome}  [{estado}]", True, cor)
            tela.blit(linha, (painel.x + 16, y))
        tela.set_clip(clip_anterior)

        hover = self.btn_voltar.collidepoint(pos_mouse)
        cor = PAINEL_UI_CLARO if hover else PAINEL_UI
        pygame.draw.rect(tela, cor, self.btn_voltar, border_radius=6)
        pygame.draw.rect(tela, ROXO_UI if hover else BORDA_UI, self.btn_voltar, 2 if hover else 1, border_radius=6)
        label = FONTE_SYS.render(t("voltar_menu", lang), True, DOURADO_UI if hover else BRANCO)
        tela.blit(label, (self.btn_voltar.centerx - label.get_width() // 2, self.btn_voltar.centery - label.get_height() // 2))
        indicador = FONTE_SYS.render(f"{inicio + 1}-{min(inicio + 12, len(CATALOGO_CONQUISTAS))}/{len(CATALOGO_CONQUISTAS)}", True, BRANCO)
        tela.blit(indicador, (LARGURA // 2 - indicador.get_width() // 2, ALTURA - 84))

    def tratar_evento(self, evento):
        self.scroll = max(0, min(
            max(0, len(CATALOGO_CONQUISTAS) - 12),
            self.scroll - evento.y * 3,
        ))

    def tratar_clique(self, pos_mouse):
        if self.btn_voltar.collidepoint(pos_mouse):
            return "VOLTAR"
        return None
