# loja_permanente.py
import pygame
from config import LARGURA, ALTURA, BRANCO, PRETO, CINZA, AMARELO, VERDE, AZUL, ROXO, FONTE_SYS, FONTE_GRANDE

class TelaLojaPermanente:
    def __init__(self):
        self.btn_voltar = pygame.Rect(LARGURA//2 - 100, ALTURA - 60, 200, 40)
        self.btn_comprar_robo = pygame.Rect(LARGURA - 230, 260, 150, 28)
        self.btn_comprar_fenix = pygame.Rect(LARGURA - 230, 310, 150, 28)

    def desenhar(self, tela, dados_salvos, pos_mouse):
        s = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        s.fill((0, 0, 0, 235))
        tela.blit(s, (0, 0))
        txt_t = FONTE_GRANDE.render("LOJA DE MELHORIAS & PETS", True, AZUL)
        tela.blit(txt_t, (LARGURA//2 - txt_t.get_width()//2, 20))
        txt_gemas = FONTE_SYS.render(f"Gemas Disponíveis: {dados_salvos.get('gemas', 0)} 💎", True, AMARELO)
        tela.blit(txt_gemas, (LARGURA//2 - txt_gemas.get_width()//2, 60))

        tem_robo = dados_salvos.get('pets_comprados', {}).get('robo', False)
        tela.blit(FONTE_SYS.render("• Robô Coletor (Atrai loot) - 50 💎", True, BRANCO), (80, 262))
        pygame.draw.rect(tela, VERDE if not tem_robo else CINZA, self.btn_comprar_robo, border_radius=4)
        tela.blit(FONTE_SYS.render("ADQUIRIDO" if tem_robo else "Comprar", True, PRETO if tem_robo else BRANCO), (self.btn_comprar_robo.centerx - 30, self.btn_comprar_robo.centery - 8))

        tem_fenix = dados_salvos.get('pets_comprados', {}).get('fenix', False)
        tela.blit(FONTE_SYS.render("• Fênix de Fogo (Atira nos mobs) - 100 💎", True, BRANCO), (80, 312))
        pygame.draw.rect(tela, VERDE if not tem_fenix else CINZA, self.btn_comprar_fenix, border_radius=4)
        tela.blit(FONTE_SYS.render("ADQUIRIDO" if tem_fenix else "Comprar", True, PRETO if tem_fenix else BRANCO), (self.btn_comprar_fenix.centerx - 30, self.btn_comprar_fenix.centery - 8))

        pygame.draw.rect(tela, AMARELO, self.btn_voltar, border_radius=6)
        tela.blit(FONTE_SYS.render("Voltar ao Menu", True, PRETO), (self.btn_voltar.centerx - 50, self.btn_voltar.centery - 10))

    def tratar_clique(self, pos_mouse, dados_salvos):
        if self.btn_voltar.collidepoint(pos_mouse): return "VOLTAR"
        if 'pets_comprados' not in dados_salvos: dados_salvos['pets_comprados'] = {}
        if self.btn_comprar_robo.collidepoint(pos_mouse) and not dados_salvos['pets_comprados'].get('robo') and dados_salvos.get('gemas', 0) >= 50:
            dados_salvos['gemas'] -= 50; dados_salvos['pets_comprados']['robo'] = True
        elif self.btn_comprar_fenix.collidepoint(pos_mouse) and not dados_salvos['pets_comprados'].get('fenix') and dados_salvos.get('gemas', 0) >= 100:
            dados_salvos['gemas'] -= 100; dados_salvos['pets_comprados']['fenix'] = True
        return None