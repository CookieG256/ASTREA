def conceder_reliquia(player, nome):
    reliquias = getattr(player, "reliquias_run", None)
    if reliquias is None:
        player.reliquias_run = []
        reliquias = player.reliquias_run
    reliquias.append({"nome": nome, "abates": 0, "nivel": 0})
    _aplicar_sinergias_reliquias(player)


def _aplicar_sinergias_reliquias(player):
    nomes = {reliquia["nome"] for reliquia in getattr(player, "reliquias_run", [])}
    aplicadas = getattr(player, "sinergias_reliquia_run", set())
    if not isinstance(aplicadas, set):
        aplicadas = set(aplicadas)
    combinacoes = (
        ("berserker+vitalidade", {"berserker", "vitalidade"}),
        ("arcana+berserker", {"arcana", "berserker"}),
        ("arcana+vitalidade", {"arcana", "vitalidade"}),
    )
    for chave, requisitos in combinacoes:
        if not requisitos.issubset(nomes) or chave in aplicadas:
            continue
        if chave == "berserker+vitalidade":
            player.hp_max += 20
            player.hp = min(player.hp_max, player.hp + 20)
            player.bonus_dano_percent += 0.05
        elif chave == "arcana+berserker":
            player.mana_max += 20
            player.mana = min(player.mana_max, player.mana + 20)
            player.bonus_dano_percent += 0.08
        else:
            player.hp_max += 20
            player.hp = min(player.hp_max, player.hp + 20)
            player.mana_max += 20
            player.mana = min(player.mana_max, player.mana + 20)
            player.defesa_percent = min(0.7, player.defesa_percent + 0.05)
        aplicadas.add(chave)
    player.sinergias_reliquia_run = aplicadas


def registrar_abate_reliquias(player):
    for reliquia in getattr(player, "reliquias_run", []):
        if reliquia["nivel"] >= 5:
            continue
        reliquia["abates"] += 1
        if reliquia["abates"] < (reliquia["nivel"] + 1) * 5:
            continue
        reliquia["nivel"] += 1
        if reliquia["nome"] == "berserker":
            player.buffs_run["dano"] = player.buffs_run.get("dano", 0) + 0.03
        elif reliquia["nome"] == "vitalidade":
            player.hp_max += 15
            player.hp = min(player.hp_max, player.hp + 15)
        else:
            player.mana_max += 5
            player.mana = min(player.mana_max, player.mana + 5)
            player.bonus_dano_percent += 0.02
