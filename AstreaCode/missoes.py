from datetime import date
import random

import pygame

from config import (
    LARGURA, ALTURA, FUNDO_UI, PAINEL_UI, PAINEL_UI_CLARO, BORDA_UI,
    BRANCO, DOURADO_UI, CIANO_UI, ROXO_UI, VERDE, FONTE_SYS, FONTE_GRANDE,
)
from cosmeticos import desbloquear_cosmetico
from idiomas import t
from save import carregar_dados, salvar_dados


_DIARIAS = (
    ("diaria_abates", "abates", 20, 25, "titulo_cacador", "aura_astral"),
    ("diaria_elites", "elites", 2, 30, "titulo_predador", None),
    ("diaria_gemas", "gemas", 50, 25, "titulo_cacador", None),
    ("diaria_salas", "salas", 4, 30, "titulo_explorador", None),
    ("diaria_raros", "raros", 1, 40, "titulo_rastreador", "rosa_nebulosa"),
    ("diaria_andar", "andar", 3, 35, "titulo_desbravador", None),
    ("diaria_abates_rapidos", "abates", 35, 40, "titulo_exterminador", None),
    ("diaria_gemas_altas", "gemas", 100, 45, "titulo_cacador", None),
    ("diaria_salas_limpas", "salas", 7, 50, "titulo_veterano", None),
    ("diaria_elites_cacados", "elites", 4, 55, "titulo_predador", "chama_violeta"),
    ("diaria_chefe", "chefes", 1, 60, "titulo_matador_chefe", None),
    ("diaria_enigma", "enigmas", 1, 50, "titulo_explorador", "mar_de_estrelas"),
)

_SEMANAIS = (
    ("semanal_abates", "abates", 100, 100, "titulo_veterano", "chama_violeta"),
    ("semanal_elites", "elites", 15, 125, "titulo_predador", None),
    ("semanal_gemas", "gemas", 500, 125, "titulo_cacador", None),
    ("semanal_salas", "salas", 30, 150, "titulo_explorador", None),
    ("semanal_raros", "raros", 5, 160, "titulo_rastreador", "folha_dourada"),
    ("semanal_andares", "andar", 15, 175, "titulo_desbravador", None),
    ("semanal_abates_muitos", "abates", 250, 180, "titulo_exterminador", None),
    ("semanal_gemas_muitas", "gemas", 1000, 200, "titulo_cacador", "mar_de_estrelas"),
    ("semanal_elites_muitos", "elites", 30, 220, "titulo_predador", None),
    ("semanal_chefes", "chefes", 5, 250, "titulo_matador_chefe", "coroa_do_vazio"),
    ("semanal_salas_muitas", "salas", 60, 250, "titulo_veterano", None),
    ("semanal_craft", "craft", 5, 180, "titulo_ferreiro", None),
)

_PERMANENTES = (
    ("quest_abates", "quest", "abates", 50, 75, "titulo_exterminador", None),
    ("desafio_elites", "desafio", "elites", 3, 60, "titulo_predador", None),
    ("quest_andar_15", "quest", "andar", 15, 150, "titulo_desbravador", "coroa_do_vazio"),
    ("quest_resgatar_npcs", "quest", "npcs", 3, 120, "titulo_aliado", "folha_dourada"),
)

