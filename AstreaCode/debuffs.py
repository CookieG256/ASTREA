# debuffs.py
import pygame
from config import arredondar_para_5, obter_modo_dificuldade

class GerenciadorStatus:
    def __init__(self):
        self.status_ativos = {}

    def adicionar_efeito(self, nome, tipo, duracao_ms, valor=0):
        dificuldade = obter_modo_dificuldade()
        if tipo == "debuff" and dificuldade == "EASY":
            return
        if tipo == "debuff" and dificuldade == "HARDCORE":
            duracao_ms = int(duracao_ms * 1.5)
        tempo_atual = pygame.time.get_ticks()
        self.status_ativos[nome] = {
            'tipo': tipo,
            'fim': tempo_atual + duracao_ms,
            'valor': valor,
            'ultimo_tick': tempo_atual
        }

    def atualizar(self, stats_jogador, tempo_atual):
        remover = []
        stats_jogador["multiplicador_velocidade"] = 1.0
        stats_jogador["multiplicador_dano"] = 1.0
        stats_jogador["multiplicador_dano_recebido"] = 1.0
        stats_jogador["pode_curar"] = True
        for nome, dados in self.status_ativos.items():
            if tempo_atual > dados['fim']:
                remover.append(nome)
                continue

            if nome == 'queimadura':
                if tempo_atual - dados['ultimo_tick'] >= 1000:
                    stats_jogador['hp'] = max(1, stats_jogador['hp'] - arredondar_para_5(5))
                    dados['ultimo_tick'] = tempo_atual

            elif nome == 'veneno':
                stats_jogador['pode_curar'] = False
                if tempo_atual - dados['ultimo_tick'] >= 500:
                    stats_jogador['hp'] = max(1, stats_jogador['hp'] - max(5, arredondar_para_5(2)))
                    dados['ultimo_tick'] = tempo_atual
            elif nome == 'sangramento':
                if tempo_atual - dados['ultimo_tick'] >= 700:
                    stats_jogador['hp'] = max(1, stats_jogador['hp'] - max(5, arredondar_para_5(dados['valor'])))
                    dados['ultimo_tick'] = tempo_atual
            elif nome == 'lentidao':
                stats_jogador["multiplicador_velocidade"] = min(
                    stats_jogador["multiplicador_velocidade"],
                    max(0.25, 1.0 - dados["valor"]),
                )
            elif nome == 'fraqueza':
                stats_jogador["multiplicador_dano"] = min(
                    stats_jogador["multiplicador_dano"],
                    max(0.25, 1.0 - dados["valor"]),
                )
            elif nome == 'atordoamento':
                stats_jogador["multiplicador_velocidade"] = 0.0
            elif nome == 'maldicao':
                stats_jogador["multiplicador_dano"] = min(
                    stats_jogador["multiplicador_dano"],
                    max(0.25, 1.0 - dados["valor"]),
                )
            elif nome == 'vulnerabilidade':
                stats_jogador["multiplicador_dano_recebido"] = max(
                    stats_jogador["multiplicador_dano_recebido"],
                    1.0 + dados["valor"],
                )
            elif nome == "exaustao":
                stats_jogador["multiplicador_velocidade"] = min(
                    stats_jogador["multiplicador_velocidade"], 0.7
                )
                stats_jogador["multiplicador_dano"] = min(
                    stats_jogador["multiplicador_dano"], 0.8
                )
            elif nome == "cegueira":
                stats_jogador["multiplicador_dano"] = min(
                    stats_jogador["multiplicador_dano"], 0.75
                )
            elif nome == "corrosao":
                stats_jogador["multiplicador_dano_recebido"] = max(
                    stats_jogador["multiplicador_dano_recebido"], 1.2
                )
            elif nome == "regeneracao":
                if tempo_atual - dados["ultimo_tick"] >= 1000:
                    stats_jogador["hp"] = min(
                        stats_jogador.get("hp_max", stats_jogador["hp"]),
                        stats_jogador["hp"] + max(5, arredondar_para_5(dados["valor"])),
                    )
                    dados["ultimo_tick"] = tempo_atual
            elif nome == "foco":
                stats_jogador["multiplicador_dano"] = max(
                    stats_jogador["multiplicador_dano"], 1.0 + dados["valor"]
                )

        for nome in remover:
            if nome == 'veneno':
                stats_jogador['pode_curar'] = True
            del self.status_ativos[nome]