# menu_config.py
import pygame
from config import LARGURA, ALTURA, BRANCO, PRETO, CINZA, AMARELO, VERDE, FONTE_SYS, FONTE_GRANDE
from idiomas import t

class MenuConfiguracoes:
    def __init__(self):
        self.btn_modo_tiro = pygame.Rect(LARGURA//2 - 180, 160, 360, 40)
        self.btn_idioma = pygame.Rect(LARGURA//2 - 180, 215, 360, 40)
        self.btn_vol_musica = pygame.Rect(LARGURA//2 - 180, 270, 360, 40)
        self.btn_vol_sfx = pygame.Rect(LARGURA//2 - 180, 325, 360, 40)
        self.btn_voltar = pygame.Rect(LARGURA//2 - 100, 420, 200, 40)

    def desenhar(self, tela, config_jogo, pos_mouse):
        tela.fill(PRETO)
        lang = config_jogo.get('idioma', 'PT')

        txt_t = FONTE_GRANDE.render(t("config", lang), True, AMARELO)
        tela.blit(txt_t, (LARGURA//2 - txt_t.get_width()//2, 60))

        cor_tiro = BRANCO if self.btn_modo_tiro.collidepoint(pos_mouse) else CINZA
        pygame.draw.rect(tela, cor_tiro, self.btn_modo_tiro, border_radius=6)
        txt_tiro = FONTE_SYS.render(f"{t('modo_tiro', lang)}: {config_jogo.get('modo_tiro', 'AUTOMATICO')}", True, PRETO if cor_tiro == BRANCO else BRANCO)
        tela.blit(txt_tiro, (self.btn_modo_tiro.centerx - txt_tiro.get_width()//2, self.btn_modo_tiro.centery - txt_tiro.get_height()//2))

        cor_id = BRANCO if self.btn_idioma.collidepoint(pos_mouse) else CINZA
        pygame.draw.rect(tela, cor_id, self.btn_idioma, border_radius=6)
        txt_id = FONTE_SYS.render(t("idioma", lang), True, PRETO if cor_id == BRANCO else BRANCO)
        tela.blit(txt_id, (self.btn_idioma.centerx - txt_id.get_width()//2, self.btn_idioma.centery - txt_id.get_height()//2))

        vol_m = int(config_jogo.get('volume_musica', 0.5) * 10)
        cor_vm = BRANCO if self.btn_vol_musica.collidepoint(pos_mouse) else CINZA
        pygame.draw.rect(tela, cor_vm, self.btn_vol_musica, border_radius=6)
        txt_vm = FONTE_SYS.render(f"{t('volume_musica', lang)}: {vol_m}/10 (Clique p/ mudar)", True, PRETO if cor_vm == BRANCO else BRANCO)
        tela.blit(txt_vm, (self.btn_vol_musica.centerx - txt_vm.get_width()//2, self.btn_vol_musica.centery - txt_vm.get_height()//2))

        vol_s = int(config_jogo.get('volume_sfx', 0.7) * 10)
        cor_vs = BRANCO if self.btn_vol_sfx.collidepoint(pos_mouse) else CINZA
        pygame.draw.rect(tela, cor_vs, self.btn_vol_sfx, border_radius=6)
        txt_vs = FONTE_SYS.render(f"{t('volume_sfx', lang)}: {vol_s}/10 (Clique p/ mudar)", True, PRETO if cor_vs == BRANCO else BRANCO)
        tela.blit(txt_vs, (self.btn_vol_sfx.centerx - txt_vs.get_width()//2, self.btn_vol_sfx.centery - txt_vs.get_height()//2))

        cor_v = BRANCO if self.btn_voltar.collidepoint(pos_mouse) else VERDE
        pygame.draw.rect(tela, cor_v, self.btn_voltar, border_radius=6)
        txt_v = FONTE_SYS.render(t("voltar", lang), True, PRETO if cor_v == BRANCO else BRANCO)
        tela.blit(txt_v, (self.btn_voltar.centerx - txt_v.get_width()//2, self.btn_voltar.centery - txt_v.get_height()//2))

    def tratar_clique(self, pos_mouse, config_jogo):
        if self.btn_modo_tiro.collidepoint(pos_mouse):
            config_jogo['modo_tiro'] = 'MANUAL' if config_jogo.get('modo_tiro', 'AUTOMATICO') == 'AUTOMATICO' else 'AUTOMATICO'
        elif self.btn_idioma.collidepoint(pos_mouse):
            idiomas = ['PT', 'ES', 'EN']
            idx = idiomas.index(config_jogo.get('idioma', 'PT'))
            config_jogo['idioma'] = idiomas[(idx + 1) % len(idiomas)]
        elif self.btn_vol_musica.collidepoint(pos_mouse):
            vol_atual = config_jogo.get('volume_musica', 0.5)
            novo_vol = round(vol_atual + 0.2, 1)
            if novo_vol > 1.0:
                novo_vol = 0.0
            config_jogo['volume_musica'] = novo_vol
            pygame.mixer.music.set_volume(novo_vol)
        elif self.btn_vol_sfx.collidepoint(pos_mouse):
            vol_atual = config_jogo.get('volume_sfx', 0.7)
            novo_vol = round(vol_atual + 0.2, 1)
            if novo_vol > 1.0:
                novo_vol = 0.0
            config_jogo['volume_sfx'] = novo_vol
        elif self.btn_voltar.collidepoint(pos_mouse):
            return "VOLTAR"
        return None