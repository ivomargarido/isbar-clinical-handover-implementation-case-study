"""
Componente 7: saída de passagem.

Na folha real, o botão «Preparar impressão» gera um PDF. Aqui geramos só
texto simples, para manter a demonstração mínima.

Regra do workflow (docs/02): a impressão NUNCA é bloqueada. Um doente
por validar sai com a marca «NÃO VALIDADO».
"""


def gerar_saida(aplicacao, turno):
    """Devolve o texto da folha de passagem com os doentes que têm cama."""
    linhas = [f"FOLHA DE PASSAGEM | turno {turno} | DADOS SINTÉTICOS", ""]

    # Só entram episódios com cama atribuída (doentes presentes no serviço).
    presentes = [e for e in aplicacao.episodios.values() if e.cama]
    for episodio in sorted(presentes, key=lambda e: e.cama):
        marca = "VALIDADO" if episodio.validado else "NÃO VALIDADO"
        linhas.append(f"Cama {episodio.cama} | {episodio.id_episodio} | {marca}")

        for (dominio, intervencao, componente, _), entrada in episodio.entradas.items():
            if entrada.estado == "retirada":
                continue                      # o enfermeiro decidiu que não entra
            texto = " / ".join(entrada.linhas)
            linhas.append(f"  [{dominio}] {intervencao} ({componente}): {texto}")

        for campo, dados in episodio.campos_manuais.items():
            valor = dados["valor"] or "(por preencher)"
            linhas.append(f"  [manual, fonte externa não integrada] {campo}: {valor}")
        linhas.append("")

    return "\n".join(linhas)
