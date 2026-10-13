# conquistas.py
import pygame
from config import LARGURA, ALTURA, BRANCO, PRETO, CINZA, AMARELO, FONTE_SYS, FONTE_GRANDE

class GerenciadorConquistas:
    def __init__(self, dados_salvos):
        self.dados = dados_salvos
        if 'conquistas' not in self.dados: self.dados['conquistas'] = {}

    def verificar_e_desbloquear(self, chave, hardcore=False):
        self.dados['conquistas'][chave] = "dourado" if hardcore else "comum"

class TelaConquistasBestiario:
    def __init__(self):
        self.btn_voltar = pygame.Rect(LARGURA//2 - 100, ALTURA - 70, 200, 40)

    def desenhar(self, tela, conquistas_mgr, pos_mouse):
        s = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        s.fill((0, 0, 0, 235))
        tela.blit(s, (0, 0))
        tela.blit(FONTE_GRANDE.render("CONQUISTAS E SELOS", True, AMARELO), (LARGURA//2 - 130, 40))
        pygame.draw.rect(tela, AMARELO, self.btn_voltar, border_radius=6)
        tela.blit(FONTE_SYS.render("Voltar ao Menu", True, PRETO), (self.btn_voltar.centerx - 50, self.btn_voltar.centery - 10))

    def tratar_clique(self, pos_mouse):
        if self.btn_voltar.collidepoint(pos_mouse): return "VOLTAR"
        return None