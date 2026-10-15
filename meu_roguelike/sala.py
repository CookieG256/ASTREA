# sala.py
import random
import pygame
import math
from config import LARGURA, ALTURA, VERMELHO, AZUL, AMARELO, BRANCO, CINZA, CINZA_CLARO, VERDE, PRETO, ROXO, CIANO, RARIDADE_CORES, CONFIG_JOGO, FONTE_SYS, FONTE_GRANDE
from save import carregar_dados, salvar_dados
from banco_itens import TODAS_ARMAS

POOL_ITENS_LOJA = [
    {"nome": "Pistola Plasma", "tipo": "equip_arma", "tipo_arma": "ranged", "dano": 20, "cadencia": 250, "raridade": "Comum", "custo": 100},
    {"nome": "Arco Curto", "tipo": "equip_arma", "tipo_arma": "ranged", "dano": 25, "cadencia": 300, "raridade": "Comum", "custo": 110},
    {"nome": "Lança de Ferro", "tipo": "equip_arma", "tipo_arma": "melee", "dano": 35, "cadencia": 350, "raridade": "Épico", "custo": 160},
    {"nome": "Cajado Místico", "tipo": "equip_arma", "tipo_arma": "magico", "dano": 45, "cadencia": 500, "raridade": "Épico", "custo": 200},
    {"nome": "Katana Sombria", "tipo": "equip_arma", "tipo_arma": "melee", "dano": 55, "cadencia": 220, "raridade": "Lendário", "custo": 250},
    {"nome": "Anel da Fênix", "tipo": "amuletos", "efeito": "Reviver", "raridade": "Mítico", "custo": 500},
    {"nome": "Poção de Cura (+50 HP)", "tipo": "cura", "valor": 50, "raridade": "Comum", "custo": 30}
]

