# debuffs.py
import pygame

class GerenciadorStatus:
    def __init__(self):
        self.status_ativos = {}

    def adicionar_efeito(self, nome, tipo, duracao_ms, valor=0):
        tempo_atual = pygame.time.get_ticks()
        self.status_ativos[nome] = {
            'tipo': tipo,
            'fim': tempo_atual + duracao_ms,
            'valor': valor,
            'ultimo_tick': tempo_atual
        }

    def atualizar(self, stats_jogador, tempo_atual):
        remover = []
        for nome, dados in self.status_ativos.items():
            if tempo_atual > dados['fim']:
                remover.append(nome)
                continue

            if nome == 'queimadura':
                if tempo_atual - dados['ultimo_tick'] >= 1000:
                    stats_jogador['hp'] = max(1, stats_jogador['hp'] - 5)
                    dados['ultimo_tick'] = tempo_atual

            elif nome == 'veneno':
                stats_jogador['pode_curar'] = False
                if tempo_atual - dados['ultimo_tick'] >= 500:
                    stats_jogador['hp'] = max(1, stats_jogador['hp'] - 2)
                    dados['ultimo_tick'] = tempo_atual

        for nome in remover:
            if nome == 'veneno':
                stats_jogador['pode_curar'] = True
            del self.status_ativos[nome]