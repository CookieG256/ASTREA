from idiomas import nome_bioma_localizado
from save import carregar_dados, salvar_dados
from missoes import registrar_progresso

FRAGMENTOS_BIOMAS = {
    1: ("O primeiro sinal", "Uma estrela caiu no campo antes da noite eterna. Suas raízes ainda brilham sob a terra."),
    2: ("A floresta que escuta", "As árvores repetem nomes de viajantes que nunca chegaram ao outro lado."),
    3: ("Cristais de memória", "Cada cristal guarda o último pensamento de quem tocou sua luz."),
    4: ("Areia antiga", "O deserto cobre uma estrada feita para levar alguém de volta para casa."),
    5: ("Água sem reflexo", "O pântano não reflete o céu: mostra um lugar que ainda não existe."),
    6: ("A cidade esquecida", "As ruínas foram construídas para conter algo, não para proteger seus habitantes."),
    7: ("O frio que chama", "No alto da montanha, uma voz responde sempre com a voz de quem a escuta."),
    8: ("O coração da forja", "O templo ainda pulsa; cada tremor é uma lembrança tentando escapar."),
    9: ("Degraus no escuro", "A torre não tem topo. Seus últimos degraus apontam para dentro do céu."),
    10: ("O pacto do abismo", "O dragão ofereceu proteção ao mundo. O preço foi apagar seu próprio nome."),
    11: ("Cinzas vivas", "As cinzas guardam calor e histórias de uma chama que se recusou a morrer."),
    12: ("Jardins suspensos", "As flores crescem seguindo constelações que desapareceram há séculos."),
    13: ("O rei dourado", "O rei mumificado ainda segura uma chave; ninguém sabe qual porta ela abre."),
    14: ("A fenda", "Do outro lado da fenda, ASTREA aparece no céu como uma estrela distante."),
    15: ("O vazio lembra", "O vazio reconhece cada passo. Ele não devora o mundo: tenta reconstruí-lo."),
}

NPCS = {
    "cartografo": {"nome": "Ivo, o Cartógrafo", "simbolo": "M"},
    "curandeira": {"nome": "Nara, a Curandeira", "simbolo": "+"},
    "ferreiro": {"nome": "Bram, o Ferreiro", "simbolo": "F"},
}


def desbloquear_fragmento(bioma_id):
    dados = carregar_dados()
    descobertos = dados.setdefault("fragmentos_historia", {})
    chave = str(int(bioma_id))
    if chave in descobertos:
        return False
    descobertos[chave] = True
    salvar_dados(dados)
    return True


def resgatar_npc(npc_id):
    if npc_id not in NPCS:
        return False
    dados = carregar_dados()
    resgatados = dados.setdefault("npcs_resgatados", [])
    if npc_id in resgatados:
        return False
    resgatados.append(npc_id)
    reputacao = dados.setdefault("reputacao_npcs", {})
    reputacao[npc_id] = int(reputacao.get(npc_id, 0)) + 1
    registrar_progresso(dados, "npcs")
    salvar_dados(dados)
    return True


def npc_para_reencontro():
    dados = carregar_dados()
    resgatados = dados.get("npcs_resgatados", [])
    disponiveis = [npc for npc in resgatados if obter_reputacao(npc, dados) < 10]
    return min(disponiveis, key=lambda npc: obter_reputacao(npc, dados)) if disponiveis else None


def registrar_reencontro(npc_id):
    dados = carregar_dados()
    vistos = dados.setdefault("npcs_reencontrados", [])
    reputacao = dados.setdefault("reputacao_npcs", {})
    reputacao[npc_id] = int(reputacao.get(npc_id, 0)) + 1
    if npc_id not in vistos:
        vistos.append(npc_id)
    registrar_progresso(dados, "npcs")
    salvar_dados(dados)


def obter_reputacao(npc_id, dados=None):
    dados = dados if isinstance(dados, dict) else carregar_dados()
    return max(0, int(dados.get("reputacao_npcs", {}).get(npc_id, 0)))


def nivel_reputacao(npc_id, dados=None):
    return min(5, obter_reputacao(npc_id, dados) // 2)


def texto_fragmento(bioma_id, idioma="PT"):
    titulo, texto = FRAGMENTOS_BIOMAS.get(int(bioma_id), FRAGMENTOS_BIOMAS[1])
    return f"{nome_bioma_localizado(bioma_id, idioma)} · {titulo}", texto
