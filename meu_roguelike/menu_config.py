# menu_config.py
import pygame
from config import LARGURA, ALTURA, BRANCO, PRETO, CINZA, AMARELO, VERDE, VERMELHO, FONTE_SYS, FONTE_GRANDE

class MenuConfiguracoes:
    def __init__(self):
        self.btn_voltar = pygame.Rect(LARGURA//2 - 100, 480, 200, 40)
        self.btn_modo_tiro = pygame.Rect(LARGURA//2 - 120, 160, 240, 40)
        
        self.btn_vol_menos = pygame.Rect(LARGURA//2 - 120, 240, 45, 35)
        self.btn_vol_mais = pygame.Rect(LARGURA//2 + 75, 240, 45, 35)

    def desenhar(self, tela, config_jogo, pos_mouse):
        s = pygame.Surface((LARGURA, ALTURA))
        s.set_alpha(235)
        s.fill(PRETO)
        tela.blit(s, (0, 0))

        txt_t = FONTE_GRANDE.render("CONFIGURAÇÕES", True, AMARELO)
        tela.blit(txt_t, (LARGURA//2 - txt_t.get_width()//2, 50))

        cor_t = VERDE if self.btn_modo_tiro.collidepoint(pos_mouse) else CINZA
        pygame.draw.rect(tela, cor_t, self.btn_modo_tiro, border_radius=6)
        txt_tiro = FONTE_SYS.render(f"Modo Tiro: {config_jogo['modo_tiro']}", True, BRANCO)
        tela.blit(txt_tiro, (self.btn_modo_tiro.centerx - txt_tiro.get_width()//2, self.btn_modo_tiro.centery - txt_tiro.get_height()//2))

        txt_v_lbl = FONTE_SYS.render(f"Volume SFX: {config_jogo['volume_sfx']}%", True, BRANCO)
        tela.blit(txt_v_lbl, (LARGURA//2 - txt_v_lbl.get_width()//2, 215))

        pygame.draw.rect(tela, VERMELHO if self.btn_vol_menos.collidepoint(pos_mouse) else CINZA, self.btn_vol_menos, border_radius=5)
        pygame.draw.rect(tela, VERDE if self.btn_vol_mais.collidepoint(pos_mouse) else CINZA, self.btn_vol_mais, border_radius=5)
        
        t_m = FONTE_GRANDE.render("-", True, BRANCO)
        t_p = FONTE_GRANDE.render("+", True, BRANCO)
        tela.blit(t_m, (self.btn_vol_menos.centerx - t_m.get_width()//2, self.btn_vol_menos.centery - t_m.get_height()//2 - 2))
        tela.blit(t_p, (self.btn_vol_mais.centerx - t_p.get_width()//2, self.btn_vol_mais.centery - t_p.get_height()//2 - 2))

        cor_v = AMARELO if self.btn_voltar.collidepoint(pos_mouse) else CINZA
        pygame.draw.rect(tela, cor_v, self.btn_voltar, border_radius=6)
        txt_v = FONTE_SYS.render("Voltar", True, PRETO if cor_v == AMARELO else BRANCO)
        tela.blit(txt_v, (self.btn_voltar.centerx - txt_v.get_width()//2, self.btn_voltar.centery - txt_v.get_height()//2))

    def tratar_clique(self, pos_mouse, config_jogo):
        if self.btn_voltar.collidepoint(pos_mouse):
            return "VOLTAR"
        elif self.btn_modo_tiro.collidepoint(pos_mouse):
            config_jogo['modo_tiro'] = 'MANUAL' if config_jogo['modo_tiro'] == 'AUTOMATICO' else 'AUTOMATICO'
        elif self.btn_vol_menos.collidepoint(pos_mouse):
            config_jogo['volume_sfx'] = max(0, config_jogo['volume_sfx'] - 10)
        elif self.btn_vol_mais.collidepoint(pos_mouse):
            config_jogo['volume_sfx'] = min(100, config_jogo['volume_sfx'] + 10)
        return None