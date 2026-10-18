# tooltip.py
import pygame
from config import BRANCO, RARIDADE_CORES, FONTE_SYS

def desenhar_tooltip(tela, item, pos_mouse):
    if not item: return

    nome = item.get('nome', 'Desconhecido')
    raridade = item.get('raridade', 'Comum')
    cor_raridade = RARIDADE_CORES.get(raridade, BRANCO)

    linhas = [f"{nome} ({raridade})"]
    if 'dano' in item: linhas.append(f"Dano: {item['dano']}")
    if 'valor_hp' in item: linhas.append(f"Vida máxima: +{item['valor_hp']}")
    if 'valor_vel' in item: linhas.append(f"Velocidade: +{item['valor_vel']}")
    if 'valor' in item: linhas.append(f"Efeito/Valor: +{item['valor']}")
    if 'cadencia' in item: linhas.append(f"Cadência: {item['cadencia']} ms")
    if 'custo' in item: linhas.append(f"Preço: ${item['custo']}")
    if 'desc' in item: linhas.extend(_quebrar(item['desc'], 290))

    largura = min(320, max(FONTE_SYS.size(l)[0] for l in linhas) + 20)
    altura = len(linhas) * 18 + 12

    mx, my = pos_mouse
    rx = max(8, min(mx + 15, 900 - largura - 8))
    ry = max(8, min(my + 15, 600 - altura - 8))

    rect_box = pygame.Rect(rx, ry, largura, altura)
    pygame.draw.rect(tela, (20, 20, 30), rect_box, border_radius=6)
    pygame.draw.rect(tela, cor_raridade, rect_box, 2, border_radius=6)

    y_off = ry + 5
    for i, linha in enumerate(linhas):
        cor_t = cor_raridade if i == 0 else BRANCO
        txt_s = FONTE_SYS.render(linha, True, cor_t)
        tela.blit(txt_s, (rx + 10, y_off))
        y_off += 18


def _quebrar(texto, largura):
    linhas = []
    atual = ""
    for palavra in str(texto).split():
        candidato = f"{atual} {palavra}".strip()
        if atual and FONTE_SYS.size(candidato)[0] > largura:
            linhas.append(atual)
            atual = palavra
        else:
            atual = candidato
    if atual:
        linhas.append(atual)
    return linhas