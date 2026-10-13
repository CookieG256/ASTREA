# inventario.py
import pygame
from config import LARGURA, ALTURA, BRANCO, PRETO, CINZA, CINZA_CLARO, AMARELO, VERMELHO, VERDE, ROXO, FONTE_SYS, FONTE_GRANDE

class TelaInventario:
    def __init__(self):
        self.slots_esquerda = [pygame.Rect(100, 160 + i*65, 45, 45) for i in range(4)]
        self.slots_direita = [pygame.Rect(520 + (i%3)*60, 160 + (i//3)*60, 45, 45) for i in range(9)]
        self.slot_lixeira = pygame.Rect(715, 270, 50, 50)
        self.slots_amuletos = [pygame.Rect(280 + i*55, 480, 45, 45) for i in range(5)]

        self.item_selecionado_mochila_idx = None

    def desenhar(self, tela, player, pos_mouse):
        s = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        s.fill((0, 0, 0, 220))
        tela.blit(s, (0, 0))

        txt_t = FONTE_GRANDE.render("INVENTÁRIO ([E] para fechar)", True, AMARELO)
        tela.blit(txt_t, (LARGURA//2 - txt_t.get_width()//2, 25))

        txt_eq = FONTE_SYS.render("EQUIPADOS", True, BRANCO)
        tela.blit(txt_eq, (100, 130))
        labels_eq = ["Capacete", "Peitoral", "Calça", "Arma"]
        
        for i, rect in enumerate(self.slots_esquerda):
            cor_borda = AMARELO if rect.collidepoint(pos_mouse) else CINZA
            pygame.draw.rect(tela, (30, 30, 40), rect, border_radius=5)
            pygame.draw.rect(tela, cor_borda, rect, 2, border_radius=5)
            
            nome_item = "Vazio"
            if i == 0 and player.equipado_capacete: nome_item = player.equipado_capacete['nome']
            elif i == 1 and player.equipado_peitoral: nome_item = player.equipado_peitoral['nome']
            elif i == 2 and player.equipado_calca: nome_item = player.equipado_calca['nome']
            elif i == 3 and player.equipado_arma: nome_item = player.equipado_arma['nome']
            
            if len(nome_item) > 18: nome_item = nome_item[:15] + "..."

            txt_lbl = FONTE_SYS.render(f"{labels_eq[i]}: {nome_item}", True, BRANCO if nome_item != "Vazio" else CINZA_CLARO)
            tela.blit(txt_lbl, (155, rect.y + 12))

        txt_moch = FONTE_SYS.render(f"MOCHILA ({len(player.mochila_itens)}/9)", True, BRANCO)
        tela.blit(txt_moch, (520, 130))

        for i, rect in enumerate(self.slots_direita):
            cor_borda = AMARELO if rect.collidepoint(pos_mouse) else CINZA
            if self.item_selecionado_mochila_idx == i: cor_borda = VERDE
            
            pygame.draw.rect(tela, (30, 30, 40), rect, border_radius=5)
            pygame.draw.rect(tela, cor_borda, rect, 2, border_radius=5)

            if i < len(player.mochila_itens):
                item = player.mochila_itens[i]
                txt_item_mini = FONTE_SYS.render(item['nome'][:2].upper(), True, AMARELO)
                tela.blit(txt_item_mini, (rect.centerx - txt_item_mini.get_width()//2, rect.centery - txt_item_mini.get_height()//2))

        cor_lixo = VERMELHO if self.slot_lixeira.collidepoint(pos_mouse) else CINZA
        pygame.draw.rect(tela, (50, 20, 20), self.slot_lixeira, border_radius=6)
        pygame.draw.rect(tela, cor_lixo, self.slot_lixeira, 2, border_radius=6)
        txt_lixo = FONTE_SYS.render("LIXO", True, BRANCO)
        tela.blit(txt_lixo, (self.slot_lixeira.centerx - txt_lixo.get_width()//2, self.slot_lixeira.centery - txt_lixo.get_height()//2))

        txt_am = FONTE_SYS.render(f"AMULETOS ({len(player.amuletos_equipados)}/5)", True, BRANCO)
        tela.blit(txt_am, (280, 450))

        for i, rect in enumerate(self.slots_amuletos):
            cor_borda = AMARELO if rect.collidepoint(pos_mouse) else CINZA
            pygame.draw.rect(tela, (30, 30, 40), rect, border_radius=5)
            pygame.draw.rect(tela, cor_borda, rect, 2, border_radius=5)

            if i < len(player.amuletos_equipados):
                txt_am_mini = FONTE_SYS.render("AMU", True, ROXO)
                tela.blit(txt_am_mini, (rect.centerx - txt_am_mini.get_width()//2, rect.centery - txt_am_mini.get_height()//2))

    def tratar_clique(self, pos_mouse, player):
        for i, rect in enumerate(self.slots_direita):
            if rect.collidepoint(pos_mouse):
                if i < len(player.mochila_itens):
                    self.item_selecionado_mochila_idx = i
                return

        if self.slot_lixeira.collidepoint(pos_mouse) and self.item_selecionado_mochila_idx is not None:
            player.mochila_itens.pop(self.item_selecionado_mochila_idx)
            self.item_selecionado_mochila_idx = None
            return

        for i, rect in enumerate(self.slots_esquerda):
            if rect.collidepoint(pos_mouse) and self.item_selecionado_mochila_idx is not None:
                item_novo = player.mochila_itens.pop(self.item_selecionado_mochila_idx)
                t = item_novo.get('tipo')

                if i == 0 and t == "equip_capacete":
                    if player.equipado_capacete: player.mochila_itens.append(player.equipado_capacete)
                    player.equipado_capacete = item_novo
                    player.hp_max += item_novo.get('valor', 0)
                    player.hp += item_novo.get('valor', 0)
                    self.item_selecionado_mochila_idx = None
                elif i == 1 and t == "equip_peitoral":
                    if player.equipado_peitoral: player.mochila_itens.append(player.equipado_peitoral)
                    player.equipado_peitoral = item_novo
                    player.hp_max += item_novo.get('valor', 0)
                    player.hp += item_novo.get('valor', 0)
                    self.item_selecionado_mochila_idx = None
                elif i == 2 and t == "equip_calca":
                    if player.equipado_calca: player.mochila_itens.append(player.equipado_calca)
                    player.equipado_calca = item_novo
                    player.hp_max += item_novo.get('valor_hp', 0)
                    player.hp += item_novo.get('valor_hp', 0)
                    player.vel_base += item_novo.get('valor_vel', 0)
                    self.item_selecionado_mochila_idx = None
                elif i == 3 and t == "equip_arma":
                    if player.equipado_arma and player.equipado_arma.get('nome') != 'Pistola':
                        player.mochila_itens.append({'nome': player.equipado_arma['nome'], 'tipo': 'equip_arma', 'dano': player.equipado_arma['dano'], 'cadencia': player.equipado_arma['cadencia']})
                    player.equipado_arma = {'nome': item_novo['nome_arma'], 'dano': item_novo['dano'], 'cadencia': item_novo['cadencia']}
                    self.item_selecionado_mochila_idx = None
                return