import pygame
from config import (
    LARGURA, BRANCO, AMARELO, FONTE_SYS, FONTE_GRANDE, RARIDADE_CORES,
    PAINEL_UI, PAINEL_UI_CLARO, BORDA_UI, DOURADO_UI, ROXO_UI, CINZA
)
from save import salvar_dados
from idiomas import t


class LojaPets:
    OPCOES = (
        ("robo", "pet_robo", 220, "Incomum", None),
        ("fenix", "pet_fenix", 100, "Raro", None),
        ("lobo", "pet_lobo", 125, "Incomum", None),
        ("tartaruga", "pet_tartaruga", 150, "Incomum", None),
        ("corvo", "pet_corvo", 175, "Raro", None),
        ("besouro", "pet_besouro", 260, "Raro", None),
        ("lince", "pet_lince", 320, "Épico", None),
        ("serpente", "pet_serpente", 380, "Épico", None),
        ("dragao", "pet_dragao", 1500, "Lendário", "andares_15"),
        ("guardiao_astral", "pet_guardiao_astral", 2000, "Mítico", "chefes_secretos_1"),
    )

    def __init__(self):
        self.botoes = {
            chave: pygame.Rect(LARGURA - 225, 168 + indice * 34, 145, 30)
            for indice, (chave, _, _, _, _) in enumerate(self.OPCOES)
        }
        self.mensagem = ""

    def desenhar(self, tela, dados_salvos, pos_mouse, lang="PT"):
        titulo = FONTE_GRANDE.render(t("aba_pets", lang), True, (50, 120, 230))
        tela.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 120))

        gemas = FONTE_SYS.render(f"{t('gemas', lang)}: {dados_salvos.get('gemas', 0)}", True, AMARELO)
        tela.blit(gemas, (LARGURA // 2 - gemas.get_width() // 2, 158))

        comprados = dados_salvos.get("pets_comprados", {})
        equipado = dados_salvos.get("pet_equipado")
        conquistas = dados_salvos.get("conquistas", {})
        for chave, chave_nome, custo, raridade, requisito in self.OPCOES:
            rect = self.botoes[chave]
            desbloqueado = requisito is None or requisito in conquistas
            pygame.draw.rect(tela, CINZA, (70, rect.y - 2, 760, 36), border_radius=6)
            texto_pet = FONTE_SYS.render(
                f"{t(chave_nome, lang)} · {t('raridade_' + raridade.lower(), lang)}",
                True, RARIDADE_CORES[raridade] if desbloqueado else (115, 115, 125),
            )
            tela.blit(texto_pet, (85, rect.y + 6))

            if equipado == chave:
                rotulo = "desequipar"
            elif comprados.get(chave):
                rotulo = "equipar"
            else:
                rotulo = "comprar" if desbloqueado else "pet_bloqueado"
            hover = rect.collidepoint(pos_mouse)
            cor = PAINEL_UI_CLARO if hover else PAINEL_UI
            pygame.draw.rect(tela, cor, rect, border_radius=7)
            pygame.draw.rect(
                tela, DOURADO_UI if equipado == chave else ROXO_UI if hover else BORDA_UI,
                rect, 2 if equipado == chave or hover else 1, border_radius=7,
            )
            texto_botao = t(rotulo, lang)
            if rotulo == "comprar":
                texto_botao = f"{texto_botao} ({custo})"
            elif rotulo == "pet_bloqueado":
                texto_botao = t("pet_requisito", lang)
            texto = FONTE_SYS.render(texto_botao, True, DOURADO_UI if equipado == chave or hover else BRANCO)
            tela.blit(texto, (rect.centerx - texto.get_width() // 2, rect.centery - texto.get_height() // 2))

        if self.mensagem:
            aviso = FONTE_SYS.render(t(self.mensagem, lang), True, AMARELO)
            tela.blit(aviso, (LARGURA // 2 - aviso.get_width() // 2, 555))

    def tratar_clique(self, pos_mouse, dados_salvos):
        for chave, _, custo, _, requisito in self.OPCOES:
            if not self.botoes[chave].collidepoint(pos_mouse):
                continue

            if requisito and requisito not in dados_salvos.get("conquistas", {}):
                self.mensagem = "pet_bloqueado"
                return False
            comprados = dados_salvos.setdefault("pets_comprados", {})
            if dados_salvos.get("pet_equipado") == chave:
                dados_salvos["pet_equipado"] = None
            elif comprados.get(chave):
                dados_salvos["pet_equipado"] = chave
            else:
                gemas = dados_salvos.get("gemas", 0)
                if gemas < custo:
                    self.mensagem = "gemas_insuficientes"
                    return False
                dados_salvos["gemas"] = gemas - custo
                comprados[chave] = True
                dados_salvos["pet_equipado"] = chave

            salvar_dados(dados_salvos)
            self.mensagem = ""
            return True
        return False
