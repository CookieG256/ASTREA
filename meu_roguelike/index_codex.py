# index_codex.py
import pygame
from config import LARGURA, ALTURA, BRANCO, PRETO, CINZA, AMARELO, ROXO, FONTE_SYS, FONTE_GRANDE
from banco_itens import TODAS_ARMAS, TODOS_AMULETOS, CORES_RARIDADE
from save import carregar_dados
from idiomas import t

class TelaIndexCodex:
    def __init__(self):
        self.btn_voltar = pygame.Rect(LARGURA//2 - 100, 520, 200, 40)
        self.scroll_y = 0
        self.max_scroll = 0

    def desenhar(self, tela, pos_mouse, config_jogo):
        tela.fill(PRETO)
        dados = carregar_dados()
        descobertas = dados.get('index_descobertas', {})
        lang = config_jogo.get('idioma', 'PT')

        # Título limpo e traduzido
        txt_t = FONTE_GRANDE.render(t("titulo_index", lang), True, AMARELO)
        tela.blit(txt_t, (LARGURA//2 - txt_t.get_width()//2, 15))

        todos_itens = TODAS_ARMAS + TODOS_AMULETOS
        
        altura_total = len(todos_itens) * 52
        self.max_scroll = min(0, -(altura_total - 380))

        y_pos = 75 + self.scroll_y
        for item in todos_itens:
            if 65 <= y_pos <= 500:
                rect_card = pygame.Rect(LARGURA//2 - 230, y_pos, 460, 45)
                cor_card = (60, 60, 65) if rect_card.collidepoint(pos_mouse) else CINZA
                pygame.draw.rect(tela, cor_card, rect_card, border_radius=8)

                nome = item['nome']
                desc = item.get('desc', '')
                raridade = item.get('raridade', 'Comum')
                cor_raridade = CORES_RARIDADE.get(raridade, BRANCO)

                if descobertas.get(nome, False):
                    txt_nome = FONTE_SYS.render(f"{nome} [{raridade}]", True, cor_raridade)
                    txt_desc = FONTE_SYS.render(desc, True, BRANCO)
                else:
                    txt_nome = FONTE_SYS.render("??? (Item Desconhecido)", True, BRANCO)
                    txt_desc = FONTE_SYS.render("Encontre este item em uma run para desbloquear.", True, CINZA)

                tela.blit(txt_nome, (rect_card.x + 12, rect_card.y + 5))
                tela.blit(txt_desc, (rect_card.x + 12, rect_card.y + 24))

            y_pos += 52

        cor_v = AMARELO if self.btn_voltar.collidepoint(pos_mouse) else CINZA
        pygame.draw.rect(tela, cor_v, self.btn_voltar, border_radius=6)
        txt_v = FONTE_SYS.render(t("voltar_lobby", lang), True, PRETO if cor_v == AMARELO else BRANCO)
        tela.blit(txt_v, (self.btn_voltar.centerx - txt_v.get_width()//2, self.btn_voltar.centery - txt_v.get_height()//2))

    def tratar_evento(self, evento, pos_mouse):
        if evento.type == pygame.MOUSEWHEEL:
            self.scroll_y += evento.y * 30
            if self.scroll_y > 0:
                self.scroll_y = 0
            if self.scroll_y < self.max_scroll:
                self.scroll_y = self.max_scroll

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.btn_voltar.collidepoint(pos_mouse):
                return "VOLTAR_LOBBY"
                
        return None

    def tratar_clique(self, pos_mouse):
        if self.btn_voltar.collidepoint(pos_mouse):
            return "VOLTAR_LOBBY"
        return None