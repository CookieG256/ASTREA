# banco_itens.py
import random
from config import RARIDADE_CORES, BRANCO, CINZA, VERDE, ROXO, AMARELO, VERMELHO, CIANO, LARANJA, AZUL, PRETO
from save import carregar_dados, salvar_dados

# Cores por Raridade
CORES_RARIDADE = {
    "Comum": CINZA,
    "Incomum": VERDE,
    "Raro": AZUL,
    "Épico": ROXO,
    "Lendário": AMARELO,
    "Mítico": VERMELHO
}

# --- DICIONÁRIO COMPLETO DE ARMAS (174 Armas) ---
TODAS_ARMAS = [
    # === MELEE COMUNS (25) ===
    {"nome": "Espada Curta de Ferro", "tipo_arma": "melee", "raridade": "Comum", "dano": 12, "cadencia": 450, "desc": "Espada simples de ferro forjado."},
    {"nome": "Adaga Enferrujada", "tipo_arma": "melee", "raridade": "Comum", "dano": 8, "cadencia": 250, "desc": "Pequena e rápida, mas pouco afiada."},
    {"nome": "Machado de Lenhador", "tipo_arma": "melee", "raridade": "Comum", "dano": 18, "cadencia": 600, "desc": "Pesado e lente, causa bom dano."},
    {"nome": "Lança de Madeira", "tipo_arma": "melee", "raridade": "Comum", "dano": 11, "cadencia": 420, "desc": "Lança artesanal com ponta afiada."},
    {"nome": "Clava de Pedra", "tipo_arma": "melee", "raridade": "Comum", "dano": 15, "cadencia": 550, "desc": "Uma pedra amarrada a um pedaço de pau."},
    {"nome": "Foice Simples", "tipo_arma": "melee", "raridade": "Comum", "dano": 10, "cadencia": 350, "desc": "Usada na agricultura, serve para defesa."},
    {"nome": "Espada de Treino", "tipo_arma": "melee", "raridade": "Comum", "dano": 7, "cadencia": 300, "desc": "Feita de madeira leve para praticar."},
    {"nome": "Martelo Curto", "tipo_arma": "melee", "raridade": "Comum", "dano": 14, "cadencia": 500, "desc": "Ferramenta de ferreiro adaptada."},
    {"nome": "Cimitarra Básica", "tipo_arma": "melee", "raridade": "Comum", "dano": 13, "cadencia": 400, "desc": "Lâmina curva para cortes rápidos."},
    {"nome": "Faca de Caça", "tipo_arma": "melee", "raridade": "Comum", "dano": 9, "cadencia": 280, "desc": "Lâmina afiada para esfolar e golpear."},
    {"nome": "Estilete de Cobre", "tipo_arma": "melee", "raridade": "Comum", "dano": 8, "cadencia": 220, "desc": "Extremamente leve e veloz."},
    {"nome": "Facão de Trilha", "tipo_arma": "melee", "raridade": "Comum", "dano": 13, "cadencia": 430, "desc": "Corta mato e inimigos com facilidade."},
    {"nome": "Espada Rústica", "tipo_arma": "melee", "raridade": "Comum", "dano": 12, "cadencia": 440, "desc": "Forjada sem capricho, mas funcional."},
    {"nome": "Maça de Ferro Batido", "tipo_arma": "melee", "raridade": "Comum", "dano": 16, "cadencia": 520, "desc": "Causa dano de impacto direto."},
    {"nome": "Lança de Pederneira", "tipo_arma": "melee", "raridade": "Comum", "dano": 12, "cadencia": 410, "desc": "Ponta de pedra lascada muito pontiaguda."},
    {"nome": "Espada Rota", "tipo_arma": "melee", "raridade": "Comum", "dano": 9, "cadencia": 380, "desc": "Lâmina desgastada com marcas de uso."},
    {"nome": "Punhal de Osso", "tipo_arma": "melee", "raridade": "Comum", "dano": 10, "cadencia": 260, "desc": "Esculpido em fêmur de monstro."},
    {"nome": "Machado de Dormente", "tipo_arma": "melee", "raridade": "Comum", "dano": 17, "cadencia": 580, "desc": "Desequilibrado, mas com grande impacto."},
    {"nome": "Glaive Simples", "tipo_arma": "melee", "raridade": "Comum", "dano": 14, "cadencia": 480, "desc": "Lâmina acoplada a uma haste longa."},
    {"nome": "Alabarda de Ferro", "tipo_arma": "melee", "raridade": "Comum", "dano": 16, "cadencia": 530, "desc": "Mistura de machado e lança."},
    {"nome": "Martelo de Ferreiro", "tipo_arma": "melee", "raridade": "Comum", "dano": 15, "cadencia": 510, "desc": "Pesado o bastante para quebrar ossos."},
    {"nome": "Rapieira de Treino", "tipo_arma": "melee", "raridade": "Comum", "dano": 10, "cadencia": 320, "desc": "Focada em estocadas diretas."},
    {"nome": "Cimitarra de Aço Leve", "tipo_arma": "melee", "raridade": "Comum", "dano": 13, "cadencia": 390, "desc": "Equilibrada para ataques ágeis."},
    {"nome": "Mangual Rústico", "tipo_arma": "melee", "raridade": "Comum", "dano": 15, "cadencia": 540, "desc": "Esfera de ferro presa por corrente."},
    {"nome": "Espada Curta de Bronze", "tipo_arma": "melee", "raridade": "Comum", "dano": 11, "cadencia": 420, "desc": "Metal antigo, porém resistente."},

    # === RANGED COMUNS (25) ===
    {"nome": "Arco de Caça Simples", "tipo_arma": "ranged", "raridade": "Comum", "dano": 10, "cadencia": 400, "desc": "Arco de madeira básico para iniciantes."},
    {"nome": "Besta de Mão", "tipo_arma": "ranged", "raridade": "Comum", "dano": 14, "cadencia": 550, "desc": "Dispara virotes com boa precisão."},
    {"nome": "Zarabatana", "tipo_arma": "ranged", "raridade": "Comum", "dano": 6, "cadencia": 200, "desc": "Atira dardos rápidos e leves."},
    {"nome": "Estilingue de Precisão", "tipo_arma": "ranged", "raridade": "Comum", "dano": 8, "cadencia": 300, "desc": "Atira pedras arredondadas."},
    {"nome": "Arco Rústico de Freixo", "tipo_arma": "ranged", "raridade": "Comum", "dano": 11, "cadencia": 420, "desc": "Madeira flexível com bom alcance."},
    {"nome": "Pistola de Pederneira Antiga", "tipo_arma": "ranged", "raridade": "Comum", "dano": 22, "cadencia": 800, "desc": "Muito lenta, mas dano elevado."},
    {"nome": "Mini-Besta", "tipo_arma": "ranged", "raridade": "Comum", "dano": 12, "cadencia": 480, "desc": "Compacta e de fácil manuseio."},
    {"nome": "Arco Curto de Cobre", "tipo_arma": "ranged", "raridade": "Comum", "dano": 9, "cadencia": 380, "desc": "Reforçado com hastes de cobre."},
    {"nome": "Lançador de Dardos", "tipo_arma": "ranged", "raridade": "Comum", "dano": 7, "cadencia": 250, "desc": "Dispara múltiplos dardos curtos."},
    {"nome": "Besta Leve", "tipo_arma": "ranged", "raridade": "Comum", "dano": 13, "cadencia": 500, "desc": "Mecanismo simples de gatilho."},
    {"nome": "Arco de Corda Simples", "tipo_arma": "ranged", "raridade": "Comum", "dano": 8, "cadencia": 350, "desc": "Corda de fibra vegetal reforçada."},
    {"nome": "Estilingue de Ferro", "tipo_arma": "ranged", "raridade": "Comum", "dano": 10, "cadencia": 320, "desc": "Usa esferas de metal como munição."},
    {"nome": "Zarabatana de Bambu", "tipo_arma": "ranged", "raridade": "Comum", "dano": 7, "cadencia": 210, "desc": "Leve e fácil de soprar."},
    {"nome": "Arco de Bétula", "tipo_arma": "ranged", "raridade": "Comum", "dano": 10, "cadencia": 390, "desc": "Madeira clara e resistente."},
    {"nome": "Besta de Madeira", "tipo_arma": "ranged", "raridade": "Comum", "dano": 12, "cadencia": 490, "desc": "Estrutura robusta de carvalho."},
    {"nome": "Arco de Caçador Inexperiente", "tipo_arma": "ranged", "raridade": "Comum", "dano": 9, "cadencia": 370, "desc": "Trabalhado à mão para sobrevivência."},
    {"nome": "Pistola de Chumbo", "tipo_arma": "ranged", "raridade": "Comum", "dano": 20, "cadencia": 750, "desc": "Atira projéteis pesados de chumbo."},
    {"nome": "Arco Curto Retorcido", "tipo_arma": "ranged", "raridade": "Comum", "dano": 11, "cadencia": 410, "desc": "Design curvado para maior força."},
    {"nome": "Besta Dobrável", "tipo_arma": "ranged", "raridade": "Comum", "dano": 11, "cadencia": 440, "desc": "Fácil de guardar no inventário."},
    {"nome": "Lançador de Esferas", "tipo_arma": "ranged", "raridade": "Comum", "dano": 8, "cadencia": 290, "desc": "Dispara esferas de argila rígida."},
    {"nome": "Arco de Junco", "tipo_arma": "ranged", "raridade": "Comum", "dano": 7, "cadencia": 310, "desc": "Simples, mas atinge alvos com precisão."},
    {"nome": "Besta de Cobre", "tipo_arma": "ranged", "raridade": "Comum", "dano": 13, "cadencia": 510, "desc": "Virotes impulsionados por mola de cobre."},
    {"nome": "Arco Padrão da Patrulha", "tipo_arma": "ranged", "raridade": "Comum", "dano": 11, "cadencia": 400, "desc": "Arma militar básica de guarda."},
    {"nome": "Zarabatana Envenenada Fraca", "tipo_arma": "ranged", "raridade": "Comum", "dano": 8, "cadencia": 230, "desc": "Dardos embebidos em toxina leve."},
    {"nome": "Besta Compacta", "tipo_arma": "ranged", "raridade": "Comum", "dano": 12, "cadencia": 460, "desc": "Virotes menores para rápido disparo."},

    # === MAGE COMUNS (25) ===
    {"nome": "Varinha de Eucalipto", "tipo_arma": "mage", "raridade": "Comum", "dano": 9, "cadencia": 320, "desc": "Conduz pequenas faíscas mágicas."},
    {"nome": "Cajado de Madeira Podre", "tipo_arma": "mage", "raridade": "Comum", "dano": 13, "cadencia": 480, "desc": "Antigo, mas mantém resquícios de magia."},
    {"nome": "Orbe de Fogo Fraco", "tipo_arma": "mage", "raridade": "Comum", "dano": 11, "cadencia": 390, "desc": "Emite labaredas de fogo fátuo."},
    {"nome": "Livro de Magias Rasgado", "tipo_arma": "mage", "raridade": "Comum", "dano": 10, "cadencia": 350, "desc": "Páginas mofadas com feitiços básicos."},
    {"nome": "Varinha de Vidro", "tipo_arma": "mage", "raridade": "Comum", "dano": 8, "cadencia": 280, "desc": "Frágil, mas canaliza mana rapidamente."},
    {"nome": "Cajado do Aprendiz", "tipo_arma": "mage", "raridade": "Comum", "dano": 12, "cadencia": 420, "desc": "Usado em academias de magia."},
    {"nome": "Orbe de Gelo Instável", "tipo_arma": "mage", "raridade": "Comum", "dano": 10, "cadencia": 370, "desc": "Atira fragmentos de gelo fino."},
    {"nome": "Varinha de Carvalho Simples", "tipo_arma": "mage", "raridade": "Comum", "dano": 9, "cadencia": 310, "desc": "Resistente e confiável para feitiços."},
    {"nome": "Cajado de Iniciante", "tipo_arma": "mage", "raridade": "Comum", "dano": 11, "cadencia": 410, "desc": "Gema bruta encravada no topo."},
    {"nome": "Orbe de Centelha", "tipo_arma": "mage", "raridade": "Comum", "dano": 10, "cadencia": 340, "desc": "Libera pequenas descargas elétricas."},
    {"nome": "Grimório de Anotações", "tipo_arma": "mage", "raridade": "Comum", "dano": 9, "cadencia": 330, "desc": "Anotações de estudantes de arcana."},
    {"nome": "Varinha de Cobre", "tipo_arma": "mage", "raridade": "Comum", "dano": 8, "cadencia": 290, "desc": "Metal condutor para pequenas magias."},
    {"nome": "Cajado Curto de Osso", "tipo_arma": "mage", "raridade": "Comum", "dano": 12, "cadencia": 450, "desc": "Canaliza energia necrótica fraca."},
    {"nome": "Orbe de Brilho Fraco", "tipo_arma": "mage", "raridade": "Comum", "dano": 9, "cadencia": 360, "desc": "Ilumina o caminho e dispara fótons."},
    {"nome": "Livro de Encantamentos Básicos", "tipo_arma": "mage", "raridade": "Comum", "dano": 10, "cadencia": 380, "desc": "Contém receitas simples de ataque."},
    {"nome": "Varinha de Salgueiro", "tipo_arma": "mage", "raridade": "Comum", "dano": 8, "cadencia": 270, "desc": "Flexível para feitiços de vento."},
    {"nome": "Cajado de Ramo Seco", "tipo_arma": "mage", "raridade": "Comum", "dano": 11, "cadencia": 430, "desc": "Encontrado em florestas antigas."},
    {"nome": "Orbe de Energia Estática", "tipo_arma": "mage", "raridade": "Comum", "dano": 10, "cadencia": 350, "desc": "Causa choque leve ao impacto."},
    {"nome": "Pergaminho Mágico Rasgado", "tipo_arma": "mage", "raridade": "Comum", "dano": 9, "cadencia": 300, "desc": "Projeta runas mágicas no ar."},
    {"nome": "Varinha de Cristal Opaco", "tipo_arma": "mage", "raridade": "Comum", "dano": 9, "cadencia": 320, "desc": "Cristal com pureza baixa."},
    {"nome": "Cajado do Noviço", "tipo_arma": "mage", "raridade": "Comum", "dano": 12, "cadencia": 440, "desc": "Entregue aos sacerdotes iniciantes."},
    {"nome": "Orbe de Sombra Fraca", "tipo_arma": "mage", "raridade": "Comum", "dano": 11, "cadencia": 390, "desc": "Projéteis de escuridão concentrada."},
    {"nome": "Grimório do Conhecimento", "tipo_arma": "mage", "raridade": "Comum", "dano": 10, "cadencia": 360, "desc": "Foco básico de meditação e ataque."},
    {"nome": "Varinha de Zinco", "tipo_arma": "mage", "raridade": "Comum", "dano": 8, "cadencia": 280, "desc": "Barata e leve de carregar."},
    {"nome": "Cajado de Madeira de Lei", "tipo_arma": "mage", "raridade": "Comum", "dano": 13, "cadencia": 460, "desc": "Madeira densa que amplia feitiços."},

    # === INCOMUNS (16 Melee, 16 Ranged, 16 Mage) ===
    {"nome": "Espada Longa de Aço", "tipo_arma": "melee", "raridade": "Incomum", "dano": 22, "cadencia": 420, "desc": "Excelente equilíbrio e corte proficiente."},
    {"nome": "Machado de Batalha Duplo", "tipo_arma": "melee", "raridade": "Incomum", "dano": 30, "cadencia": 580, "desc": "Duas lâminas para decapitar monstros."},
    {"nome": "Lança de Infantaria", "tipo_arma": "melee", "raridade": "Incomum", "dano": 20, "cadencia": 390, "desc": "Haste longa com ponta de aço temperado."},
    {"nome": "Mangual de Espinhos", "tipo_arma": "melee", "raridade": "Incomum", "dano": 26, "cadencia": 520, "desc": "Esfera pontiaguda que perfura armaduras."},
    {"nome": "Rapieira Rápida", "tipo_arma": "melee", "raridade": "Incomum", "dano": 18, "cadencia": 280, "desc": "Estocadas letais em tempo recorde."},
    {"nome": "Espada Bastarda", "tipo_arma": "melee", "raridade": "Incomum", "dano": 24, "cadencia": 460, "desc": "Pode ser usada com uma ou duas mãos."},
    {"nome": "Cimitarra de Aço Reforçado", "tipo_arma": "melee", "raridade": "Incomum", "dano": 21, "cadencia": 380, "desc": "Lâmina curva polida e cortante."},
    {"nome": "Maça Pesada de Guerra", "tipo_arma": "melee", "raridade": "Incomum", "dano": 28, "cadencia": 560, "desc": "Esmaga escudos e ossos."},
    {"nome": "Glaive de Combate", "tipo_arma": "melee", "raridade": "Incomum", "dano": 23, "cadencia": 440, "desc": "Varredura circular devastadora."},
    {"nome": "Espada Falchion", "tipo_arma": "melee", "raridade": "Incomum", "dano": 22, "cadencia": 410, "desc": "Lâmina pesada na ponta para maior dano."},
    {"nome": "Machado de Duas Mãos", "tipo_arma": "melee", "raridade": "Incomum", "dano": 32, "cadencia": 620, "desc": "Requer força bruta para manusear."},
    {"nome": "Lança de Cavalaria", "tipo_arma": "melee", "raridade": "Incomum", "dano": 25, "cadencia": 480, "desc": "Projetada para investidas diretas."},
    {"nome": "Adaga Sombria", "tipo_arma": "melee", "raridade": "Incomum", "dano": 16, "cadencia": 240, "desc": "Ideal para ataques críticos surpresa."},
    {"nome": "Espada de Aço Azul", "tipo_arma": "melee", "raridade": "Incomum", "dano": 23, "cadencia": 400, "desc": "Liga metálica especial e leve."},
    {"nome": "Mangual Pesado", "tipo_arma": "melee", "raridade": "Incomum", "dano": 27, "cadencia": 550, "desc": "Duas esferas de aço na corrente."},
    {"nome": "Katana de Prata", "tipo_arma": "melee", "raridade": "Incomum", "dano": 21, "cadencia": 340, "desc": "Corta demônios com facilidade."},

    {"nome": "Arco Composto de Caça", "tipo_arma": "ranged", "raridade": "Incomum", "dano": 19, "cadencia": 380, "desc": "Roldanas aumentam a força do disparo."},
    {"nome": "Besta Pesada", "tipo_arma": "ranged", "raridade": "Incomum", "dano": 27, "cadencia": 580, "desc": "Perfura escudos de madeira facilmente."},
    {"nome": "Arco Longo Reforçado", "tipo_arma": "ranged", "raridade": "Incomum", "dano": 21, "cadencia": 420, "desc": "Alcance estendido e alta precisão."},
    {"nome": "Metralhadora de Flechas", "tipo_arma": "ranged", "raridade": "Incomum", "dano": 12, "cadencia": 210, "desc": "Dispara projéteis em rajada rápida."},
    {"nome": "Arco de Chifre", "tipo_arma": "ranged", "raridade": "Incomum", "dano": 20, "cadencia": 390, "desc": "Feito com chifre de besta selvagem."},
    {"nome": "Besta de Repetição", "tipo_arma": "ranged", "raridade": "Incomum", "dano": 16, "cadencia": 320, "desc": "Carregador com capacidade para 5 virotes."},
    {"nome": "Arco Recurvo de Aço", "tipo_arma": "ranged", "raridade": "Incomum", "dano": 22, "cadencia": 410, "desc": "Combinação de aço e fibra para tensão."},
    {"nome": "Besta de Cerco Média", "tipo_arma": "ranged", "raridade": "Incomum", "dano": 29, "cadencia": 620, "desc": "Poder de impacto estrondoso."},
    {"nome": "Arco de Caçador Experiente", "tipo_arma": "ranged", "raridade": "Incomum", "dano": 20, "cadencia": 370, "desc": "Equilibrado para tiros no ponto fraco."},
    {"nome": "Pistola Dupla de Pederneira", "tipo_arma": "ranged", "raridade": "Incomum", "dano": 31, "cadencia": 720, "desc": "Dois canos para disparos potentes."},
    {"nome": "Arco de Precisão Rápida", "tipo_arma": "ranged", "raridade": "Incomum", "dano": 18, "cadencia": 330, "desc": "Gatilho de soltura instantânea."},
    {"nome": "Besta de Aço Reforçado", "tipo_arma": "ranged", "raridade": "Incomum", "dano": 25, "cadencia": 540, "desc": "Estrutura de aço para maior durabilidade."},
    {"nome": "Arco de Espinheiro", "tipo_arma": "ranged", "raridade": "Incomum", "dano": 19, "cadencia": 360, "desc": "Flechas saem com energia da floresta."},
    {"nome": "Besta Tática", "tipo_arma": "ranged", "raridade": "Incomum", "dano": 23, "cadencia": 480, "desc": "Mira acoplada para tiros certeiros."},
    {"nome": "Arco de Alta Tensão", "tipo_arma": "ranged", "raridade": "Incomum", "dano": 22, "cadencia": 430, "desc": "Exige braços fortes para puxar a corda."},
    {"nome": "Arbalete de Campanha", "tipo_arma": "ranged", "raridade": "Incomum", "dano": 26, "cadencia": 530, "desc": "Arma de atiradores de elite do reino."},

    {"nome": "Cajado de Runas Brancas", "tipo_arma": "mage", "raridade": "Incomum", "dano": 20, "cadencia": 400, "desc": "Runas entalhadas purificam o disparo."},
    {"nome": "Orbe de Plasma Menor", "tipo_arma": "mage", "raridade": "Incomum", "dano": 18, "cadencia": 330, "desc": "Atira esferas de energia incandescente."},
    {"nome": "Grimório de Elementos", "tipo_arma": "mage", "raridade": "Incomum", "dano": 21, "cadencia": 390, "desc": "Alterna disparos de fogo e gelo."},
    {"nome": "Varinha de Cristal de Rocha", "tipo_arma": "mage", "raridade": "Incomum", "dano": 17, "cadencia": 290, "desc": "Focus arcano de cristal purificado."},
    {"nome": "Cajado de Ametista", "tipo_arma": "mage", "raridade": "Incomum", "dano": 22, "cadencia": 410, "desc": "Pedra púrpura amplia o alcance arcano."},
    {"nome": "Orbe de Fogo Fátuo", "tipo_arma": "mage", "raridade": "Incomum", "dano": 19, "cadencia": 350, "desc": "Esferas perseguem alvos levemente."},
    {"nome": "Livro de Feitiços Raros", "tipo_arma": "mage", "raridade": "Incomum", "dano": 21, "cadencia": 380, "desc": "Magias de destruição intermediárias."},
    {"nome": "Varinha de Ferro Mágico", "tipo_arma": "mage", "raridade": "Incomum", "dano": 18, "cadencia": 310, "desc": "Inquebrável e com condutividade de mana."},
    {"nome": "Cajado de Batalha Arcano", "tipo_arma": "mage", "raridade": "Incomum", "dano": 23, "cadencia": 430, "desc": "Pode ser usado para bater e conjurar."},
    {"nome": "Orbe de Gelo Profundo", "tipo_arma": "mage", "raridade": "Incomum", "dano": 19, "cadencia": 360, "desc": "Congela a trajetória do ar."},
    {"nome": "Grimório de Evocação", "tipo_arma": "mage", "raridade": "Incomum", "dano": 20, "cadencia": 370, "desc": "Evoca projéteis de energia etérea."},
    {"nome": "Varinha de Ébano", "tipo_arma": "mage", "raridade": "Incomum", "dano": 17, "cadencia": 280, "desc": "Madeira negra que absorve calor."},
    {"nome": "Cajado do Mago Viajante", "tipo_arma": "mage", "raridade": "Incomum", "dano": 21, "cadencia": 400, "desc": "Encantado para longas jornadas."},
    {"nome": "Orbe de Relâmpago Concentrado", "tipo_arma": "mage", "raridade": "Incomum", "dano": 18, "cadencia": 300, "desc": "Dispara fasíscas de alta voltagem."},
    {"nome": "Livro de Runas Antigas", "tipo_arma": "mage", "raridade": "Incomum", "dano": 22, "cadencia": 390, "desc": "Linguagem esquecida dos magos."},
    {"nome": "Varinha de Safira Menor", "tipo_arma": "mage", "raridade": "Incomum", "dano": 19, "cadencia": 320, "desc": "Gema azul reluzente e veloz."},

      # === RARAS (10 Melee, 10 Ranged, 10 Mage) ===
    {"nome": "Katana Sombria", "tipo_arma": "melee", "raridade": "Raro", "dano": 38, "cadencia": 300, "desc": "Lâmina rápida encharcada em sombras."},
    {"nome": "Machado do Carniceiro", "tipo_arma": "melee", "raridade": "Raro", "dano": 50, "cadencia": 550, "desc": "Causa sangramento maciço nos alvos."},
    {"nome": "Lança do Trovão", "tipo_arma": "melee", "raridade": "Raro", "dano": 36, "cadencia": 360, "desc": "Ataques soltam faíscas elétricas."},
    {"nome": "Espada de Obsidiana", "tipo_arma": "melee", "raridade": "Raro", "dano": 42, "cadencia": 420, "desc": "Lâmina feita de vidro vulcânico negro."},
    {"nome": "Cimitarra do Deserto Escaldante", "tipo_arma": "melee", "raridade": "Raro", "dano": 39, "cadencia": 330, "desc": "Ataques queimam a carne do inimigo."},
    {"nome": "Greatsword do Julgamento", "tipo_arma": "melee", "raridade": "Raro", "dano": 55, "cadencia": 600, "desc": "Espada colossal sagrada."},
    {"nome": "Adaga do Assassino Silencioso", "tipo_arma": "melee", "raridade": "Raro", "dano": 30, "cadencia": 180, "desc": "Velocidade de ataque impressionante."},
    {"nome": "Maça de Magma", "tipo_arma": "melee", "raridade": "Raro", "dano": 48, "cadencia": 520, "desc": "Goteja lava ardente a cada golpe."},
    {"nome": "Lança das Profundezas", "tipo_arma": "melee", "raridade": "Raro", "dano": 40, "cadencia": 380, "desc": "Forjada no fundo do oceano."},
    {"nome": "Espada do Vento Cortante", "tipo_arma": "melee", "raridade": "Raro", "dano": 37, "cadencia": 310, "desc": "Gera lâminas de ar ao atacar."},

    {"nome": "Arco do Falcão de Vento", "tipo_arma": "ranged", "raridade": "Raro", "dano": 34, "cadencia": 290, "desc": "Dispara flechas com velocidade do vento."},
    {"nome": "Besta de Aço Negro", "tipo_arma": "ranged", "raridade": "Raro", "dano": 46, "cadencia": 500, "desc": "Virotes pesados que empurram os alvos."},
    {"nome": "Arco Élfico Ancestral", "tipo_arma": "ranged", "raridade": "Raro", "dano": 36, "cadencia": 320, "desc": "Trabalhado pelos antigos elfos da floresta."},
    {"nome": "Arbalete de Precisão Mágica", "tipo_arma": "ranged", "raridade": "Raro", "dano": 44, "cadencia": 480, "desc": "Flechas teleguiadas em curta distância."},
    {"nome": "Arco de Cristal Lunar", "tipo_arma": "ranged", "raridade": "Raro", "dano": 38, "cadencia": 340, "desc": "Brilha sob o luar e congela alvos."},
    {"nome": "Besta de Disparo Rápido Mágico", "tipo_arma": "ranged", "raridade": "Raro", "dano": 28, "cadencia": 200, "desc": "Chuva constante de virotes de mana."},
    {"nome": "Arco do Caçador Estelar", "tipo_arma": "ranged", "raridade": "Raro", "dano": 37, "cadencia": 310, "desc": "Flechas reluzentes como constelações."},
    {"nome": "Arbalete Pesada de Precisão", "tipo_arma": "ranged", "raridade": "Raro", "dano": 49, "cadencia": 530, "desc": "Perfura múltiplos inimigos em linha."},
    {"nome": "Arco Solar", "tipo_arma": "ranged", "raridade": "Raro", "dano": 40, "cadencia": 350, "desc": "Dispara projéteis de pura luz solar."},
    {"nome": "Besta de Fogo Gélido", "tipo_arma": "ranged", "raridade": "Raro", "dano": 42, "cadencia": 420, "desc": "Combina queimadura e lentidão."},

    {"nome": "Cajado do Caos", "tipo_arma": "mage", "raridade": "Raro", "dano": 38, "cadencia": 320, "desc": "Dispara esferas de pura energia caótica."},
    {"nome": "Orbe de Energia Estelar", "tipo_arma": "mage", "raridade": "Raro", "dano": 35, "cadencia": 270, "desc": "Canaliza rajadas de meteoros menores."},
    {"nome": "Grimório do Eclipse", "tipo_arma": "mage", "raridade": "Raro", "dano": 41, "cadencia": 360, "desc": "Combina poder de luz e escuridão."},
    {"nome": "Varinha de Plasma Puro", "tipo_arma": "mage", "raridade": "Raro", "dano": 32, "cadencia": 220, "desc": "Dispara feixes de plasma contínuo."},
    {"nome": "Cajado do Tsunami", "tipo_arma": "mage", "raridade": "Raro", "dano": 39, "cadencia": 350, "desc": "Lança projéteis de água pressurizada."},
    {"nome": "Orbe de Chamas Eternas", "tipo_arma": "mage", "raridade": "Raro", "dano": 43, "cadencia": 390, "desc": "Explosões de fogo ao atingir alvos."},
    {"nome": "Grimório das Dimensões", "tipo_arma": "mage", "raridade": "Raro", "dano": 37, "cadencia": 310, "desc": "Projéteis surgem de portais arcanos."},
    {"nome": "Varinha de Cristal Sonoro", "tipo_arma": "mage", "raridade": "Raro", "dano": 33, "cadencia": 250, "desc": "Ondas de choque sônicas."},
    {"nome": "Cajado do Mago de Batalha", "tipo_arma": "mage", "raridade": "Raro", "dano": 42, "cadencia": 380, "desc": "Poder devastador de área."},
    {"nome": "Orbe de Gravidade Zero", "tipo_arma": "mage", "raridade": "Raro", "dano": 36, "cadencia": 290, "desc": "Empurra inimigos para longe."},

    # === LENDÁRIAS (6 Melee, 6 Ranged, 6 Mage) ===
    {"nome": "Lâmina do Sol Nascente", "tipo_arma": "melee", "raridade": "Lendário", "dano": 75, "cadencia": 250, "desc": "Corta o ar com chamas solares puras."},
    {"nome": "Ceifadora de Almas de Titã", "tipo_arma": "melee", "raridade": "Lendário", "dano": 95, "cadencia": 480, "desc": "Rouba vida e absorve almas dos mortos."},
    {"nome": "Espada do Dragão Ancestral", "tipo_arma": "melee", "raridade": "Lendário", "dano": 85, "cadencia": 350, "desc": "Libera o rugido do dragão a cada golpe."},
    {"nome": "Katana Dimensional", "tipo_arma": "melee", "raridade": "Lendário", "dano": 78, "cadencia": 220, "desc": "Corta através do próprio espaço-tempo."},
    {"nome": "Martelo do Trovão Divino", "tipo_arma": "melee", "raridade": "Lendário", "dano": 90, "cadencia": 450, "desc": "Invoca raios reais do céu no alvo."},
    {"nome": "Lança Rompe-Mundos", "tipo_arma": "melee", "raridade": "Lendário", "dano": 82, "cadencia": 320, "desc": "Perfura qualquer tipo de armadura."},

    {"nome": "Arco Supremo de Artemis", "tipo_arma": "ranged", "raridade": "Lendário", "dano": 72, "cadencia": 240, "desc": "Nunca erra o alvo e dispara 3 flechas por vez."},
    {"nome": "Canhão de Plasma Arcano", "tipo_arma": "ranged", "raridade": "Lendário", "dano": 92, "cadencia": 500, "desc": "Dispara esferas de plasma devastadoras."},
    {"nome": "Besta do Vazio Sideral", "tipo_arma": "ranged", "raridade": "Lendário", "dano": 80, "cadencia": 380, "desc": "Cria pequenos buracos negros ao impactar."},
    {"nome": "Arco dos Mil Ventos", "tipo_arma": "ranged", "raridade": "Lendário", "dano": 70, "cadencia": 200, "desc": "Tempestade contínua de flechas aéreas."},
    {"nome": "Arbalete de Precisão Solar", "tipo_arma": "ranged", "raridade": "Lendário", "dano": 88, "cadencia": 420, "desc": "Feixes de luz solar concentrada."},
    {"nome": "Arco de Estrelas Cadentes", "tipo_arma": "ranged", "raridade": "Lendário", "dano": 76, "cadencia": 260, "desc": "Chuva de meteoros no ponto atingido."},

    {"nome": "Grimório do Arquimago Supremo", "tipo_arma": "mage", "raridade": "Lendário", "dano": 74, "cadencia": 230, "desc": "Domina todos os elementos da natureza."},
    {"nome": "Cajado do Vazio Eterno", "tipo_arma": "mage", "raridade": "Lendário", "dano": 86, "cadencia": 360, "desc": "Desintegra a matéria dos inimigos."},
    {"nome": "Orbe da Criação Primordial", "tipo_arma": "mage", "raridade": "Lendário", "dano": 70, "cadencia": 190, "desc": "Disparo contínuo e devastador."},
    {"nome": "Cajado dos Tempos Antigos", "tipo_arma": "mage", "raridade": "Lendário", "dano": 82, "cadencia": 330, "desc": "Paralisa inimigos temporariamente."},
    {"nome": "Grimório de Magia Proibida", "tipo_arma": "mage", "raridade": "Lendário", "dano": 90, "cadencia": 410, "desc": "Magia sombria de destruição em massa."},
    {"nome": "Varinha do Big Bang", "tipo_arma": "mage", "raridade": "Lendário", "dano": 84, "cadencia": 300, "desc": "Cria explosões de supernovas."},

    # === MÍTICAS (1 Melee, 1 Ranged, 1 Mage) ===
    {"nome": "Excalibur do Juízo Final", "tipo_arma": "melee", "raridade": "Mítico", "dano": 150, "cadencia": 180, "desc": "A lendária lâmina sagrada definitiva. Ondas de choque em cada balanço."},
    {"nome": "Arco do Cosmos Infinito", "tipo_arma": "ranged", "raridade": "Mítico", "dano": 140, "cadencia": 160, "desc": "Flechas teleguiadas infinitas de pura energia cósmica."},
    {"nome": "Cajado do Arquiteto Universal", "tipo_arma": "mage", "raridade": "Mítico", "dano": 145, "cadencia": 170, "desc": "Manipula o tecido do universo para aniquilar qualquer ameaça."}
]

