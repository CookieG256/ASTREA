import random

import pygame
from config import LARGURA, ALTURA, BRANCO, CINZA, CINZA_CLARO, AMARELO, VERMELHO, VERDE, CIANO, CIANO_UI, DOURADO_UI, BORDA_UI, PAINEL_UI, PAINEL_UI_CLARO, FONTE_SYS, FONTE_PEQUENA, FONTE_GRANDE, RARIDADE_CORES
from pixel_assets import sprite_item
from tooltip import desenhar_tooltip
from idiomas import t
from sinergias import sinergia_ativa
from jogador import configurar_municao_arma
from banco_itens import TODAS_ARMAS, TODOS_AMULETOS, SETS_ARMADURAS, registrar_item_no_index


class TelaInventario:
    def __init__(self):
        self.slots_esquerda = [pygame.Rect(100, 160 + i * 65, 45, 45) for i in range(4)]
        self.slots_direita = [pygame.Rect(520 + (i % 3) * 60, 160 + (i // 3) * 60, 45, 45) for i in range(9)]
        self.slot_lixeira = pygame.Rect(705, 270, 76, 50)
        self.slots_amuletos = [pygame.Rect(280 + i * 55, 480, 45, 45) for i in range(5)]
        self.item_selecionado_mochila_idx = None
        self.aba = "EQUIPAMENTOS"
        self.btn_aba_equipamentos = pygame.Rect(LARGURA // 2 - 240, 82, 145, 34)
        self.btn_aba_pocoes = pygame.Rect(LARGURA // 2 - 72, 82, 145, 34)
        self.btn_aba_mercado = pygame.Rect(LARGURA // 2 + 96, 82, 145, 34)
        self.btn_aba_alquimia = pygame.Rect(LARGURA // 2 + 264, 82, 145, 34)
        self.btn_usar_pocao = pygame.Rect(LARGURA // 2 - 105, 315, 210, 46)
        self.btn_pocao_rapida = pygame.Rect(LARGURA // 2 - 105, 375, 210, 40)
        self.btn_mercado_fragmentos = pygame.Rect(LARGURA // 2 - 235, 390, 145, 38)
        self.btn_mercado_vida = pygame.Rect(LARGURA // 2 - 72, 390, 145, 38)
        self.btn_mercado_maldicao = pygame.Rect(LARGURA // 2 + 91, 390, 145, 38)
        self.btn_trocar_item = pygame.Rect(LARGURA // 2 - 130, 455, 260, 38)
        self.btn_fundir_armas = pygame.Rect(LARGURA // 2 - 105, 400, 210, 44)
        self.itens_alquimia_indices = set()
        self.aviso_alquimia = ""
        self.pocao_rapida_ativa = False
        self.aviso_mercado = ""
        self.aviso_protecao = ""

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

    @staticmethod
    def _pool_itens(tipo=None, raridade_minima=None):
        pool = [
            dict(item, tipo="equip_arma") for item in TODAS_ARMAS
        ] + [
            dict(item, tipo="equip_amulet") for item in TODOS_AMULETOS
        ]
        for conjunto, dados in SETS_ARMADURAS.items():
            for parte, tipo_peca in (
                ("Capacete", "equip_capacete"),
                ("Peitoral", "equip_peitoral"),
                ("Calça", "equip_calca"),
            ):
                pool.append({
                    "nome": f"{parte} {conjunto}",
                    "tipo": tipo_peca,
                    "raridade": dados["raridade"],
                    "valor_hp": max(5, int(dados["hp"] / 3)),
                    "valor_def": max(1, int(dados["def"] / 3)),
                    "desc": dados["set_completo"],
                })
        raridades = ("Comum", "Incomum", "Raro", "Épico", "Lendário", "Mítico")
        if tipo:
            pool = [item for item in pool if TelaInventario._tipo_item(item) == tipo]
        if raridade_minima:
            minimo = raridades.index(raridade_minima)
            pool = [
                item for item in pool
                if raridades.index(item.get("raridade", "Comum")) >= minimo
            ]
        return pool

    @staticmethod
    def _preparar_item(item):
        item = dict(item)
        item["tipo"] = TelaInventario._tipo_item(item)
        item.pop("protegido", None)
        if item["tipo"] == "equip_arma" and item.get("tipo_arma") == "ranged":
            configurar_municao_arma(item)
        return item

    def usar_pocao(self, player):
        if (
            not self.pocao_rapida_ativa
            or getattr(player, "pocoes_run", 0) <= 0
            or player.hp >= player.hp_max
        ):
            return 0
        cura = min(60, player.hp_max - player.hp)
        player.hp += cura
        player.pocoes_run -= 1
        return cura

    def alternar_protecao(self, player, pos_mouse=None):
        item = None
        if pos_mouse is not None:
            for index, rect in enumerate(self.slots_direita):
                if index < len(player.mochila_itens) and rect.collidepoint(pos_mouse):
                    item = player.mochila_itens[index]
                    break
            if item is None:
                for index, rect in enumerate(self.slots_esquerda):
                    equipado = self._equipamentos(player)[index]
                    if equipado and rect.collidepoint(pos_mouse):
                        item = equipado
                        break
            if item is None:
                for index, rect in enumerate(self.slots_amuletos):
                    if index < len(player.amuletos_equipados) and rect.collidepoint(pos_mouse):
                        item = player.amuletos_equipados[index]
                        break
        elif self.item_selecionado_mochila_idx is not None:
            index = self.item_selecionado_mochila_idx
            if index < len(player.mochila_itens):
                item = player.mochila_itens[index]
        if item is None:
            return False
        item["protegido"] = not item.get("protegido", False)
        self.aviso_protecao = (
            "inventario_item_protegido" if item["protegido"]
            else "inventario_item_desprotegido"
        )
        return item["protegido"]

    def _garantir_oferta_mercado(self, player):
        if not hasattr(player, "oferta_mercado_negro"):
            player.oferta_mercado_negro = self._preparar_item(
                random.choice(self._pool_itens(raridade_minima="Raro"))
            )
            player.oferta_mercado_comprada = False

    def _comprar_mercado(self, player, forma_pagamento):
        self._garantir_oferta_mercado(player)
        if player.oferta_mercado_comprada:
            self.aviso_mercado = "inventario_mercado_esgotado"
            return False
        if len(player.mochila_itens) >= 9:
            self.aviso_mercado = "inventario_mercado_mochila_cheia"
            return False
        custo_fragmentos = 10
        custo_vida = max(20, int(player.hp_max * 0.2))
        if forma_pagamento == "fragmentos":
            if getattr(player, "fragmentos_run", 0) < custo_fragmentos:
                self.aviso_mercado = "inventario_mercado_sem_fragmentos"
                return False
            player.fragmentos_run -= custo_fragmentos
        elif forma_pagamento == "vida":
            if player.hp <= custo_vida:
                self.aviso_mercado = "inventario_mercado_vida_insuficiente"
                return False
            player.hp -= custo_vida
        elif forma_pagamento == "maldicao":
            if getattr(player, "maldicao_mercado_ativa", False):
                self.aviso_mercado = "inventario_mercado_maldicao_ativa"
                return False
            player.bonus_dano_percent -= 0.15
            player.maldicao_mercado_ativa = True
        else:
            return False
        item_comprado = self._preparar_item(player.oferta_mercado_negro)
        player.mochila_itens.append(item_comprado)
        registrar_item_no_index(item_comprado["nome"])
        player.oferta_mercado_comprada = True
        self.aviso_mercado = "inventario_mercado_compra_ok"
        return True

    def _trocar_item_mercador(self, player):
        indice = self.item_selecionado_mochila_idx
        if indice is None or indice >= len(player.mochila_itens):
            self.aviso_mercado = "inventario_mercado_selecione"
            return False
        item_atual = player.mochila_itens[indice]
        if item_atual.get("protegido"):
            self.aviso_mercado = "inventario_mercado_protegido"
            return False
        tipo = self._tipo_item(item_atual)
        pool = [
            item for item in self._pool_itens(tipo=tipo)
            if item.get("nome") != item_atual.get("nome")
        ]
        if not pool:
            self.aviso_mercado = "inventario_mercado_sem_troca"
            return False
        item_trocado = self._preparar_item(random.choice(pool))
        player.mochila_itens[indice] = item_trocado
        registrar_item_no_index(item_trocado["nome"])
        self.item_selecionado_mochila_idx = None
        self.aviso_mercado = "inventario_mercado_troca_ok"
        return True

    def desenhar(self, tela, player, pos_mouse, lang="PT"):
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        tela.blit(overlay, (0, 0))

        titulo = FONTE_GRANDE.render(t("inventario_titulo", lang), True, AMARELO)
        tela.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 25))
        for rect, chave, aba in (
            (self.btn_aba_equipamentos, "inventario_equipamentos", "EQUIPAMENTOS"),
            (self.btn_aba_pocoes, "inventario_pocoes", "POCOES"),
            (self.btn_aba_mercado, "inventario_mercado", "MERCADO"),
            (self.btn_aba_alquimia, "inventario_alquimia", "ALQUIMIA"),
        ):
            ativo = self.aba == aba
            hover = rect.collidepoint(pos_mouse)
            pygame.draw.rect(tela, (57, 49, 91) if ativo or hover else (30, 30, 40), rect, border_radius=7)
            pygame.draw.rect(tela, CIANO if ativo else CINZA, rect, 2 if ativo else 1, border_radius=7)
            label = t(chave, lang)
            if aba == "POCOES":
                label += f" ({getattr(player, 'pocoes_run', 0)})"
            texto = FONTE_SYS.render(label, True, BRANCO)
            tela.blit(texto, (rect.centerx - texto.get_width() // 2, rect.centery - texto.get_height() // 2))

        if self.aba == "ALQUIMIA":
            titulo_alquimia = FONTE_GRANDE.render(
                t("inventario_alquimia_titulo", lang), True, DOURADO_UI
            )
            tela.blit(
                titulo_alquimia,
                (LARGURA // 2 - titulo_alquimia.get_width() // 2, 145),
            )
            instrucao = FONTE_SYS.render(
                t("inventario_alquimia_instrucao", lang), True, CINZA_CLARO
            )
            tela.blit(
                instrucao,
                (LARGURA // 2 - instrucao.get_width() // 2, 185),
            )
            tela.blit(
                FONTE_SYS.render(
                    t("inventario_alquimia_selecionadas", lang).format(
                        quantidade=len(self.itens_alquimia_indices)
                    ),
                    True, CIANO_UI,
                ),
                (LARGURA // 2 - 105, 225),
            )
            for index, rect in enumerate(self.slots_direita):
                item = player.mochila_itens[index] if index < len(player.mochila_itens) else None
                selecionado = index in self.itens_alquimia_indices
                self._desenhar_slot(
                    tela, rect, item,
                    rect.collidepoint(pos_mouse),
                    selecionado=selecionado,
                )
                if item and item.get("protegido"):
                    marca = FONTE_PEQUENA.render("★", True, DOURADO_UI)
                    tela.blit(marca, (rect.right - marca.get_width(), rect.y - 5))
            pode_fundir = self._itens_alquimia_validos(player)
            hover_fundir = self.btn_fundir_armas.collidepoint(pos_mouse)
            pygame.draw.rect(
                tela,
                (42, 105, 65) if pode_fundir and hover_fundir else
                (35, 77, 55) if pode_fundir else PAINEL_UI,
                self.btn_fundir_armas, border_radius=8,
            )
            pygame.draw.rect(
                tela, VERDE if pode_fundir else BORDA_UI,
                self.btn_fundir_armas, 2 if hover_fundir and pode_fundir else 1,
                border_radius=8,
            )
            label_fundir = FONTE_SYS.render(
                t("inventario_alquimia_fundir", lang), True,
                BRANCO if pode_fundir else CINZA_CLARO,
            )
            tela.blit(
                label_fundir,
                (self.btn_fundir_armas.centerx - label_fundir.get_width() // 2,
                 self.btn_fundir_armas.centery - label_fundir.get_height() // 2),
            )
            aviso = self.aviso_alquimia or "inventario_alquimia_regra"
            linha_aviso = FONTE_PEQUENA.render(t(aviso, lang), True, AMARELO)
            tela.blit(
                linha_aviso,
                (LARGURA // 2 - linha_aviso.get_width() // 2, 465),
            )
            return

        if self.aba == "POCOES":
            quantidade = getattr(player, "pocoes_run", 0)
            hp_faltando = max(0, player.hp_max - player.hp)
            cura_prevista = min(60, hp_faltando)
            tela.blit(
                FONTE_GRANDE.render(t("inventario_pocao_nome", lang), True, VERDE),
                (LARGURA // 2 - 120, 190),
            )
            tela.blit(
                FONTE_SYS.render(t("inventario_pocao_quantidade", lang).format(quantidade=quantidade), True, BRANCO),
                (LARGURA // 2 - 120, 240),
            )
            pygame.draw.rect(tela, (30, 30, 40), self.btn_usar_pocao, border_radius=8)
            habilitado = quantidade > 0 and hp_faltando > 0
            hover = self.btn_usar_pocao.collidepoint(pos_mouse)
            pygame.draw.rect(
                tela, VERDE if habilitado and hover else (42, 105, 65) if habilitado else CINZA,
                self.btn_usar_pocao, 2, border_radius=8,
            )
            texto_uso = t("inventario_usar_pocao", lang).format(cura=cura_prevista)
            texto = FONTE_SYS.render(texto_uso, True, BRANCO if habilitado else CINZA_CLARO)
            tela.blit(texto, (self.btn_usar_pocao.centerx - texto.get_width() // 2, self.btn_usar_pocao.centery - texto.get_height() // 2))
            tela.blit(
                FONTE_SYS.render(
                    f"HP: {int(player.hp)}/{int(player.hp_max)}", True, VERDE
                ),
                (LARGURA // 2 - 70, 430),
            )
            chave_rapida = (
                "inventario_pocao_rapida_ativa"
                if self.pocao_rapida_ativa else "inventario_pocao_rapida"
            )
            hover = self.btn_pocao_rapida.collidepoint(pos_mouse)
            pygame.draw.rect(
                tela, PAINEL_UI_CLARO if hover else PAINEL_UI,
                self.btn_pocao_rapida, border_radius=8,
            )
            pygame.draw.rect(
                tela, CIANO_UI if self.pocao_rapida_ativa else BORDA_UI,
                self.btn_pocao_rapida, 2 if self.pocao_rapida_ativa else 1,
                border_radius=8,
            )
            label_rapida = FONTE_SYS.render(t(chave_rapida, lang), True, BRANCO)
            tela.blit(
                label_rapida,
                (self.btn_pocao_rapida.centerx - label_rapida.get_width() // 2,
                 self.btn_pocao_rapida.centery - label_rapida.get_height() // 2),
            )
            return
        if self.aba == "MERCADO":
            self._garantir_oferta_mercado(player)
            oferta = player.oferta_mercado_negro
            titulo_mercado = FONTE_GRANDE.render(
                t("inventario_mercado_titulo", lang), True, DOURADO_UI
            )
            tela.blit(titulo_mercado, (LARGURA // 2 - titulo_mercado.get_width() // 2, 150))
            cor_raridade = RARIDADE_CORES.get(oferta.get("raridade", "Raro"), BRANCO)
            nome = FONTE_GRANDE.render(oferta.get("nome", ""), True, cor_raridade)
            tela.blit(nome, (LARGURA // 2 - nome.get_width() // 2, 205))
            tipo_item = self._tipo_item(oferta)
            tipo_chave = {
                "equip_arma": "inventario_mercado_arma",
                "equip_amulet": "inventario_mercado_amulet",
                "equip_capacete": "inventario_mercado_armadura",
                "equip_peitoral": "inventario_mercado_armadura",
                "equip_calca": "inventario_mercado_armadura",
            }.get(tipo_item, "inventario_mercado_arma")
            tipo = FONTE_SYS.render(t(tipo_chave, lang), True, BRANCO)
            tela.blit(tipo, (LARGURA // 2 - tipo.get_width() // 2, 247))
            descricao = FONTE_PEQUENA.render(oferta.get("desc", ""), True, CINZA_CLARO)
            tela.blit(descricao, (LARGURA // 2 - descricao.get_width() // 2, 274))

            botoes = (
                (self.btn_mercado_fragmentos, "inventario_mercado_fragmentos", "fragmentos"),
                (self.btn_mercado_vida, "inventario_mercado_vida", "vida"),
                (self.btn_mercado_maldicao, "inventario_mercado_maldicao", "maldicao"),
            )
            for rect, chave, _ in botoes:
                hover = rect.collidepoint(pos_mouse)
                pygame.draw.rect(tela, PAINEL_UI_CLARO if hover else PAINEL_UI, rect, border_radius=7)
                pygame.draw.rect(tela, DOURADO_UI if hover else BORDA_UI, rect, 1, border_radius=7)
                label = FONTE_PEQUENA.render(t(chave, lang), True, BRANCO)
                tela.blit(label, (rect.centerx - label.get_width() // 2, rect.centery - label.get_height() // 2))

            index_selecionado = self.item_selecionado_mochila_idx
            pode_trocar = (
                index_selecionado is not None
                and index_selecionado < len(player.mochila_itens)
                and self._tipo_item(player.mochila_itens[index_selecionado]) in (
                    "equip_arma", "equip_amulet", "equip_capacete",
                    "equip_peitoral", "equip_calca",
                )
                and not player.mochila_itens[index_selecionado].get("protegido")
            )
            hover = self.btn_trocar_item.collidepoint(pos_mouse)
            pygame.draw.rect(tela, PAINEL_UI_CLARO if hover else PAINEL_UI, self.btn_trocar_item, border_radius=7)
            pygame.draw.rect(tela, CIANO_UI if pode_trocar else BORDA_UI, self.btn_trocar_item, 2 if pode_trocar else 1, border_radius=7)
            label_troca = FONTE_PEQUENA.render(t("inventario_trocar_item", lang), True, BRANCO if pode_trocar else CINZA_CLARO)
            tela.blit(label_troca, (self.btn_trocar_item.centerx - label_troca.get_width() // 2, self.btn_trocar_item.centery - label_troca.get_height() // 2))
            status = (
                t(self.aviso_mercado, lang)
                if self.aviso_mercado
                else t("inventario_mercado_fragmentos_status", lang).format(
                    fragmentos=getattr(player, "fragmentos_run", 0)
                )
            )
            status_render = FONTE_SYS.render(status, True, CIANO_UI)
            tela.blit(status_render, (LARGURA // 2 - status_render.get_width() // 2, 340))
            return

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
        texto_protecao = self.aviso_protecao or "inventario_proteger_dica"
        dica_protecao = FONTE_PEQUENA.render(
            t(texto_protecao, lang), True,
            DOURADO_UI if self.aviso_protecao else CINZA_CLARO,
        )
        tela.blit(dica_protecao, (LARGURA // 2 - dica_protecao.get_width() // 2, ALTURA - 28))

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
            if item.get("protegido"):
                marca = FONTE_PEQUENA.render("★", True, DOURADO_UI)
                tela.blit(marca, (rect.right - marca.get_width(), rect.y - 5))
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
        if item and item.get("protegido"):
            self.aviso_protecao = "inventario_item_bloqueado"
            return False
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
        if antigo and antigo.get("protegido"):
            self.aviso_protecao = "inventario_item_bloqueado"
            return False
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
        if self.btn_aba_equipamentos.collidepoint(pos_mouse):
            self.aba = "EQUIPAMENTOS"
            return 0
        if self.btn_aba_pocoes.collidepoint(pos_mouse):
            self.aba = "POCOES"
            return 0
        if self.btn_aba_mercado.collidepoint(pos_mouse):
            self.aba = "MERCADO"
            self.aviso_mercado = ""
            self._garantir_oferta_mercado(player)
            return 0
        if self.btn_aba_alquimia.collidepoint(pos_mouse):
            self.aba = "ALQUIMIA"
            self.itens_alquimia_indices.clear()
            self.aviso_alquimia = ""
            return 0
        if self.aba == "POCOES":
            if (
                self.btn_usar_pocao.collidepoint(pos_mouse)
                and getattr(player, "pocoes_run", 0) > 0
                and player.hp < player.hp_max
            ):
                cura = min(60, player.hp_max - player.hp)
                player.hp += cura
                player.pocoes_run -= 1
                return cura
            if self.btn_pocao_rapida.collidepoint(pos_mouse):
                self.pocao_rapida_ativa = not self.pocao_rapida_ativa
            return 0
        if self.aba == "MERCADO":
            for rect, forma_pagamento in (
                (self.btn_mercado_fragmentos, "fragmentos"),
                (self.btn_mercado_vida, "vida"),
                (self.btn_mercado_maldicao, "maldicao"),
            ):
                if rect.collidepoint(pos_mouse):
                    self._comprar_mercado(player, forma_pagamento)
                    return 0
            if self.btn_trocar_item.collidepoint(pos_mouse):
                self._trocar_item_mercador(player)
            return 0
        if self.aba == "ALQUIMIA":
            if self.btn_fundir_armas.collidepoint(pos_mouse):
                self._fundir_armas(player)
                return 0
            for index, rect in enumerate(self.slots_direita):
                if not rect.collidepoint(pos_mouse):
                    continue
                if index >= len(player.mochila_itens):
                    return 0
                item = player.mochila_itens[index]
                if self._tipo_item(item) != "equip_arma":
                    self.aviso_alquimia = "inventario_alquimia_somente_armas"
                    return 0
                if item.get("protegido"):
                    self.aviso_alquimia = "inventario_alquimia_protegida"
                    return 0
                if index in self.itens_alquimia_indices:
                    self.itens_alquimia_indices.remove(index)
                    self.aviso_alquimia = ""
                    return 0
                if len(self.itens_alquimia_indices) >= 3:
                    self.aviso_alquimia = "inventario_alquimia_maximo"
                    return 0
                self.itens_alquimia_indices.add(index)
                self.aviso_alquimia = ""
                return 0
            return 0

        for index, rect in enumerate(self.slots_direita):
            if rect.collidepoint(pos_mouse):
                if index < len(player.mochila_itens):
                    self.item_selecionado_mochila_idx = index
                return

        if self.slot_lixeira.collidepoint(pos_mouse) and self.item_selecionado_mochila_idx is not None:
            if self.item_selecionado_mochila_idx < len(player.mochila_itens):
                item = player.mochila_itens[self.item_selecionado_mochila_idx]
                if item.get("protegido"):
                    self.aviso_protecao = "inventario_item_bloqueado"
                    return 0
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
                    if player.amuletos_equipados[index].get("protegido"):
                        return
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

    def _itens_alquimia_validos(self, player):
        if len(self.itens_alquimia_indices) != 3:
            return False
        indices = sorted(self.itens_alquimia_indices)
        if any(indice >= len(player.mochila_itens) for indice in indices):
            return False
        itens = [player.mochila_itens[indice] for indice in indices]
        primeiro = itens[0]
        raridades = ("Comum", "Incomum", "Raro", "Épico", "Lendário", "Mítico")
        if primeiro.get("raridade") not in raridades[:-1]:
            return False
        return all(
            self._tipo_item(item) == "equip_arma"
            and not item.get("protegido")
            and item.get("raridade") == primeiro.get("raridade")
            and item.get("tipo_arma") == primeiro.get("tipo_arma")
            for item in itens
        )

    def _fundir_armas(self, player):
        if not self._itens_alquimia_validos(player):
            self.aviso_alquimia = "inventario_alquimia_invalidas"
            return False
        indices = sorted(self.itens_alquimia_indices)
        arma_base = player.mochila_itens[indices[0]]
        raridades = ("Comum", "Incomum", "Raro", "Épico", "Lendário", "Mítico")
        raridade_nova = raridades[raridades.index(arma_base["raridade"]) + 1]
        candidatas = [
            item for item in TODAS_ARMAS
            if item.get("raridade") == raridade_nova
            and item.get("tipo_arma") == arma_base.get("tipo_arma")
        ]
        if not candidatas:
            self.aviso_alquimia = "inventario_alquimia_sem_resultado"
            return False

        nova_arma = self._preparar_item(random.choice(candidatas))
        for indice in reversed(indices):
            player.mochila_itens.pop(indice)
        player.mochila_itens.append(nova_arma)
        registrar_item_no_index(nova_arma["nome"])
        self.itens_alquimia_indices.clear()
        self.aviso_alquimia = "inventario_alquimia_sucesso"
        return True