_NOMES_MISSOES = {
    "diaria_abates": ("Derrote inimigos", "Derrota enemigos", "Defeat enemies"),
    "diaria_elites": ("Derrote elites", "Derrota élites", "Defeat elites"),
    "diaria_gemas": ("Colete gemas", "Recoge gemas", "Collect gems"),
    "diaria_salas": ("Conclua salas", "Completa salas", "Complete rooms"),
    "diaria_raros": ("Derrote inimigos raros", "Derrota enemigos raros", "Defeat rare enemies"),
    "diaria_andar": ("Avance de andar", "Avanza de piso", "Advance floors"),
    "diaria_abates_rapidos": ("Derrote muitos inimigos", "Derrota muchos enemigos", "Defeat more enemies"),
    "diaria_gemas_altas": ("Reúna muitas gemas", "Reúne muchas gemas", "Gather more gems"),
    "diaria_salas_limpas": ("Explore e conclua salas", "Explora y completa salas", "Explore and clear rooms"),
    "diaria_elites_cacados": ("Cace elites", "Caza élites", "Hunt elites"),
    "diaria_chefe": ("Derrote um chefe", "Derrota a un jefe", "Defeat a boss"),
    "diaria_enigma": ("Resolva um enigma", "Resuelve un enigma", "Solve a riddle"),
    "semanal_abates": ("Derrote inimigos na semana", "Derrota enemigos esta semana", "Defeat enemies this week"),
    "semanal_elites": ("Derrote elites na semana", "Derrota élites esta semana", "Defeat elites this week"),
    "semanal_gemas": ("Colete gemas na semana", "Recoge gemas esta semana", "Collect gems this week"),
    "semanal_salas": ("Conclua salas na semana", "Completa salas esta semana", "Clear rooms this week"),
    "semanal_raros": ("Cace inimigos raros", "Caza enemigos raros", "Hunt rare enemies"),
    "semanal_andares": ("Avance pelos andares", "Avanza por los pisos", "Advance through floors"),
    "semanal_abates_muitos": ("Elimine uma grande horda", "Elimina una gran horda", "Defeat a large horde"),
    "semanal_gemas_muitas": ("Reúna uma fortuna em gemas", "Reúne una fortuna en gemas", "Gather a fortune in gems"),
    "semanal_elites_muitos": ("Derrote muitos elites", "Derrota muchos élites", "Defeat many elites"),
    "semanal_chefes": ("Derrote chefes", "Derrota jefes", "Defeat bosses"),
    "semanal_salas_muitas": ("Complete muitas salas", "Completa muchas salas", "Clear many rooms"),
    "semanal_craft": ("Fabrique equipamentos", "Fabrica equipo", "Craft equipment"),
    "quest_resgatar_npcs": ("Resgate todos os viajantes", "Rescata a todos los viajeros", "Rescue every traveler"),
}


def _periodo(tipo):
    hoje = date.today()
    if tipo == "diaria":
        return hoje.isoformat()
    ano, semana, _ = hoje.isocalendar()
    return f"{ano}-W{semana:02d}"


def _selecionar_rotacao(pool, tipo, periodo, quantidade):
    gerador = random.Random(f"{tipo}:{periodo}")
    return gerador.sample(pool, min(quantidade, len(pool)))


def atualizar_missoes(dados):
    estado = dados.setdefault("missoes", {})
    diaria = _periodo("diaria")
    semanal = _periodo("semanal")
    if dados.get("rotacao_missoes_diarias") != diaria:
        dados["rotacao_missoes_diarias"] = diaria
        dados["missoes_ativas_diarias"] = [
            missao[0] for missao in _selecionar_rotacao(_DIARIAS, "diaria", diaria, 4)
        ]
    if dados.get("rotacao_missoes_semanais") != semanal:
        dados["rotacao_missoes_semanais"] = semanal
        dados["missoes_ativas_semanais"] = [
            missao[0] for missao in _selecionar_rotacao(_SEMANAIS, "semanal", semanal, 4)
        ]
    ativas = (
        [missao for missao in _DIARIAS if missao[0] in dados["missoes_ativas_diarias"]]
        + [missao for missao in _SEMANAIS if missao[0] in dados["missoes_ativas_semanais"]]
    )
    for chave, _, _, _, _, _ in ativas:
        periodo = diaria if chave in dados["missoes_ativas_diarias"] else semanal
        atual = estado.setdefault(chave, {})
        if atual.get("periodo") != periodo:
            atual.update({"periodo": periodo, "progresso": 0, "resgatada": False})
    for chave, _, _, _, _, _, _ in _PERMANENTES:
        estado.setdefault(chave, {"periodo": "permanente", "progresso": 0, "resgatada": False})
    return estado


