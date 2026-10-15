# tooltip.py
import pygame
from config import PRETO, BRANCO, RARIDADE_CORES, FONTE_SYS

def desenhar_tooltip(tela, item, pos_mouse):
    if not item: return

    nome = item.get('nome', 'Desconhecido')
    raridade = item.get('raridade', 'Comum')
    cor_raridade = RARIDADE_CORES.get(raridade, BRANCO)

    linhas = [f"{nome} ({raridade})"]
    if 'dano' in item: linhas.append(f"Dano: {item['dano']}")
    if 'valor' in item: linhas.append(f"Efeito/Valor: +{item['valor']}")
    if 'cadencia' in item: linhas.append(f"Cadência: {item['cadencia']}ms")
    if 'custo' in item: linhas.append(f"Preço: ${item['custo']}")
    if 'desc' in item: linhas.append(f"Desc: {item['desc']}")

    largura = max(FONTE_SYS.size(l)[0] for l in linhas) + 20
    altura = len(linhas) * 20 + 10

    mx, my = pos_mouse
    rx = min(mx + 15, 900 - largura - 10)
    ry = min(my + 15, 600 - altura - 10)

    rect_box = pygame.Rect(rx, ry, largura, altura)
    pygame.draw.rect(tela, (20, 20, 30), rect_box, border_radius=6)
    pygame.draw.rect(tela, cor_raridade, rect_box, 2, border_radius=6)

    y_off = ry + 5
    for i, linha in enumerate(linhas):
        cor_t = cor_raridade if i == 0 else BRANCO
        txt_s = FONTE_SYS.render(linha, True, cor_t)
        tela.blit(txt_s, (rx + 10, y_off))
        y_off += 20