from save import carregar_dados, salvar_dados


def registrar_run(estatisticas, dificuldade, cooperativo=False):
    dados = carregar_dados()
    registros = dados.setdefault("melhores_runs", [])
    registro = {
        "andar": int(estatisticas.get("andar_morte", 1)),
        "abates": int(estatisticas.get("mobs_mortos", 0)),
        "gemas": int(estatisticas.get("gemas_coletadas", 0)),
        "tempo": int(estatisticas.get("tempo_segundos", 0)),
        "dano_causado": int(estatisticas.get("dano_causado", 0)),
        "salas_concluidas": int(estatisticas.get("salas_concluidas", 0)),
        "salas_sem_dano": int(estatisticas.get("salas_sem_dano", 0)),
        "inimigos_raros_derrotados": int(estatisticas.get("inimigos_raros_derrotados", 0)),
        "dificuldade": dificuldade,
        "cooperativo": bool(cooperativo),
    }
    registros.append(registro)
    novos_registros = []
    for modo in ("EASY", "NORMAL", "HARD", "HARDCORE"):
        por_modo = [item for item in registros if item.get("dificuldade") == modo]
        por_modo.sort(
            key=lambda item: (
                item["andar"], item["abates"], item["gemas"], -item["tempo"]
            ),
            reverse=True,
        )
        novos_registros.extend(por_modo[:10])
    registros[:] = novos_registros
    salvar_dados(dados)
    return registro


def obter_melhores_runs():
    dados = carregar_dados()
    registros = dados.get("melhores_runs", [])
    if not isinstance(registros, list):
        return []
    return sorted(
        registros,
        key=lambda item: (
            int(item.get("andar", 1)),
            int(item.get("abates", 0)),
            int(item.get("gemas", 0)),
            -int(item.get("tempo", 0)),
        ),
        reverse=True,
    )[:10]


def obter_melhores_runs_por_dificuldade():
    dados = carregar_dados()
    registros = dados.get("melhores_runs", [])
    if not isinstance(registros, list):
        registros = []
    dificuldades = ("EASY", "NORMAL", "HARD", "HARDCORE")
    resultados = {}
    for dificuldade in dificuldades:
        candidatos = [
            registro for registro in registros
            if registro.get("dificuldade") == dificuldade
        ]
        candidatos.sort(
            key=lambda item: (
                int(item.get("andar", 1)),
                int(item.get("abates", 0)),
                int(item.get("gemas", 0)),
                -int(item.get("tempo", 0)),
            ),
            reverse=True,
        )
        resultados[dificuldade] = candidatos[0] if candidatos else None
    return resultados