def registrar_progresso(dados, objetivo, quantidade=1):
    estado = atualizar_missoes(dados)
    quantidade = max(0, int(quantidade))
    rotacoes = (
        [missao for missao in _DIARIAS if missao[0] in dados["missoes_ativas_diarias"]]
        + [missao for missao in _SEMANAIS if missao[0] in dados["missoes_ativas_semanais"]]
    )
    configuracoes = [
        (chave, alvo) for chave, _, alvo, _, _, _ in rotacoes
    ] + [
        (chave, alvo) for chave, _, alvo, _, _, _, _ in _PERMANENTES
    ]
    alterou = False
    for chave, alvo in configuracoes:
        missao = estado[chave]
        if alvo == objetivo and not missao.get("resgatada"):
            missao["progresso"] += quantidade
            alterou = True
    if alterou:
        salvar_dados(dados)


def listar_missoes(dados):
    estado = atualizar_missoes(dados)
    rotacoes = (
        [("diaria", *missao) for missao in _DIARIAS if missao[0] in dados["missoes_ativas_diarias"]]
        + [("semanal", *missao) for missao in _SEMANAIS if missao[0] in dados["missoes_ativas_semanais"]]
    )
    permanentes = [
        (tipo, chave, objetivo, meta, gemas, titulo, cosmetico)
        for chave, tipo, objetivo, meta, gemas, titulo, cosmetico in _PERMANENTES
    ]
    resultado = []
    for tipo, chave, _objetivo, meta, gemas, titulo, cosmetico in rotacoes + permanentes:
        atual = estado[chave]
        resultado.append({
            "id": chave,
            "tipo": tipo,
            "progresso": atual.get("progresso", 0),
            "meta": meta,
            "gemas": gemas,
            "titulo": titulo,
            "cosmetico": cosmetico,
            "nome": _NOMES_MISSOES.get(chave),
            "resgatada": atual.get("resgatada", False),
        })
    return resultado


def resgatar_missao(dados, chave):
    estado = atualizar_missoes(dados)
    missao = next((item for item in listar_missoes(dados) if item["id"] == chave), None)
    if not missao or missao["resgatada"] or missao["progresso"] < missao["meta"]:
        return False
    estado[chave]["resgatada"] = True
    dados["gemas"] = int(dados.get("gemas", 0)) + missao["gemas"]
    dados.setdefault("titulos_desbloqueados", [])
    if missao["titulo"] not in dados["titulos_desbloqueados"]:
        dados["titulos_desbloqueados"].append(missao["titulo"])
    if missao["cosmetico"]:
        desbloquear_cosmetico(dados, missao["cosmetico"])
    salvar_dados(dados)
    return True