class Sala:
    def __init__(self, x, y, tipo="DESCONHECIDO"):
        self.grid_x = x
        self.grid_y = y
        self.tipo = tipo
        self.revelada = False
        self.vizinhos = {}
        self.limpa = True if tipo in ["INICIAL", "CURA", "LOJA", "CASSINO", "SACRIFICIO", "BAU"] else False
        self.inimigos = []
        self.moedas_no_chao = []
        self.orbes_cura = []
        self.baus = []
        self.boss_derrotado = False
        self.boss_ativo = False
        
        self.fase_chefe = 0  
        self.cassino_cliq = 0
        self.cassino_msg = "Pressione [G] para apostar (Custo: 30 Gold)"
        self.sacrificio_feito = False

        self.itens_ofertados = []
        self.loja_comprados = []

        self.total_ondas = random.randint(3, 5) if tipo not in ["INICIAL", "CURA", "LOJA", "CASSINO", "SACRIFICIO", "CHEFE", "BAU", "MIMICO"] else 0
        self.onda_atual = 0

    def revelar(self):
        self.revelada = True
        
        # --- SALA DE RECOMPENSA ---
        if self.tipo == "RECOMPENSA" and not self.baus:
            self.baus = [
                {"tipo": "moedas", "valor": 100, "rect": pygame.Rect(LARGURA//2 - 150, ALTURA//2, 60, 60), "aberto": False},
                {"tipo": "buff", "valor": "Dano Extra", "rect": pygame.Rect(LARGURA//2 + 90, ALTURA//2, 60, 60), "aberto": False}
            ]
        
        # --- SALA DO MÍMICO (Dois baús: um bom, um mímico) ---
        elif self.tipo == "MIMICO_SALA" and not self.baus:
            # Sorteia qual dos dois vai ser o mímico verdadeiro
            eh_mimico_direito = random.choice([True, False])
            self.baus = [
                {"tipo": "mimico" if not eh_mimico_direito else "recompensa", "rect": pygame.Rect(LARGURA//2 - 150, ALTURA//2, 60, 60), "aberto": False},
                {"tipo": "mimico" if eh_mimico_direito else "recompensa", "rect": pygame.Rect(LARGURA//2 + 90, ALTURA//2, 60, 60), "aberto": False}
            ]
    def desenhar_baus(self, tela):
        if hasattr(self, 'baus'):
            for bau in self.baus:
                if not bau["aberto"]:
                    # Desenha o baú (dourado) na tela
                    pygame.draw.rect(tela, (218, 165, 32), bau["rect"])

    def revelar(self):
        self.revelada = True
        if self.tipo == "LOJA" and not self.itens_ofertados:
            self.itens_ofertados = []
            
            # Queremos exatamente 5 itens sorteados para a vitrine
            while len(self.itens_ofertados) < 5:
                # Sorteio de 0.0 a 100.0 para definir a raridade do slot
                roll = random.uniform(0, 100)
                
                if roll <= 1.0: # 1% Mítico
                    raridade_alvo = "Mítico"
                elif roll <= 6.0: # 5% Lendário (acumulado de 1.0 a 6.0)
                    raridade_alvo = "Lendário"
                elif roll <= 21.0: # 15% Épico (6.0 a 21.0)
                    raridade_alvo = "Épico"
                elif roll <= 51.0: # 30% Raro (21.0 a 51.0)
                    raridade_alvo = "Raro"
                elif roll <= 81.0: # 30% Incomum
                    raridade_alvo = "Incomum"
                else: # Restante para Comum
                    raridade_alvo = "Comum"
                
                # Filtra todas as armas do banco_itens que têm a raridade sorteada
                candidatos = [arma for arma in TODAS_ARMAS if arma.get('raridade') == raridade_alvo]
                
                if candidatos:
                    escolhido = random.choice(candidatos)
                    # Evita colocar armas repetidas na mesma loja
                    if escolhido not in self.itens_ofertados:
                        # Garante que o item possui o campo "tipo" exigido pela loja
                        item_loja = escolhido.copy()
                        item_loja["tipo"] = "equip_arma"
                        # Preço proporcional ao dano e raridade
                        item_loja["custo"] = item_loja.get("custo", int(item_loja["dano"] * 4 + 20))
                        
                        self.itens_ofertados.append(item_loja)
                else:
                    # Fallback de segurança se não houver armas na raridade sorteada
                    escolhido = random.choice(TODAS_ARMAS).copy()
                    escolhido["tipo"] = "equip_arma"
                    escolhido["custo"] = int(escolhido["dano"] * 4 + 20)
                    if escolhido not in self.itens_ofertados:
                        self.itens_ofertados.append(escolhido)

            self.loja_comprados = [False] * len(self.itens_ofertados)

    def spawnar_boss_direto(self):
        self.inimigos.clear()
        fator_dificuldade = 1.5 if CONFIG_JOGO.get('modo_dificuldade') == 'DIFICIL' else 1.0
        hp_boss = int(1000 * fator_dificuldade)
        self.inimigos.append({
            'tipo': 'boss',
            'rect': pygame.Rect(LARGURA//2 - 40, ALTURA//2 - 40, 80, 80),
            'hp': hp_boss,
            'hp_max': hp_boss,
            'dano_contato': 30,
            'eh_boss': True,
            'nome': 'Chefe do Andar',
            'rage_ativado': False
        })
        self.boss_ativo = True
        self.fase_chefe = 1

    def spawnar_proxima_onda(self):
        if self.limpa: return
        if len(self.inimigos) > 0: return

        if self.tipo == "CHEFE":
            self.spawnar_boss_direto()
        elif self.tipo == "MIMICO":
            self.limpa = True
        else:
            if self.onda_atual < self.total_ondas:
                self.onda_atual += 1
                qtd_mobs = random.randint(3, 5)
                fator_dificuldade = 1.5 if CONFIG_JOGO.get('modo_dificuldade') == 'DIFICIL' else 1.0
                
                for _ in range(qtd_mobs):
                    rx = random.randint(150, LARGURA - 150)
                    ry = random.randint(150, ALTURA - 150)
                    tipo_mob = random.choice(['perto', 'tank', 'longe', 'curandeiro'])
                    
                    if tipo_mob == 'perto':
                        hp = int(40 * fator_dificuldade)
                        self.inimigos.append({'tipo': 'perto', 'rect': pygame.Rect(rx, ry, 25, 25), 'hp': hp, 'hp_max': hp, 'dano_contato': 15})
                    elif tipo_mob == 'tank':
                        hp = int(100 * fator_dificuldade)
                        self.inimigos.append({'tipo': 'tank', 'rect': pygame.Rect(rx, ry, 38, 38), 'hp': hp, 'hp_max': hp, 'dano_contato': 25})
                    elif tipo_mob == 'longe':
                        hp = int(30 * fator_dificuldade)
                        self.inimigos.append({'tipo': 'longe', 'rect': pygame.Rect(rx, ry, 25, 25), 'hp': hp, 'hp_max': hp, 'dano_contato': 10, 'ultimo_tiro': 0})
                    elif tipo_mob == 'curandeiro':
                        hp = int(35 * fator_dificuldade)
                        self.inimigos.append({'tipo': 'curandeiro', 'rect': pygame.Rect(rx, ry, 28, 28), 'hp': hp, 'hp_max': hp, 'dano_contato': 10, 'ultima_cura': 0})
            else:
                self.limpa = True

    def desenhar_conteudo_especial(self, tela, player, evento_tecla, particulas=None):
        if self.tipo == "LOJA":
            if not self.itens_ofertados:
                self.itens_ofertados = random.sample(POOL_ITENS_LOJA, min(5, len(POOL_ITENS_LOJA)))
                self.loja_comprados = [False] * len(self.itens_ofertados)

            txt_t = FONTE_GRANDE.render("LOJA", True, AMARELO)
            tela.blit(txt_t, (LARGURA//2 - txt_t.get_width()//2, 80))
            
            y_pos = 160
            for i, item in enumerate(self.itens_ofertados):
                comprado = self.loja_comprados[i]
                txt_status = "[ESGOTADO]" if comprado else f"[Custo: ${item['custo']}]"
                cor_txt = CINZA_CLARO if comprado else RARIDADE_CORES.get(item.get('raridade', 'Comum'), BRANCO)
                
                txt_item = FONTE_SYS.render(f"[{i+1}] {item['nome']} ({item.get('raridade','Comum')}) - {txt_status}", True, cor_txt)
                tela.blit(txt_item, (LARGURA//2 - txt_item.get_width()//2, y_pos))
                y_pos += 45

            if evento_tecla and evento_tecla.unicode.isdigit():
                tecla_num = int(evento_tecla.unicode) - 1
                if 0 <= tecla_num < len(self.itens_ofertados) and not self.loja_comprados[tecla_num]:
                    item = self.itens_ofertados[tecla_num]
                    if player.ouro >= item['custo']:
                        if item['tipo'] == 'cura':
                            player.ouro -= item['custo']
                            self.loja_comprados[tecla_num] = True
                            player.hp = min(player.hp_max, player.hp + item['valor'])
                            if particulas: particulas.criar_texto_dano(player.rect.centerx, player.rect.y - 15, f"+{item['valor']} HP", VERDE)
                        elif len(player.mochila_itens) < 9:
                            player.ouro -= item['custo']
                            self.loja_comprados[tecla_num] = True
                            player.mochila_itens.append(item)

        elif self.tipo == "BAU":
            txt_t = FONTE_GRANDE.render("SALA DE RECOMPENSAS", True, AMARELO)
            tela.blit(txt_t, (LARGURA//2 - txt_t.get_width()//2, 80))
            
            for bau in self.baus:
                cor_bau = (139, 69, 19) if not bau['aberto'] else (80, 40, 10)
                pygame.draw.rect(tela, cor_bau, bau['rect'], border_radius=4)
                pygame.draw.rect(tela, AMARELO, bau['rect'], 2, border_radius=4)
                
                if player.rect.colliderect(bau['rect']) and not bau['aberto']:
                    bau['aberto'] = True
                    player.ouro += 50
                    if particulas: particulas.criar_texto_dano(bau['rect'].centerx, bau['rect'].y - 15, "+50 Gold!", AMARELO)

        elif self.tipo == "CASSINO":
            txt_t = FONTE_GRANDE.render("CASSINO", True, ROXO)
            tela.blit(txt_t, (LARGURA//2 - txt_t.get_width()//2, 100))
            
            txt_inst = FONTE_SYS.render("[G] Apostar 30 Gold (50% de chance)", True, BRANCO)
            txt_res = FONTE_SYS.render(self.cassino_msg, True, AMARELO if "GANHOU" in self.cassino_msg else VERMELHO if "PERDEU" in self.cassino_msg else BRANCO)
            
            tela.blit(txt_inst, (LARGURA//2 - txt_inst.get_width()//2, 170))
            tela.blit(txt_res, (LARGURA//2 - txt_res.get_width()//2, 230))

            if evento_tecla and evento_tecla.key == pygame.K_g:
                if player.ouro >= 30:
                    player.ouro -= 30
                    self.cassino_cliq += 1
                    if random.random() < 0.5:
                        player.ouro += 60
                        self.cassino_msg = "VOCÊ GANHOU +60 DE OURO!"
                    else:
                        self.cassino_msg = "VOCÊ PERDEU!"
                else:
                    self.cassino_msg = "OURO INSUFICIENTE!"

        elif self.tipo == "SACRIFICIO":
            txt_t = FONTE_GRANDE.render("ALTAR DE SACRIFÍCIO", True, VERMELHO)
            tela.blit(txt_t, (LARGURA//2 - txt_t.get_width()//2, 100))
            
            if not self.sacrificio_feito:
                txt_1 = FONTE_SYS.render("[1] -15 HP Max por +50 Gold", True, BRANCO)
                txt_2 = FONTE_SYS.render("[2] -25 HP Max por +8 Dano Arma", True, BRANCO)
                txt_3 = FONTE_SYS.render("[3] -30 HP Max por +15% Mana Max", True, BRANCO)
                txt_4 = FONTE_SYS.render("[4] Sair", True, CINZA_CLARO)
                
                tela.blit(txt_1, (LARGURA//2 - txt_1.get_width()//2, 170))
                tela.blit(txt_2, (LARGURA//2 - txt_2.get_width()//2, 210))
                tela.blit(txt_3, (LARGURA//2 - txt_3.get_width()//2, 250))
                tela.blit(txt_4, (LARGURA//2 - txt_4.get_width()//2, 290))
                
                if evento_tecla:
                    if evento_tecla.key == pygame.K_1 and player.hp_max > 30:
                        player.hp_max -= 15; player.hp = min(player.hp, player.hp_max); player.ouro += 50; self.sacrificio_feito = True
                    elif evento_tecla.key == pygame.K_2 and player.hp_max > 40:
                        player.hp_max -= 25; player.hp = min(player.hp, player.hp_max)
                        if player.equipado_arma: player.equipado_arma['dano'] += 8
                        self.sacrificio_feito = True
                    elif evento_tecla.key == pygame.K_3 and player.hp_max > 45:
                        player.hp_max -= 30; player.hp = min(player.hp, player.hp_max); player.mana_max += 50; player.mana = min(player.mana_max, player.mana + 50); self.sacrificio_feito = True
                    elif evento_tecla.key == pygame.K_4:
                        self.sacrificio_feito = True
            else:
                txt_feito = FONTE_SYS.render("Altar finalizado. Você pode sair da sala.", True, CINZA_CLARO)
                tela.blit(txt_feito, (LARGURA//2 - txt_feito.get_width()//2, 210))

# --- Certifica-te de que está indentado dentro da classe Sala ---
    def desenhar_inimigos_e_moedas(self, tela, player, particulas=None, estatisticas_run=None):
        for inimigo in self.inimigos:
            if 'x' in inimigo and 'y' in inimigo:
                pos_x, pos_y = int(inimigo['x']), int(inimigo['y'])
            elif 'rect' in inimigo:
                pos_x, pos_y = inimigo['rect'].centerx, inimigo['rect'].centery
            else:
                continue
            pygame.draw.circle(tela, (255, 0, 0), (pos_x, pos_y), 12)
        velocidade_atracao = 12.0 if self.limpa else 4.0
        raio_alcance = 9999 if self.limpa else 70

        for m in self.moedas_no_chao[:]:
            mx, my = m['rect'].center
            px, py = player.rect.center
            dist = math.hypot(px - mx, py - my)
            
            if dist < raio_alcance and dist > 0:
                m['rect'].x += int((px - mx) / dist * velocidade_atracao)
                m['rect'].y += int((py - my) / dist * velocidade_atracao)

            eh_gema = m.get('tipo') == 'gema_ciano'
            cor_moeda = CIANO if eh_gema else AMARELO
            pygame.draw.circle(tela, cor_moeda, m['rect'].center, 7 if eh_gema else 6)
            pygame.draw.circle(tela, BRANCO if eh_gema else (200, 160, 0), m['rect'].center, 7 if eh_gema else 6, 1)

            if player.rect.colliderect(m['rect']):
                if eh_gema:
                    dados = carregar_dados()
                    dados['gemas'] = dados.get('gemas', 0) + m['valor']
                    salvar_dados(dados)
                    if particulas:
                        particulas.criar_texto_dano(player.rect.centerx, player.rect.y - 15, f"+{m['valor']} Gemas!", CIANO)
                else:
                    player.ouro += m['valor']
                self.moedas_no_chao.remove(m)

        raio_alcance_orbe = 9999 if self.limpa else 80
        for orbe in self.orbes_cura[:]:
            ox, oy = orbe['rect'].center
            px, py = player.rect.center
            dist = math.hypot(px - ox, py - oy)

            if dist < raio_alcance_orbe and dist > 0:
                orbe['rect'].x += int((px - ox) / dist * velocidade_atracao)
                orbe['rect'].y += int((py - oy) / dist * velocidade_atracao)

            pygame.draw.circle(tela, VERDE, orbe['rect'].center, 7)
            pygame.draw.circle(tela, BRANCO, orbe['rect'].center, 7, 1)

            if player.rect.colliderect(orbe['rect']):
                player.hp = min(player.hp_max, player.hp + orbe['cura'])
                if particulas:
                    particulas.criar_texto_dano(player.rect.centerx, player.rect.y - 15, f"+{orbe['cura']} HP", VERDE)
                self.orbes_cura.remove(orbe)

        for inimigo in self.inimigos:
            tipo = inimigo.get('tipo', 'perto')
            r = inimigo['rect']
            
            if tipo == 'perto':
                pygame.draw.polygon(tela, VERMELHO, [(r.centerx, r.top), (r.bottomleft[0], r.bottomleft[1]), (r.bottomright[0], r.bottomright[1])])
            elif tipo == 'tank':
                pygame.draw.rect(tela, VERMELHO, r)
            elif tipo == 'longe':
                pygame.draw.circle(tela, VERMELHO, r.center, r.width // 2)
            elif tipo == 'curandeiro':
                pygame.draw.circle(tela, AMARELO, r.center, r.width // 2)
            elif tipo == 'mimico':
                pygame.draw.rect(tela, (139, 69, 19), r, border_radius=4)
                pygame.draw.rect(tela, AMARELO, r, 2, border_radius=4)
            elif tipo == 'boss':
                pygame.draw.rect(tela, (180, 0, 0), r, border_radius=8)

            if tipo != 'boss':
                hp_perc = max(0, inimigo['hp'] / inimigo['hp_max'])
                pygame.draw.rect(tela, VERMELHO, (r.x, r.y - 8, r.width, 4))
                pygame.draw.rect(tela, (0, 255, 0), (r.x, r.y - 8, int(r.width * hp_perc), 4))

def desenhar_minimapa(tela, mapa_salas, sala_atual):
    largura_box, altura_box = 140, 140
    origem_box_x = LARGURA - largura_box - 20
    origem_box_y = 20

    pygame.draw.rect(tela, (20, 20, 30), (origem_box_x, origem_box_y, largura_box, altura_box), border_radius=8)
    pygame.draw.rect(tela, CINZA, (origem_box_x, origem_box_y, largura_box, altura_box), 2, border_radius=8)

    centro_x = origem_box_x + (largura_box // 2) - 8
    centro_y = origem_box_y + (altura_box // 2) - 8
    tam_quad = 16
    espaco = 4

    for (gx, gy), s in mapa_salas.items():
        dif_x = gx - sala_atual.grid_x
        dif_y = gy - sala_atual.grid_y

        px = centro_x + (dif_x * (tam_quad + espaco))
        py = centro_y + (dif_y * (tam_quad + espaco))

        if origem_box_x + 4 <= px <= origem_box_x + largura_box - 20 and origem_box_y + 4 <= py <= origem_box_y + altura_box - 20:
            if s.revelada:
                cor = VERDE if s == sala_atual else CINZA_CLARO
                if s.tipo == "LOJA": cor = AMARELO
                elif s.tipo == "CHEFE": cor = VERMELHO
                elif s.tipo == "CASSINO": cor = ROXO
                elif s.tipo == "SACRIFICIO": cor = VERMELHO
                elif s.tipo == "RECOMPENSA": cor = CIANO
                elif s.tipo == "MIMICO": cor = (139, 69, 19)
                pygame.draw.rect(tela, cor, (px, py, tam_quad, tam_quad), border_radius=3)
            else:
                pygame.draw.rect(tela, (40, 40, 50), (px, py, tam_quad, tam_quad), 1, border_radius=3)

def todas_salas_exploradas(mapa_salas):
    for s in mapa_salas.values():
        if not s.revelada:
            return False
    return True

def gerar_andar():
    qtd_salas = random.choice([8, 9, 10])
    salas = {}
    s_ini = Sala(0, 0, "INICIAL")
    s_ini.revelar()
    salas[(0, 0)] = s_ini
    
    lista_pos = [(0, 0)]
    direcoes = [('NORTE', (0, -1)), ('SUL', (0, 1)), ('LESTE', (1, 0)), ('OESTE', (-1, 0))]
    opostos = {'NORTE': 'SUL', 'SUL': 'NORTE', 'LESTE': 'OESTE', 'OESTE': 'LESTE'}

    while len(salas) < qtd_salas:
        px, py = random.choice(lista_pos)
        nome_dir, (dx, dy) = random.choice(direcoes)
        nx, ny = px + dx, py + dy
        if (nx, ny) not in salas:
            nova = Sala(nx, ny, "DESCONHECIDO")
            salas[(nx, ny)] = nova
            lista_pos.append((nx, ny))
            salas[(px, py)].vizinhos[nome_dir] = nova
            nova.vizinhos[opostos[nome_dir]] = salas[(px, py)]

    for pos1, s1 in salas.items():
        for pos2, s2 in salas.items():
            if pos1 != pos2:
                dx = pos2[0] - pos1[0]
                dy = pos2[1] - pos1[1]
                if dx == 1 and dy == 0: s1.vizinhos['LESTE'] = s2
                elif dx == -1 and dy == 0: s1.vizinhos['OESTE'] = s2
                elif dx == 0 and dy == 1: s1.vizinhos['SUL'] = s2
                elif dx == 0 and dy == -1: s1.vizinhos['NORTE'] = s2

    pos_ordenadas = sorted(salas.keys(), key=lambda p: abs(p[0]) + abs(p[1]))
    tipos_especiais = ["LOJA", "CASSINO", "SACRIFICIO", "RECOMPENSA", "MIMICO"]
    random.shuffle(tipos_especiais)

    for idx, pos in enumerate(pos_ordenadas):
        if pos == (0, 0): continue
        if idx == len(pos_ordenadas) - 1:
            salas[pos].tipo = "CHEFE"
            salas[pos].limpa = False
        elif idx <= len(tipos_especiais) - 1:
            salas[pos].tipo = tipos_especiais[idx - 1]
            salas[pos].limpa = True if salas[pos].tipo != "MIMICO" else False
        else:
            salas[pos].tipo = "NORMAL"

    return s_ini, salas