# menu_inicial.py
import pygame
from config import LARGURA, ALTURA, BRANCO, PRETO, CINZA, AMARELO, VERDE, VERMELHO, ROXO, CIANO, FONTE_SYS, FONTE_GRANDE, FONTE_TITULO
from save import carregar_dados, salvar_dados
from idiomas import t

UPGRADES_CONFIG = {
    "hp_max": {"chave_nome": "up_hp_max", "max": 15, "custo_base": 10, "fator": 5},
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
        self.btn_jogar = pygame.Rect(LARGURA//2 - 120, 180, 240, 45)
        self.btn_config = pygame.Rect(LARGURA//2 - 120, 235, 240, 45)
        self.btn_loja_perm = pygame.Rect(LARGURA//2 - 120, 290, 240, 45)
        self.btn_index = pygame.Rect(LARGURA//2 - 120, 345, 240, 45)
        self.btn_sair = pygame.Rect(LARGURA//2 - 120, 400, 240, 45)

        self.sub_modo = False
        self.btn_casual = pygame.Rect(LARGURA//2 - 120, 220, 240, 40)
        self.btn_dificil = pygame.Rect(LARGURA//2 - 120, 275, 240, 40)
        self.btn_hardcore = pygame.Rect(LARGURA//2 - 120, 330, 240, 40)
        self.btn_voltar_modo = pygame.Rect(LARGURA//2 - 120, 385, 240, 35)

        self.tela_loja = False
        self.btn_voltar_loja = pygame.Rect(LARGURA//2 - 100, 520, 200, 40)
        self.rects_upgrades = {}

    def desenhar(self, tela, pos_mouse, gemas, config_jogo):
        tela.fill(PRETO)
        dados = carregar_dados()
        lang = config_jogo.get('idioma', 'PT')

        txt_gemas = FONTE_SYS.render(f"{t('gemas', lang)}: {gemas}", True, CIANO)
        tela.blit(txt_gemas, (LARGURA - txt_gemas.get_width() - 20, 20))

        vits = dados.get('vitórias_totais', 0)
        txt_vits = FONTE_SYS.render(f"{t('vitorias_totais', lang)}: {vits}", True, AMARELO)
        tela.blit(txt_vits, (20, 20))

        if not self.tela_loja:
            txt_t = FONTE_TITULO.render(t("titulo_jogo", lang), True, AMARELO)
            tela.blit(txt_t, (LARGURA//2 - txt_t.get_width()//2, 70))

            if not self.sub_modo:
                for btn, chave_txt, cor_base in [
                    (self.btn_jogar, "jogar", VERDE),
                    (self.btn_config, "config", CINZA),
                    (self.btn_loja_perm, "loja", AMARELO),
                    (self.btn_index, "index", ROXO),
                    (self.btn_sair, "sair", VERMELHO)
                ]:
                    cor = BRANCO if btn.collidepoint(pos_mouse) else cor_base
                    pygame.draw.rect(tela, cor, btn, border_radius=8)
                    txt = FONTE_SYS.render(t(chave_txt, lang), True, PRETO if cor == BRANCO else BRANCO)
                    tela.blit(txt, (btn.centerx - txt.get_width()//2, btn.centery - txt.get_height()//2))
            else:
                for btn, chave_txt, cor_base in [
                    (self.btn_casual, "casual", VERDE),
                    (self.btn_dificil, "dificil", AMARELO),
                    (self.btn_hardcore, "hardcore", VERMELHO),
                    (self.btn_voltar_modo, "voltar", CINZA)
                ]:
                    cor = BRANCO if btn.collidepoint(pos_mouse) else cor_base
                    pygame.draw.rect(tela, cor, btn, border_radius=6)
                    txt = FONTE_SYS.render(t(chave_txt, lang), True, PRETO if cor == BRANCO else BRANCO)
                    tela.blit(txt, (btn.centerx - txt.get_width()//2, btn.centery - txt.get_height()//2))
        else:
            txt_l = FONTE_GRANDE.render(t("loja_upgrades", lang), True, CIANO)
            tela.blit(txt_l, (LARGURA//2 - txt_l.get_width()//2, 20))

            ups_salvos = dados.get('upgrades_nivel', {})
            y_p = 75
            self.rects_upgrades = {}

            for chave, cfg in UPGRADES_CONFIG.items():
                lvl_atual = ups_salvos.get(chave, 0)
                max_l = cfg['max']
                custo = cfg['custo_base'] + (lvl_atual * cfg['fator'])
                nome_up = t(cfg['chave_nome'], lang)

                txt_st = f"MAX (Lvl {max_l})" if lvl_atual >= max_l else f"Lvl {lvl_atual}/{max_l} - {t('gemas', lang)}: {custo}"
                rect_b = pygame.Rect(LARGURA//2 - 240, y_p, 480, 36)
                self.rects_upgrades[chave] = (rect_b, custo, lvl_atual >= max_l)

                cor = BRANCO if rect_b.collidepoint(pos_mouse) else CINZA
                pygame.draw.rect(tela, cor, rect_b, border_radius=5)

                txt_u = FONTE_SYS.render(f"{nome_up}: {txt_st}", True, PRETO if cor == BRANCO else BRANCO)
                tela.blit(txt_u, (rect_b.centerx - txt_u.get_width()//2, rect_b.centery - txt_u.get_height()//2))
                y_p += 42

            cor_v = AMARELO if self.btn_voltar_loja.collidepoint(pos_mouse) else CINZA
            pygame.draw.rect(tela, cor_v, self.btn_voltar_loja, border_radius=6)
            txt_v = FONTE_SYS.render(t("voltar_menu", lang), True, PRETO if cor_v == AMARELO else BRANCO)
            tela.blit(txt_v, (self.btn_voltar_loja.centerx - txt_v.get_width()//2, self.btn_voltar_loja.centery - txt_v.get_height()//2))

    def tratar_clique(self, pos_mouse, config_jogo):
        dados = carregar_dados()
        gemas = dados.get('gemas', 0)

        if 'upgrades_nivel' not in dados:
            dados['upgrades_nivel'] = {}

        if not self.tela_loja:
            if not self.sub_modo:
                if self.btn_jogar.collidepoint(pos_mouse): self.sub_modo = True
                elif self.btn_config.collidepoint(pos_mouse): return "IR_CONFIG"
                elif self.btn_loja_perm.collidepoint(pos_mouse): self.tela_loja = True
                elif self.btn_index.collidepoint(pos_mouse): return "IR_INDEX"
                elif self.btn_sair.collidepoint(pos_mouse): return "SAIR"
            else:
                if self.btn_casual.collidepoint(pos_mouse):
                    config_jogo['modo_dificuldade'] = 'CASUAL'; self.sub_modo = False; return "INICIAR_RUN"
                elif self.btn_dificil.collidepoint(pos_mouse):
                    config_jogo['modo_dificuldade'] = 'DIFICIL'; self.sub_modo = False; return "INICIAR_RUN"
                elif self.btn_hardcore.collidepoint(pos_mouse):
                    config_jogo['modo_dificuldade'] = 'HARDCORE'; self.sub_modo = False; return "INICIAR_RUN"
                elif self.btn_voltar_modo.collidepoint(pos_mouse): self.sub_modo = False
        else:
            if self.btn_voltar_loja.collidepoint(pos_mouse): self.tela_loja = False
            else:
                for chave, (rect_b, custo, maximo) in self.rects_upgrades.items():
                    if rect_b.collidepoint(pos_mouse) and not maximo and gemas >= custo:
                        dados['gemas'] -= custo
                        dados['upgrades_nivel'][chave] = dados['upgrades_nivel'].get(chave, 0) + 1
                        salvar_dados(dados)
                        break
        return None