class TelaMissoes:
    def __init__(self):
        self.btn_voltar = pygame.Rect(LARGURA // 2 - 100, ALTURA - 58, 200, 38)
        self.botoes_resgate = {}
        self.categoria = "todas"
        self.botoes_categoria = {}
        self.scroll = 0

    def desenhar(self, tela, pos_mouse, config_jogo):
        lang = config_jogo.get("idioma", "PT")
        dados = carregar_dados()
        tela.fill(FUNDO_UI)
        titulo = FONTE_GRANDE.render(t("missoes_titulo", lang), True, DOURADO_UI)
        tela.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 28))
        self.botoes_categoria = {}
        categorias = (
            ("todas", "missoes_todas"),
            ("diaria", "missoes_diarias"),
            ("semanal", "missoes_semanais"),
            ("quest", "missoes_quests"),
            ("desafio", "missoes_desafios"),
        )
        for indice, (categoria, texto_chave) in enumerate(categorias):
            rect = pygame.Rect(85 + indice * 146, 70, 138, 32)
            self.botoes_categoria[categoria] = rect
            ativo = self.categoria == categoria
            hover = rect.collidepoint(pos_mouse)
            pygame.draw.rect(tela, PAINEL_UI_CLARO if hover or ativo else PAINEL_UI, rect, border_radius=7)
            pygame.draw.rect(tela, ROXO_UI if ativo or hover else BORDA_UI, rect, 2 if ativo else 1, border_radius=7)
            label = FONTE_SYS.render(t(texto_chave, lang), True, DOURADO_UI if ativo else BRANCO)
            tela.blit(label, (rect.centerx - label.get_width() // 2, rect.centery - label.get_height() // 2))
        self.botoes_resgate = {}
        missoes = [
            missao for missao in listar_missoes(dados)
            if self.categoria == "todas" or missao["tipo"] == self.categoria
        ]
        area_lista = pygame.Rect(90, 112, LARGURA - 180, ALTURA - 188)
        clip_anterior = tela.get_clip()
        tela.set_clip(area_lista)
        visiveis = missoes[self.scroll:self.scroll + 5]
        for indice, missao in enumerate(visiveis):
            rect = pygame.Rect(125, 112 + indice * 80, 650, 68)
            pygame.draw.rect(tela, PAINEL_UI, rect, border_radius=9)
            pygame.draw.rect(tela, BORDA_UI, rect, 1, border_radius=9)
            nomes = missao.get("nome")
            nome = nomes[{"PT": 0, "ES": 1, "EN": 2}.get(lang, 0)] if nomes else t("missao_" + missao["id"], lang)
            descricao = FONTE_SYS.render(f"{nome} · {missao['progresso']}/{missao['meta']}", True, BRANCO)
            tela.blit(descricao, (rect.x + 14, rect.y + 6))
            premio = FONTE_SYS.render(
                f"{t('recompensa', lang)}: {missao['gemas']} {t('gemas', lang)} · {t(missao['titulo'], lang)}",
                True, CIANO_UI,
            )
            tela.blit(premio, (rect.x + 14, rect.y + 38))
            if missao["progresso"] >= missao["meta"] and not missao["resgatada"]:
                botao = pygame.Rect(rect.right - 128, rect.y + 17, 112, 34)
                self.botoes_resgate[missao["id"]] = botao
                pygame.draw.rect(tela, PAINEL_UI_CLARO if botao.collidepoint(pos_mouse) else ROXO_UI, botao, border_radius=7)
                label = FONTE_SYS.render(t("resgatar", lang), True, BRANCO)
                tela.blit(label, (botao.centerx - label.get_width() // 2, botao.centery - label.get_height() // 2))
            elif missao["resgatada"]:
                label = FONTE_SYS.render(t("resgatada", lang), True, VERDE)
                tela.blit(label, (rect.right - label.get_width() - 18, rect.centery - label.get_height() // 2))
        tela.set_clip(clip_anterior)
        hover = self.btn_voltar.collidepoint(pos_mouse)
        pygame.draw.rect(tela, PAINEL_UI_CLARO if hover else PAINEL_UI, self.btn_voltar, border_radius=8)
        pygame.draw.rect(tela, ROXO_UI if hover else BORDA_UI, self.btn_voltar, 1, border_radius=8)
        voltar = FONTE_SYS.render(t("voltar", lang), True, DOURADO_UI)
        tela.blit(voltar, (self.btn_voltar.centerx - voltar.get_width() // 2, self.btn_voltar.centery - voltar.get_height() // 2))

    def tratar_evento(self, evento):
        dados = carregar_dados()
        missoes = [
            missao for missao in listar_missoes(dados)
            if self.categoria == "todas" or missao["tipo"] == self.categoria
        ]
        self.scroll = max(0, min(max(0, len(missoes) - 5), self.scroll - evento.y))

    def tratar_clique(self, pos_mouse):
        for categoria, rect in self.botoes_categoria.items():
            if rect.collidepoint(pos_mouse):
                self.categoria = categoria
                self.scroll = 0
                return None
        for chave, rect in self.botoes_resgate.items():
            if rect.collidepoint(pos_mouse):
                dados = carregar_dados()
                return "RESGATADA" if resgatar_missao(dados, chave) else None
        if self.btn_voltar.collidepoint(pos_mouse):
            return "VOLTAR"
        return None
