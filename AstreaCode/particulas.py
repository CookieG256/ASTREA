# particulas.py
import pygame
import random

class GerenciadorParticulas:
    def __init__(self):
        self.particulas = []
        self.textos_flutuantes = []

    def criar_explosao(self, x, y, cor):
        for _ in range(8):
            self.particulas.append({
                'x': x, 'y': y,
                'vx': random.uniform(-3, 3),
                'vy': random.uniform(-3, 3),
                'vida': random.randint(15, 25),
                'cor': cor
            })

    def criar_texto_dano(self, x, y, texto, cor, destaque=False):
        self.textos_flutuantes.append({
            'x': x, 'y': y,
            'texto': str(texto),
            'cor': cor,
            'vida': 36 if destaque else 30,
            'destaque': destaque,
        })

    def atualizar_e_desenhar(self, tela, fonte):
        for p in self.particulas[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vida'] -= 1
            pygame.draw.circle(tela, p['cor'], (int(p['x']), int(p['y'])), 3)
            if p['vida'] <= 0:
                self.particulas.remove(p)

        for t in self.textos_flutuantes[:]:
            t['y'] -= 1
            t['vida'] -= 1
            txt_surf = fonte.render(t['texto'], True, t['cor'])
            if t.get('destaque'):
                txt_surf = pygame.transform.scale(
                    txt_surf,
                    (max(1, int(txt_surf.get_width() * 1.2)), max(1, int(txt_surf.get_height() * 1.2))),
                )
            tela.blit(txt_surf, (t['x'], t['y']))
            if t['vida'] <= 0:
                self.textos_flutuantes.remove(t)
