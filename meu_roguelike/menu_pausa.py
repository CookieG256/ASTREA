# menu_pausa.py
import pygame
from config import LARGURA, ALTURA, BRANCO, PRETO, CINZA, AMARELO, VERDE, VERMELHO, FONTE_SYS, FONTE_GRANDE
from idiomas import t

class MenuPausa:
    def __init__(self):
        self.btn_retomar = pygame.Rect(LARGURA//2 - 120, 200, 240, 45)
        self.btn_lobby = pygame.Rect(LARGURA//2 - 120, 265, 240, 45)
        self.btn_sair = pygame.Rect(LARGURA//2 - 120, 330, 240, 45)

    def desenhar(self, tela, config_jogo, pos_mouse):
        superficie_sombra = pygame.Surface((LARGURA, ALTURA))
        superficie_sombra.set_alpha(160)
        superficie_sombra.fill(PRETO)
        tela.blit(superficie_sombra, (0, 0))

        lang = config_jogo.get('idioma', 'PT')

        txt_t = FONTE_GRANDE.render(t("pausa", lang), True, AMARELO)
        tela.blit(txt_t, (LARGURA//2 - txt_t.get_width()//2, 110))

        cor_ret = BRANCO if self.btn_retomar.collidepoint(pos_mouse) else CINZA
        pygame.draw.rect(tela, cor_ret, self.btn_retomar, border_radius=6)
        txt_ret = FONTE_SYS.render(t("retomar", lang), True, PRETO if cor_ret == BRANCO else BRANCO)
        tela.blit(txt_ret, (self.btn_retomar.centerx - txt_ret.get_width()//2, self.btn_retomar.centery - txt_ret.get_height()//2))

        cor_lob = BRANCO if self.btn_lobby.collidepoint(pos_mouse) else CINZA
        pygame.draw.rect(tela, cor_lob, self.btn_lobby, border_radius=6)
        txt_lob = FONTE_SYS.render(t("voltar_lobby", lang), True, PRETO if cor_lob == BRANCO else BRANCO)
        tela.blit(txt_lob, (self.btn_lobby.centerx - txt_lob.get_width()//2, self.btn_lobby.centery - txt_lob.get_height()//2))

        cor_sai = BRANCO if self.btn_sair.collidepoint(pos_mouse) else VERMELHO
        pygame.draw.rect(tela, cor_sai, self.btn_sair, border_radius=6)
        txt_sai = FONTE_SYS.render(t("sair", lang), True, PRETO if cor_sai == BRANCO else BRANCO)
        tela.blit(txt_sai, (self.btn_sair.centerx - txt_sai.get_width()//2, self.btn_sair.centery - txt_sai.get_height()//2))

    def tratar_clique(self, pos_mouse):
        if self.btn_retomar.collidepoint(pos_mouse):
            return "RETOMAR"
        elif self.btn_lobby.collidepoint(pos_mouse):
            return "LOBBY"
        elif self.btn_sair.collidepoint(pos_mouse):
            return "SAIR"
        return None