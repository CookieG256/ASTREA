# index_codex.py
import pygame
from config import LARGURA, ALTURA, PRETO, AMARELO, CINZA, CINZA_CLARO, VERMELHO, BRANCO, VERDE_CLARO, FONTE_GRANDE, FONTE_SYS, FONTE_PEQUENA

class TelaIndexCodex:
    def __init__(self):
        self.botao_voltar = pygame.Rect(LARGURA//2 - 100, 500, 200, 40)

    def desenhar(self, tela, dados_descobertas, pos_mouse):
        s_overlay = pygame.Surface((LARGURA, ALTURA))
        s_overlay.set_alpha(220)
        s_overlay.fill(PRETO)
        tela.blit(s_overlay, (0, 0))

        txt_titulo = FONTE_GRANDE.render("INDEX / ENCICLOPÉDIA", True, AMARELO)
        tela.blit(txt_titulo, (LARGURA//2 - txt_titulo.get_width()//2, 50))

        y_pos = 120
        itens_exemplo = [
            {"nome": "Moeda da Sorte", "desc": "+15% de ouro ganho", "id": "moeda_sorte"},
            {"nome": "Anel de Fogo", "desc": "Tiros aplicam queimadura", "id": "anel_fogo"},
            {"nome": "Coração de Dragão", "desc": "Revive 1 vez por run", "id": "coracao_dragao"}
        ]

        for item in itens_exemplo:
            descoberto = dados_descobertas.get('artefatos', {}).get(item['id'], False)
            cor_caixa = CINZA if descoberto else (30, 30, 35)
            pygame.draw.rect(tela, cor_caixa, (150, y_pos, 500, 50), border_radius=6)

            if descoberto:
                txt_nome = FONTE_SYS.render(item['nome'], True, BRANCO)
                txt_desc = FONTE_PEQUENA.render(item['desc'], True, VERDE_CLARO)
                tela.blit(txt_nome, (170, y_pos + 8))
                tela.blit(txt_desc, (170, y_pos + 28))
            else:
                txt_bloq = FONTE_SYS.render("??? (Item Desconhecido)", True, CINZA_CLARO)
                tela.blit(txt_bloq, (170, y_pos + 15))

            y_pos += 65

        cor_v = VERMELHO if self.botao_voltar.collidepoint(pos_mouse) else CINZA
        pygame.draw.rect(tela, cor_v, self.botao_voltar, border_radius=6)
        txt_v = FONTE_SYS.render("Voltar ao Lobby", True, BRANCO)
        tela.blit(txt_v, (self.botao_voltar.centerx - txt_v.get_width()//2, self.botao_voltar.centery - txt_v.get_height()//2))

    def tratar_clique(self, pos_mouse):
        if self.botao_voltar.collidepoint(pos_mouse):
            return "VOLTAR_LOBBY"
        return None