# --- DICIONÁRIO COMPLETO DE AMULETOS (46 Amuletos) ---
TODOS_AMULETOS = [
    # Comuns (16)
    {"nome": "Amuleto de Sangue", "raridade": "Comum", "valor": 15, "desc": "+15 Vida Máxima."},
    {"nome": "Pingente de Cobre", "raridade": "Comum", "valor": 5, "desc": "+5% Defesa."},
    {"nome": "Anel de Prata Velha", "raridade": "Comum", "valor": 5, "desc": "+5% Chance Crítica."},
    {"nome": "Olho de Gato", "raridade": "Comum", "valor": 8, "desc": "+8% Velocidade de Movimento."},
    {"nome": "Talismã da Coragem", "raridade": "Comum", "valor": 10, "desc": "+10% Dano Físico."},
    {"nome": "Pedra da Sorte Menor", "raridade": "Comum", "valor": 10, "desc": "+10% Ouro Encontrado."},
    {"nome": "Trevo de Três Folhas", "raridade": "Comum", "valor": 3, "desc": "+3% Chance de Esquiva."},
    {"nome": "Símbolo de Ferro", "raridade": "Comum", "valor": 8, "desc": "+8 Defesa Base."},
    {"nome": "Medalhão do Viajante", "raridade": "Comum", "valor": 10, "desc": "+10 Mana Máxima."},
    {"nome": "Broche de Rubi Simples", "raridade": "Comum", "valor": 5, "desc": "+5% Dano de Fogo."},
    {"nome": "Fio de Cabelo de Fada", "raridade": "Comum", "valor": 5, "desc": "-5% Cooldown de Habilidades."},
    {"nome": "Anel de Resistência Física", "raridade": "Comum", "valor": 6, "desc": "Reduz dano físico em 6%."},
    {"nome": "Pingente de Areia", "raridade": "Comum", "valor": 4, "desc": "+4% Esquiva em salas secas."},
    {"nome": "Selo do Guardião", "raridade": "Comum", "valor": 10, "desc": "+10 Escudo Inicial."},
    {"nome": "Pulseira de Couro", "raridade": "Comum", "valor": 5, "desc": "+5% Velocidade de Ataque."},
    {"nome": "Amuleto da Brisa", "raridade": "Comum", "valor": 6, "desc": "+6% Velocidade ao correr."},

    # Incomuns (12)
    {"nome": "Amuleto de Mana Fluida", "raridade": "Incomum", "valor": 25, "desc": "+25 Mana Máxima e regeneção leve."},
    {"nome": "Anel de Foco Crítico", "raridade": "Incomum", "valor": 12, "desc": "+12% Chance Crítica."},
    {"nome": "Olho do Falcão", "raridade": "Incomum", "valor": 15, "desc": "+15% Alcance dos projéteis."},
    {"nome": "Pedra de Fogo Interno", "raridade": "Incomum", "valor": 12, "desc": "+12% Dano de Fogo."},
    {"nome": "Corrente de Aço Reforçado", "raridade": "Incomum", "valor": 12, "desc": "+12% Defesa Física."},
    {"nome": "Talismã de Regeneração Lenta", "raridade": "Incomum", "valor": 1, "desc": "Recupera 1 HP a cada 5s."},
    {"nome": "Trevo de Ouro", "raridade": "Incomum", "valor": 20, "desc": "+20% Drop de Ouro."},
    {"nome": "Pingente de Gelo Sutil", "raridade": "Incomum", "valor": 10, "desc": "Ataques causam lentidão de 10%."},
    {"nome": "Broche de Vento Ágil", "raridade": "Incomum", "valor": 12, "desc": "+12% Velocidade de Movimento."},
    {"nome": "Símbolo de Proteção Arcana", "raridade": "Incomum", "valor": 15, "desc": "+15 Escudo Mágico."},
    {"nome": "Anel do Vampiro Menor", "raridade": "Incomum", "valor": 3, "desc": "Recupera 3% do dano causado em HP."},
    {"nome": "Medalhão da Determinação", "raridade": "Incomum", "valor": 20, "desc": "+20 HP ao entrar em nova sala."},

    # Raros (8)
    {"nome": "Coração de Golem", "raridade": "Raro", "valor": 60, "desc": "+60 HP Máximo e +15 Defesa."},
    {"nome": "Olho de Ciclope", "raridade": "Raro", "valor": 35, "desc": "+35% Dano Crítico."},
    {"nome": "Amuleto do Relâmpago", "raridade": "Raro", "valor": 20, "desc": "+20% Velocidade de Ataque."},
    {"nome": "Símbolo do Sacerdote", "raridade": "Raro", "valor": 50, "desc": "Eficácia de poções e cura dobrada."},
    {"nome": "Pingente de Sombra", "raridade": "Raro", "valor": 15, "desc": "+15% Chance de Esquiva total."},
    {"nome": "Broche de Diamante Negro", "raridade": "Raro", "valor": 25, "desc": "+25% Dano Geral."},
    {"nome": "Anel de Retaliação", "raridade": "Raro", "valor": 30, "desc": "Reflete 30% do dano sofrido."},
    {"nome": "Talismã do Alquimista", "raridade": "Raro", "valor": 50, "desc": "+50% Ouro e +10% Gemas."},

    # Épicos (6)
    {"nome": "Amuleto da Fúria de Batalha", "raridade": "Épico", "valor": 40, "desc": "+40% Dano quanto menor for sua vida."},
    {"nome": "Olho do Dragão", "raridade": "Épico", "valor": 30, "desc": "Imunidade a fogo e +30% Dano elemental."},
    {"nome": "Símbolo do Tempo Parado", "raridade": "Épico", "valor": 30, "desc": "Reduz cooldowns em 30%."},
    {"nome": "Corrente de Almas Prisioneiras", "raridade": "Épico", "valor": 10, "desc": "Gera 10 de Escudo ao matar um mob."},
    {"nome": "Anel do Fênix Menor", "raridade": "Épico", "valor": 25, "desc": "Revive uma vez com 25% de vida."},
    {"nome": "Medalhão de Mana Infinita", "raridade": "Épico", "valor": 50, "desc": "Regenera 5 de Mana por segundo."},

    # Lendários (3)
    {"nome": "Coração de Titã Primordial", "raridade": "Lendário", "valor": 150, "desc": "Dobra HP e Armadura máximas."},
    {"nome": "Olho do Cosmos", "raridade": "Lendário", "valor": 100, "desc": "Todos os projéteis perseguem inimigos."},
    {"nome": "Anel de Midas", "raridade": "Lendário", "valor": 100, "desc": "Inimigos derrotados dropam Gemas e Ouro duplo."},

    # Mítico (1)
    {"nome": "Anel da Fênix", "raridade": "Mítico", "valor": 100, "desc": "Revive o jogador com HP cheio e concede 10s de imortalidade ao morrer."}
]

