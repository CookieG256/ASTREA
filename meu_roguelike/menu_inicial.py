# menu_inicial.py
import pygame
from config import LARGURA, ALTURA, BRANCO, PRETO, CINZA, AMARELO, VERDE, VERMELHO, ROXO, CIANO, FONTE_SYS, FONTE_GRANDE
from save import carregar_dados, salvar_dados

class MenuInicial:
    def __init__(self):
        self.btn_jogar = pygame.Rect(LARGURA//2 - 120, 180, 240, 45)
        self.btn_loja_perm = pygame.Rect(LARGURA//2 - 120, 235, 240, 45)
        self.btn_index = pygame.Rect(LARGURA//2 - 120, 290, 240, 45)
        self.btn_config = pygame.Rect(LARGURA//2 - 120, 345, 240, 45)
        self.btn_sair = pygame.Rect(LARGURA//2 - 120, 400, 240, 45)

        self.sub_modo = False
        self.btn_casual = pygame.Rect(LARGURA//2 - 120, 220, 240, 40)
        self.btn_dificil = pygame.Rect(LARGURA//2 - 120, 275, 240, 40)
        self.btn_hardcore = pygame.Rect(LARGURA//2 - 120, 330, 240, 40)
        self.btn_voltar_modo = pygame.Rect(LARGURA//2 - 120, 385, 240, 35)

        self.tela_loja = False
        self.btn_up_hp = pygame.Rect(LARGURA//2 - 180, 200, 360, 45)
        self.btn_up_mana = pygame.Rect(LARGURA//2 - 180, 260, 360, 45)
        self.btn_voltar_loja = pygame.Rect(LARGURA//2 - 100, 400, 200, 40)

    def desenhar(self, tela, pos_mouse, gemas):
        tela.fill(PRETO)

        if not self.tela_loja:
            txt_t = FONTE_GRANDE.render("ROGUELIKE", True, AMARELO)
            tela.blit(txt_t, (LARGURA//2 - txt_t.get_width()//2, 50))

            txt_gemas = FONTE_SYS.render(f"Gemas: {gemas}", True, CIANO)
            tela.blit(txt_gemas, (LARGURA//2 - txt_gemas.get_width()//2, 100))

            if not self.sub_modo:
                for btn, texto, cor_base in [
                    (self.btn_jogar, "JOGAR (PLAY)", VERDE),
                    (self.btn_loja_perm, "Loja", AMARELO),
                    (self.btn_index, "INDEX / ENCICLOPÉDIA", ROXO),
                    (self.btn_config, "CONFIGURAÇÕES", CINZA),
                    (self.btn_sair, "SAIR DO JOGO", VERMELHO)
                ]:
                    cor = BRANCO if btn.collidepoint(pos_mouse) else cor_base
                    pygame.draw.rect(tela, cor, btn, border_radius=8)
                    txt = FONTE_SYS.render(texto, True, PRETO if cor == BRANCO else BRANCO)
                    tela.blit(txt, (btn.centerx - txt.get_width()//2, btn.centery - txt.get_height()//2))
            else:
                txt_m = FONTE_SYS.render("SELEÇÃO DE DIFICULDADE", True, AMARELO)
                tela.blit(txt_m, (LARGURA//2 - txt_m.get_width()//2, 150))

                for btn, texto, cor_base in [
                    (self.btn_casual, "CASUAL", VERDE),
                    (self.btn_dificil, "DIFÍCIL (+50% Dificuldade)", AMARELO),
                    (self.btn_hardcore, "Hardcore ", VERMELHO),
                    (self.btn_voltar_modo, "VOLTAR", CINZA)
                ]:
                    cor = BRANCO if btn.collidepoint(pos_mouse) else cor_base
                    pygame.draw.rect(tela, cor, btn, border_radius=6)
                    txt = FONTE_SYS.render(texto, True, PRETO if cor == BRANCO else BRANCO)
                    tela.blit(txt, (btn.centerx - txt.get_width()//2, btn.centery - txt.get_height()//2))
        else:
            txt_l = FONTE_GRANDE.render("LOJA DE GEMAS", True, CIANO)
            tela.blit(txt_l, (LARGURA//2 - txt_l.get_width()//2, 60))

            txt_g = FONTE_SYS.render(f"Gemas Disponíveis: {gemas}", True, BRANCO)
            tela.blit(txt_g, (LARGURA//2 - txt_g.get_width()//2, 120))

            for btn, texto in [
                (self.btn_up_hp, "Comprar +50 HP Máximo (Custo: 20 Gemas)"),
                (self.btn_up_mana, "Comprar +50 Mana Máxima (Custo: 20 Gemas)")
            ]:
                cor = BRANCO if btn.collidepoint(pos_mouse) else CINZA
                pygame.draw.rect(tela, cor, btn, border_radius=6)
                txt = FONTE_SYS.render(texto, True, PRETO if cor == BRANCO else BRANCO)
                tela.blit(txt, (btn.centerx - txt.get_width()//2, btn.centery - txt.get_height()//2))

            cor_v = AMARELO if self.btn_voltar_loja.collidepoint(pos_mouse) else CINZA
            pygame.draw.rect(tela, cor_v, self.btn_voltar_loja, border_radius=6)
            txt_v = FONTE_SYS.render("Voltar", True, PRETO if cor_v == AMARELO else BRANCO)
            tela.blit(txt_v, (self.btn_voltar_loja.centerx - txt_v.get_width()//2, self.btn_voltar_loja.centery - txt_v.get_height()//2))

    def tratar_clique(self, pos_mouse, config_jogo):
        dados = carregar_dados()
        gemas = dados.get('gemas', 0)

        if not self.tela_loja:
            if not self.sub_modo:
                if self.btn_jogar.collidepoint(pos_mouse):
                    self.sub_modo = True
                elif self.btn_loja_perm.collidepoint(pos_mouse):
                    self.tela_loja = True
                elif self.btn_index.collidepoint(pos_mouse):
                    return "IR_INDEX"
                elif self.btn_config.collidepoint(pos_mouse):
                    return "IR_CONFIG"
                elif self.btn_sair.collidepoint(pos_mouse):
                    return "SAIR"
            else:
                if self.btn_casual.collidepoint(pos_mouse):
                    config_jogo['modo_dificuldade'] = 'CASUAL'
                    self.sub_modo = False
                    return "INICIAR_RUN"
                elif self.btn_dificil.collidepoint(pos_mouse):
                    config_jogo['modo_dificuldade'] = 'DIFICIL'
                    self.sub_modo = False
                    return "INICIAR_RUN"
                elif self.btn_hardcore.collidepoint(pos_mouse):
                    config_jogo['modo_dificuldade'] = 'HARDCORE'
                    self.sub_modo = False
                    return "INICIAR_RUN"
                elif self.btn_voltar_modo.collidepoint(pos_mouse):
                    self.sub_modo = False
        else:
            if self.btn_voltar_loja.collidepoint(pos_mouse):
                self.tela_loja = False
            elif self.btn_up_hp.collidepoint(pos_mouse) and gemas >= 20:
                dados['gemas'] -= 20
                dados['upgrades_permanentes']['hp_extra'] = dados['upgrades_permanentes'].get('hp_extra', 0) + 50
                salvar_dados(dados)
            elif self.btn_up_mana.collidepoint(pos_mouse) and gemas >= 20:
                dados['gemas'] -= 20
                dados['upgrades_permanentes']['mana_extra'] = dados['upgrades_permanentes'].get('mana_extra', 0) + 50
                salvar_dados(dados)

        return None

