import pygame
from config import LARGURA, ALTURA, BRANCO, CINZA, CINZA_CLARO, AMARELO, VERMELHO, VERDE, CIANO, FONTE_SYS, FONTE_GRANDE, RARIDADE_CORES
from pixel_assets import sprite_item
from tooltip import desenhar_tooltip
from idiomas import t
from sinergias import sinergia_ativa
from jogador import configurar_municao_arma


class TelaInventario:
    def __init__(self):
        self.slots_esquerda = [pygame.Rect(100, 160 + i * 65, 45, 45) for i in range(4)]
        self.slots_direita = [pygame.Rect(520 + (i % 3) * 60, 160 + (i // 3) * 60, 45, 45) for i in range(9)]
        self.slot_lixeira = pygame.Rect(705, 270, 76, 50)
        self.slots_amuletos = [pygame.Rect(280 + i * 55, 480, 45, 45) for i in range(5)]
        self.item_selecionado_mochila_idx = None

    @staticmethod
    def _equipamentos(player):
        return (
            player.equipado_capacete,
            player.equipado_peitoral,
            player.equipado_calca,
            player.equipado_arma,
        )

    def _item_hover(self, player, pos_mouse):
        for index, rect in enumerate(self.slots_direita):
            if index < len(player.mochila_itens) and rect.collidepoint(pos_mouse):
                return player.mochila_itens[index]
        for index, rect in enumerate(self.slots_esquerda):
            item = self._equipamentos(player)[index]
            if item and rect.collidepoint(pos_mouse):
                return item
        for index, rect in enumerate(self.slots_amuletos):
            if index < len(player.amuletos_equipados) and rect.collidepoint(pos_mouse):
                return player.amuletos_equipados[index]
        return None

    def desenhar(self, tela, player, pos_mouse, lang="PT"):
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        tela.blit(overlay, (0, 0))

        titulo = FONTE_GRANDE.render("INVENTÁRIO ([E] para fechar)", True, AMARELO)
        tela.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 25))
        tela.blit(FONTE_SYS.render("EQUIPADOS", True, BRANCO), (100, 130))
        labels = ("Capacete", "Peitoral", "Calça", "Arma")

        for index, rect in enumerate(self.slots_esquerda):
            item = self._equipamentos(player)[index]
            self._desenhar_slot(tela, rect, item, rect.collidepoint(pos_mouse), labels[index])

        tela.blit(FONTE_SYS.render(f"MOCHILA ({len(player.mochila_itens)}/9)", True, BRANCO), (520, 130))
        for index, rect in enumerate(self.slots_direita):
            selecionado = self.item_selecionado_mochila_idx == index
            item = player.mochila_itens[index] if index < len(player.mochila_itens) else None
            self._desenhar_slot(tela, rect, item, rect.collidepoint(pos_mouse), selecionado=selecionado)

        pygame.draw.rect(tela, (50, 20, 20), self.slot_lixeira, border_radius=6)
        pygame.draw.rect(tela, VERMELHO if self.slot_lixeira.collidepoint(pos_mouse) else CINZA, self.slot_lixeira, 2, border_radius=6)
        lixo = FONTE_SYS.render(t("desmontar", lang), True, BRANCO)
        tela.blit(lixo, (self.slot_lixeira.centerx - lixo.get_width() // 2, self.slot_lixeira.centery - lixo.get_height() // 2))
        fragmentos = FONTE_SYS.render(
            f"{t('fragmentos', lang)}: {getattr(player, 'fragmentos_run', 0)}",
            True, CIANO,
        )
        tela.blit(fragmentos, (self.slot_lixeira.centerx - fragmentos.get_width() // 2, self.slot_lixeira.bottom + 5))

        tela.blit(FONTE_SYS.render(f"AMULETOS ({len(player.amuletos_equipados)}/5)", True, BRANCO), (280, 450))
        for index, rect in enumerate(self.slots_amuletos):
            item = player.amuletos_equipados[index] if index < len(player.amuletos_equipados) else None
            self._desenhar_slot(tela, rect, item, rect.collidepoint(pos_mouse), selecionado=False)

        pet = getattr(player, "pet_tipo", None)
        chave_pet = "pet_" + pet if pet else "pet_nenhum"
        pet_texto = FONTE_SYS.render(f"{t('pet_beneficio', lang)}: {t(chave_pet, lang)}", True, VERDE)
        tela.blit(pet_texto, (100, 535))
        buffs = getattr(player, "buffs_run", {})
        if buffs:
            bonus = []
            if buffs.get("dano"): bonus.append(f"{t('up_dano', lang)} +{int(buffs['dano'] * 100)}%")
            if buffs.get("vida"): bonus.append(f"{t('up_hp_max', lang)} +{int(buffs['vida'])}")
            if buffs.get("velocidade"): bonus.append(f"{t('up_velocidade', lang)} +{buffs['velocidade']}")
            if buffs.get("defesa"): bonus.append(f"{t('up_defesa', lang)} +{int(buffs['defesa'] * 100)}%")
            if bonus:
                tela.blit(FONTE_SYS.render(" | ".join(bonus), True, AMARELO), (100, 560))

        sinergia = sinergia_ativa(player)
        texto_sinergia = t(sinergia, lang) if sinergia else t("sinergia_nenhuma", lang)
        tela.blit(FONTE_SYS.render(f"{t('sinergias', lang)}: {texto_sinergia}", True, CIANO), (100, 582))

        item_hover = self._item_hover(player, pos_mouse)
        if item_hover:
            desenhar_tooltip(tela, item_hover, pos_mouse)

    @staticmethod
    def _desenhar_slot(tela, rect, item, hover, label=None, selecionado=False):
        pygame.draw.rect(tela, (30, 30, 40), rect, border_radius=5)
        cor = VERDE if selecionado else AMARELO if hover else RARIDADE_CORES.get(item.get("raridade", "Comum"), CINZA) if item else CINZA
        pygame.draw.rect(tela, cor, rect, 2, border_radius=5)
        if item:
            icon = sprite_item(item, 32)
            tela.blit(icon, (rect.centerx - 16, rect.centery - 16))
        if label:
            nome = item.get("nome", "Vazio") if item else "Vazio"
            texto = FONTE_SYS.render(f"{label}: {nome}", True, BRANCO if item else CINZA_CLARO)
            tela.blit(texto, (155, rect.y + 12))

    @staticmethod
    def _tipo_item(item):
        tipo = item.get("tipo")
        if tipo in ("equip_capacete", "equip_peitoral", "equip_calca", "equip_arma"):
            return tipo
        if item.get("tipo_arma") in ("melee", "ranged", "mage"):
            return "equip_arma"
        if "valor" in item:
            return "equip_amulet"
        return tipo

    @staticmethod
    def _aplicar_atributos(player, item, sinal):
        tipo = TelaInventario._tipo_item(item)
        vida = item.get("valor_hp", item.get("valor", 0) if tipo in ("equip_capacete", "equip_peitoral") else 0)
        vida += item.get("valor_hp", 0) if tipo == "equip_calca" else 0
        if vida:
            player.hp_max = max(1, player.hp_max + sinal * vida)
            player.hp = min(player.hp, player.hp_max)
        if tipo == "equip_calca":
            player.vel_base = max(1, player.vel_base + sinal * item.get("valor_vel", 0))
        if tipo in ("equip_capacete", "equip_peitoral", "equip_calca"):
            player.defesa_percent = max(0.0, player.defesa_percent + sinal * item.get("valor_def", 0) / 100)
        descricao = item.get("desc", "").lower()
        valor = item.get("valor", 0)
        if tipo == "equip_amulet":
            if "defesa" in descricao:
                player.defesa_percent = max(0.0, player.defesa_percent + sinal * valor / 100)
            elif "dano" in descricao:
                player.bonus_dano_percent += sinal * valor / 100
            elif "mana" in descricao:
                player.mana_max = max(1, player.mana_max + sinal * valor)
                player.mana = min(player.mana, player.mana_max)
            elif "vida" in descricao or "hp" in descricao:
                player.hp_max = max(1, player.hp_max + sinal * valor)
                player.hp = min(player.hp, player.hp_max)

    def _retirar_equipado(self, player, slot):
        if len(player.mochila_itens) >= 9:
            return False
        nomes = ("equipado_capacete", "equipado_peitoral", "equipado_calca", "equipado_arma")
        attr = nomes[slot]
        item = getattr(player, attr)
        if not item:
            return False
        self._aplicar_atributos(player, item, -1)
        item_guardado = item.copy()
        item_guardado["tipo"] = self._tipo_item(item)
        player.mochila_itens.append(item_guardado)
        setattr(player, attr, None)
        return True

    def _equipar_mochila(self, player, slot):
        index = self.item_selecionado_mochila_idx
        if index is None or index >= len(player.mochila_itens):
            return False
        item = player.mochila_itens[index]
        tipo = self._tipo_item(item)
        attrs = ("equipado_capacete", "equipado_peitoral", "equipado_calca", "equipado_arma")
        tipos_slot = ("equip_capacete", "equip_peitoral", "equip_calca", "equip_arma")
        if tipo == "equip_amulet":
            return False
        if tipo != tipos_slot[slot]:
            return False

        antigo = getattr(player, attrs[slot])
        if antigo and len(player.mochila_itens) >= 9:
            # Replacing the selected item frees one backpack slot.
            pass
        self._aplicar_atributos(player, item, 1)
        if antigo:
            self._aplicar_atributos(player, antigo, -1)
            antigo_guardado = antigo.copy()
            antigo_guardado["tipo"] = self._tipo_item(antigo)
        else:
            antigo_guardado = None
        item_equipado = item.copy()
        item_equipado["tipo"] = tipo
        if tipo == "equip_arma":
            item_equipado.setdefault("tipo_arma", "ranged")
            configurar_municao_arma(item_equipado)
        player.mochila_itens.pop(index)
        if antigo_guardado:
            player.mochila_itens.append(antigo_guardado)
        setattr(player, attrs[slot], item_equipado)
        self.item_selecionado_mochila_idx = None
        return True

    def tratar_clique(self, pos_mouse, player):
        for index, rect in enumerate(self.slots_direita):
            if rect.collidepoint(pos_mouse):
                if index < len(player.mochila_itens):
                    self.item_selecionado_mochila_idx = index
                return

        if self.slot_lixeira.collidepoint(pos_mouse) and self.item_selecionado_mochila_idx is not None:
            if self.item_selecionado_mochila_idx < len(player.mochila_itens):
                item = player.mochila_itens.pop(self.item_selecionado_mochila_idx)
                materiais_por_raridade = {
                    "Comum": 1, "Incomum": 2, "Raro": 3,
                    "Épico": 4, "Lendário": 5, "Mítico": 6,
                }
                player.fragmentos_run = getattr(player, "fragmentos_run", 0) + materiais_por_raridade.get(
                    item.get("raridade", "Comum"), 1
                )
            self.item_selecionado_mochila_idx = None
            return

        for index, rect in enumerate(self.slots_esquerda):
            if not rect.collidepoint(pos_mouse):
                continue
            if self.item_selecionado_mochila_idx is not None:
                self._equipar_mochila(player, index)
            else:
                self._retirar_equipado(player, index)
            return

        for index, rect in enumerate(self.slots_amuletos):
            if not rect.collidepoint(pos_mouse):
                continue
            selected = self.item_selecionado_mochila_idx
            if selected is None:
                if index < len(player.amuletos_equipados) and len(player.mochila_itens) < 9:
                    item = player.amuletos_equipados.pop(index)
                    self._aplicar_atributos(player, item, -1)
                    item_guardado = item.copy()
                    item_guardado["tipo"] = "equip_amulet"
                    player.mochila_itens.append(item_guardado)
            elif selected < len(player.mochila_itens):
                item = player.mochila_itens[selected]
                if self._tipo_item(item) == "equip_amulet" and len(player.amuletos_equipados) < 5:
                    item_equipado = item.copy()
                    item_equipado["tipo"] = "equip_amulet"
                    player.amuletos_equipados.append(item_equipado)
                    self._aplicar_atributos(player, item_equipado, 1)
                    player.mochila_itens.pop(selected)
                    self.item_selecionado_mochila_idx = None
            return
