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

    def criar_texto_dano(self, x, y, texto, cor, critico=False):
        self.textos_flutuantes.append({
            'x': x, 'y': y,
            'texto': str(texto),
            'cor': cor,
            'vida': 38 if critico else 30,
            'critico': critico,
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
            fonte_popup = pygame.font.Font(
                None, 28 if t.get("critico") else 19
            )
            txt_surf = fonte_popup.render(t['texto'], True, t['cor'])
            tela.blit(txt_surf, (int(t['x'] - txt_surf.get_width() / 2), int(t['y'])))
            if t['vida'] <= 0:
                self.textos_flutuantes.remove(t)