# --- ESTRUTURA DE SETS DE ARMADURAS (Capacete, Peitoral, Calça) ---
SETS_ARMADURAS = {
    # Épicos (1 Buff Adicional)
    "Paladino Sagrado": {
        "raridade": "Épico", "def": 18, "hp": 40, "buffs": ["+15% Cura Recebida"],
        "set_completo": "Regenera 2% HP por segundo em combate."
    },
    "Assassino das Sombras": {
        "raridade": "Épico", "def": 12, "hp": 25, "buffs": ["+10% Esquiva"],
        "set_completo": "+25% Dano Crítico por trás."
    },
    "Mago Elemental": {
        "raridade": "Épico", "def": 10, "hp": 30, "buffs": ["+20% Reg. Mana"],
        "set_completo": "+20% Dano de Feitiços (H, J, K, L)."
    },
    "Berserker Sangrento": {
        "raridade": "Épico", "def": 15, "hp": 50, "buffs": ["+15% Vel. Ataque ao perder HP"],
        "set_completo": "+30% Dano quando HP abaixo de 40%."
    },

    # Lendários (3 Buffs Adicionais)
    "Guardião Real": {
        "raridade": "Lendário", "def": 35, "hp": 100, "buffs": ["+20% Defesa Total", "+10% HP Máx", "Reflete 10% Dano"],
        "set_completo": "Imunidade a atordoamento e +50 Defesa Base."
    },
    "Senhor das Tempestades": {
        "raridade": "Lendário", "def": 28, "hp": 80, "buffs": ["+25% Dano Mágico", "Raios Passivos nos Inimigos", "+10% Velocidade"],
        "set_completo": "Invoca uma tempestade elétrica na sala inteira."
    },
    "Executor Implacável": {
        "raridade": "Lendário", "def": 30, "hp": 85, "buffs": ["+30% Dano Crítico", "+15% Roubo de Vida", "Imunidade Sangramento"],
        "set_completo": "Ataques críticos causam explosões de sangue."
    },

    # Mítico (5 Buffs Adicionais + Set Supremo)
    "Imperador do Abismo": {
        "raridade": "Mítico", "def": 60, "hp": 250, 
        "buffs": ["Imunidade a CC", "+50% Todos Status Base", "Regeneração Contínua", "Explosão de Energia", "+100% Gemas Ganhas"],
        "set_completo": "Transforma o herói em um lorde invencível com escudo impenetrável."
    }
}

# --- FUNÇÕES DE INTEGRAÇÃO COM INDEX/BESTIÁRIO ---

def registrar_item_no_index(nome_item):
    """Registra o item descoberto no save permanentemente"""
    dados = carregar_dados()
    if 'index_descobertas' not in dados:
        dados['index_descobertas'] = {}
    
    if not dados['index_descobertas'].get(nome_item, False):
        dados['index_descobertas'][nome_item] = True
        salvar_dados(dados)

def sortear_item(raridade_desejada=None):
    """Sorteia um item aleatório com base na raridade e grava no Index ao pegar"""
    if not raridade_desejada:
        raridade_desejada = random.choices(
            ["Comum", "Incomum", "Raro", "Épico", "Lendário", "Mítico"],
            weights=[50, 30, 12, 5, 2.5, 0.5]
        )[0]

    opcoes = [i for i in TODAS_ARMAS + TODOS_AMULETOS if i.get('raridade') == raridade_desejada]
    if not opcoes:
        opcoes = TODAS_ARMAS

    item_sorteado = random.choice(opcoes).copy()
    registrar_item_no_index(item_sorteado['nome'])
    return item_sorteado