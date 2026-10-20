import math
import random

import pygame

from banco_itens import TODAS_ARMAS, sortear_arma_por_classe
from config import (
    ALTURA,
    BORDA_UI,
    BRANCO,
    CIANO_UI,
    DOURADO_UI,
    FONTE_GRANDE,
    FONTE_PEQUENA,
    FONTE_SYS,
    FUNDO_UI,
    LARGURA,
    PAINEL_UI,
    PAINEL_UI_CLARO,
    ROXO_UI,
    CONFIG_JOGO,
)
from idiomas import t
from narrativa import NPCS
from reliquias import conceder_reliquia
from save import carregar_dados, salvar_dados

PRECOS_SERVICOS = {
    "cartografo": 40,
    "curandeira": 50,
    "ferreiro": 70,
    "alquimista": 45,
    "mercadora": 35,
    "oraculo": 65,
    "treinador": 55,
    "guardiao": 60,
}

POSICOES_NPCS = (
    (170, 190), (355, 190), (545, 190), (730, 190),
    (170, 330), (355, 330), (545, 330), (730, 330),
)


class SalaNPCs:
    def __init__(self):
        self.jogador = pygame.Vector2(LARGURA // 2, ALTURA - 95)
        self.alvo_npc = None
        self.botao_comprar = pygame.Rect(LARGURA // 2 + 12, ALTURA - 83, 188, 36)
        self.botao_voltar = pygame.Rect(LARGURA // 2 - 100, ALTURA - 40, 200, 30)
        self.botao_pet = pygame.Rect(LARGURA - 215, ALTURA - 42, 200, 32)
        self.rects_npcs = {}
        self.aviso = ""
        self._ultima_atualizacao = pygame.time.get_ticks()

    def atualizar(self):
        agora = pygame.time.get_ticks()
        dt = min(0.05, max(0.0, (agora - self._ultima_atualizacao) / 1000))
        self._ultima_atualizacao = agora
        teclas = pygame.key.get_pressed()
        dx = int(teclas[pygame.K_d] or teclas[pygame.K_RIGHT]) - int(
            teclas[pygame.K_a] or teclas[pygame.K_LEFT]
        )
        dy = int(teclas[pygame.K_s] or teclas[pygame.K_DOWN]) - int(
            teclas[pygame.K_w] or teclas[pygame.K_UP]
        )
        if dx or dy:
            direcao = pygame.Vector2(dx, dy).normalize()
            self.jogador += direcao * 225 * dt
        self.jogador.x = max(92, min(LARGURA - 92, self.jogador.x))
        self.jogador.y = max(112, min(ALTURA - 105, self.jogador.y))

    def _npc_proximo(self):
        candidatos = [
            (math.dist(self.jogador, pos), npc_id)
            for npc_id, pos in self.rects_npcs.items()
        ]
        if not candidatos:
            return None
        distancia, npc_id = min(candidatos)
        return npc_id if distancia <= 78 else None

    def tratar_tecla(self, tecla, idioma):
        if tecla == pygame.K_ESCAPE:
            if self.alvo_npc:
                self.alvo_npc = None
            else:
                return "VOLTAR"
        elif tecla == pygame.K_e:
            if self.alvo_npc:
                return "COMPRAR"
            self.alvo_npc = self._npc_proximo()
            if not self.alvo_npc:
                self.aviso = t("npc_hub_distante", idioma)
        return None

    def tratar_clique(self, pos_mouse):
        if self.botao_pet.collidepoint(pos_mouse):
            return "EVOLUIR_PET"
        if self.botao_voltar.collidepoint(pos_mouse):
            self.alvo_npc = None
            return "VOLTAR"
        if self.alvo_npc and self.botao_comprar.collidepoint(pos_mouse):
            return "COMPRAR"
        return None

    def evoluir_pet(self, idioma):
        dados = carregar_dados()
        pet = dados.get("pet_equipado")
        if not pet:
            return t("pet_sem_mascote", idioma)
        niveis = dados.setdefault("pet_niveis", {})
        nivel = max(1, min(5, int(niveis.get(pet, 1))))
        if nivel >= 5:
            return t("pet_nivel_maximo", idioma)
        custo = nivel * 100
        if int(dados.get("gemas", 0)) < custo:
            return t("gemas_insuficientes", idioma)
        dados["gemas"] -= custo
        niveis[pet] = nivel + 1
        salvar_dados(dados)
        return t("pet_nivel", idioma).format(nivel=nivel + 1)

    def desenhar(self, tela, pos_mouse, idioma, dados=None):
        dados = dados or carregar_dados()
        tela.fill(FUNDO_UI)
        pygame.draw.rect(tela, (31, 27, 48), (54, 68, LARGURA - 108, ALTURA - 115), border_radius=22)
        pygame.draw.rect(tela, (15, 13, 27), (68, 82, LARGURA - 136, ALTURA - 143), border_radius=18)
        pygame.draw.rect(tela, BORDA_UI, (54, 68, LARGURA - 108, ALTURA - 115), 3, border_radius=22)

        titulo = FONTE_GRANDE.render(t("npc_hub_titulo", idioma), True, ROXO_UI)
        tela.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 18))
        instrucoes = FONTE_PEQUENA.render(t("npc_hub_controles", idioma), True, BRANCO)
        tela.blit(instrucoes, (LARGURA // 2 - instrucoes.get_width() // 2, 54))

        self.rects_npcs = {}
        desbloqueados = set(dados.get("npcs_resgatados", []))
        pendentes = dados.get("preparacao_npc_run", {})
        for indice, (npc_id, npc) in enumerate(NPCS.items()):
            if npc_id not in desbloqueados:
                continue
            centro = POSICOES_NPCS[indice]
            self.rects_npcs[npc_id] = centro
            ativo = npc_id == self.alvo_npc
            cor = (115, 76, 176) if ativo else (55, 75, 111)
            pygame.draw.circle(tela, (8, 9, 18), (centro[0], centro[1] + 4), 26)
            pygame.draw.circle(tela, cor, centro, 23)
            pygame.draw.circle(tela, DOURADO_UI if ativo else CIANO_UI, centro, 23, 2)
            simbolo = FONTE_GRANDE.render(npc["simbolo"], True, BRANCO)
            tela.blit(simbolo, (centro[0] - simbolo.get_width() // 2, centro[1] - simbolo.get_height() // 2))
            nome = FONTE_PEQUENA.render(t(f"npc_nome_{npc_id}", idioma), True, DOURADO_UI)
            servico = FONTE_PEQUENA.render(t(f"npc_servico_{npc_id}", idioma), True, BRANCO)
            tela.blit(nome, (centro[0] - nome.get_width() // 2, centro[1] + 29))
            tela.blit(servico, (centro[0] - servico.get_width() // 2, centro[1] + 46))
            if npc_id in pendentes:
                selo = FONTE_PEQUENA.render(t("npc_hub_preparado", idioma), True, CIANO_UI)
                tela.blit(selo, (centro[0] - selo.get_width() // 2, centro[1] + 63))

        pygame.draw.circle(tela, ROXO_UI, (round(self.jogador.x), round(self.jogador.y)), 13)
        pygame.draw.circle(tela, BRANCO, (round(self.jogador.x), round(self.jogador.y)), 13, 2)
        npc_proximo = self._npc_proximo()
        if npc_proximo and not self.alvo_npc:
            prompt = FONTE_SYS.render(
                f"{t('npc_interagir', idioma)} [E] · {t(f'npc_nome_{npc_proximo}', idioma)}",
                True, DOURADO_UI,
            )
            tela.blit(prompt, (LARGURA // 2 - prompt.get_width() // 2, ALTURA - 97))

        if not desbloqueados:
            bloqueio = FONTE_SYS.render(t("npc_hub_sem_desbloqueados", idioma), True, BRANCO)
            tela.blit(bloqueio, (LARGURA // 2 - bloqueio.get_width() // 2, ALTURA // 2))

        if self.alvo_npc and self.alvo_npc in desbloqueados:
            self._desenhar_dialogo(tela, pos_mouse, idioma, pendentes)
        if self.aviso:
            aviso = FONTE_PEQUENA.render(self.aviso, True, DOURADO_UI)
            tela.blit(aviso, (LARGURA // 2 - aviso.get_width() // 2, ALTURA - 121))

        pet_atual = dados.get("pet_equipado")
        nivel_pet = int(dados.get("pet_niveis", {}).get(pet_atual, 1)) if pet_atual else 0
        pet_custo = nivel_pet * 100
        nivel_texto = t("pet_nivel", idioma).format(nivel=nivel_pet) if pet_atual else t("pet_sem_mascote", idioma)
        nivel_render = FONTE_PEQUENA.render(nivel_texto, True, DOURADO_UI)
        tela.blit(nivel_render, (LARGURA - 225, ALTURA - 83))
        hover_pet = self.botao_pet.collidepoint(pos_mouse)
        pygame.draw.rect(
            tela, PAINEL_UI_CLARO if hover_pet else PAINEL_UI,
            self.botao_pet, border_radius=7,
        )
        pygame.draw.rect(
            tela, CIANO_UI if hover_pet else BORDA_UI,
            self.botao_pet, 1, border_radius=7,
        )
        rotulo_pet = (
            t("pet_evoluir", idioma).format(custo=pet_custo)
            if pet_atual and nivel_pet < 5
            else t("pet_nivel_maximo", idioma) if pet_atual
            else t("pet_sem_mascote", idioma)
        )
        pet_label = FONTE_PEQUENA.render(rotulo_pet, True, BRANCO)
        tela.blit(
            pet_label,
            (self.botao_pet.centerx - pet_label.get_width() // 2,
             self.botao_pet.centery - pet_label.get_height() // 2),
        )

        hover = self.botao_voltar.collidepoint(pos_mouse)
        pygame.draw.rect(tela, PAINEL_UI_CLARO if hover else PAINEL_UI, self.botao_voltar, border_radius=7)
        pygame.draw.rect(tela, ROXO_UI if hover else BORDA_UI, self.botao_voltar, 1, border_radius=7)
        voltar = FONTE_PEQUENA.render(t("voltar_menu", idioma), True, BRANCO)
        tela.blit(voltar, (self.botao_voltar.centerx - voltar.get_width() // 2, self.botao_voltar.centery - voltar.get_height() // 2))

    def _desenhar_dialogo(self, tela, pos_mouse, idioma, pendentes):
        npc_id = self.alvo_npc
        painel = pygame.Rect(180, ALTURA - 170, LARGURA - 360, 95)
        pygame.draw.rect(tela, PAINEL_UI, painel, border_radius=10)
        pygame.draw.rect(tela, DOURADO_UI, painel, 1, border_radius=10)
        nome = FONTE_SYS.render(t(f"npc_nome_{npc_id}", idioma), True, DOURADO_UI)
        descricao = FONTE_PEQUENA.render(t(f"npc_desc_{npc_id}", idioma), True, BRANCO)
        tela.blit(nome, (painel.x + 14, painel.y + 8))
        tela.blit(descricao, (painel.x + 14, painel.y + 33))
        comprado = npc_id in pendentes
        chave = "npc_hub_preparado" if comprado else "npc_hub_comprar"
        texto = (
            t(chave, idioma)
            if comprado
            else t(chave, idioma).format(preco=PRECOS_SERVICOS[npc_id])
        )
        hover = self.botao_comprar.collidepoint(pos_mouse)
        pygame.draw.rect(tela, PAINEL_UI_CLARO if hover else (42, 64, 77), self.botao_comprar, border_radius=7)
        pygame.draw.rect(tela, CIANO_UI if hover else BORDA_UI, self.botao_comprar, 1, border_radius=7)
        label = FONTE_PEQUENA.render(texto, True, BRANCO)
        tela.blit(label, (self.botao_comprar.centerx - label.get_width() // 2, self.botao_comprar.centery - label.get_height() // 2))
        dica = FONTE_PEQUENA.render(t("npc_hub_confirmar", idioma), True, BRANCO)
        tela.blit(dica, (painel.x + 14, painel.bottom - 23))


def comprar_servico_npc(npc_id):
    if npc_id not in PRECOS_SERVICOS:
        return False, "npc_compra_invalida"
    dados = carregar_dados()
    if npc_id not in dados.get("npcs_resgatados", []):
        return False, "npc_nao_desbloqueado"
    preparacao = dados.setdefault("preparacao_npc_run", {})
    if npc_id in preparacao:
        return False, "npc_servico_ja_comprado"
    preco = PRECOS_SERVICOS[npc_id]
    if int(dados.get("gemas", 0)) < preco:
        return False, "npc_sem_gemas"

    servico = {"npc_id": npc_id}
    if npc_id == "ferreiro":
        armas_comuns = [
            arma for arma in TODAS_ARMAS
            if arma.get("raridade") in ("Comum", "Incomum")
        ]
        if not armas_comuns:
            return False, "npc_servico_indisponivel"
        arma = dict(
            sortear_arma_por_classe(
                armas_comuns, CONFIG_JOGO.get("classe_jogador", "Guerreiro")
            ),
            tipo="equip_arma",
        )
        if arma.get("tipo_arma") == "ranged":
            dano = max(1, int(arma.get("dano", 15)))
            municao = max(4, min(16, int(180 / dano)))
            arma.update({
                "municao_max": municao,
                "municao": municao,
                "recarga_ms": 1400,
                "recarregando_ate": 0,
            })
        servico["arma"] = arma
    elif npc_id == "oraculo":
        servico["reliquia"] = random.choice(("vitalidade", "berserker", "arcana"))
    dados["gemas"] -= preco
    preparacao[npc_id] = servico
    salvar_dados(dados)
    return True, "npc_compra_sucesso"


def aplicar_servicos_npc(player, servicos):
    for npc_id, dados_servico in servicos.items():
        if npc_id == "cartografo":
            player.sorte_run = getattr(player, "sorte_run", 0.0) + 0.15
        elif npc_id == "curandeira":
            player.pocoes_run = getattr(player, "pocoes_run", 0) + 2
        elif npc_id == "ferreiro":
            arma = dados_servico.get("arma")
            if isinstance(arma, dict):
                player.equipado_arma = dict(arma)
        elif npc_id == "alquimista":
            player.mana_max += 20
            player.mana = player.mana_max
            player.defesa_percent = min(0.7, player.defesa_percent + 0.08)
        elif npc_id == "mercadora":
            player.ouro += 100
        elif npc_id == "oraculo":
            reliquia = dados_servico.get("reliquia")
            if reliquia:
                conceder_reliquia(player, reliquia)
        elif npc_id == "treinador":
            player.buffs_run["dano"] += 0.10
        elif npc_id == "guardiao":
            player.hp_max += 40
            player.hp = min(player.hp_max, player.hp + 40)
