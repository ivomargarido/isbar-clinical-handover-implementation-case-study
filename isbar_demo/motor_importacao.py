"""
Componente 4: motor de importação.

Recebe os registos do episódio e a configuração, aplica as regras Core
da UC-01 (docs/01, secção 6.1) e devolve PROPOSTAS. Não decide nada clínico:
propõe, assinala e deixa a decisão ao enfermeiro.

Regras aplicadas aqui (ver comentários junto de cada bloco):
    C-02 episódio tem de corresponder
    C-04 cada componente separado, sem fundir nem gerar texto
    C-05 metadados: "registado por" e referência temporal
    C-06 aviso de herança por componente
    C-07 estados: achado, negativo, registo sem conteúdo importado, sem registo
    C-08 só o período de referência; vários registos: todos
    C-09 valores com unidade; unidade em falta assinalada
    C-10 sem cálculos e sem extrair valores de texto livre
    C-11 só intervenções finais (janelas compostas ignoradas)
"""

from dataclasses import dataclass, field

from .configuracao import heranca_do_componente, intervencoes_configuradas

# Textos de aviso, num só sítio para serem fáceis de rever.
AVISO_HERANCA = "Pode conter conteúdo de registo anterior."
AVISO_SEM_INFORMACAO = "Sem informação importada."
AVISO_CONTEUDO_NAO_IMPORTADO = "Existe registo na origem; conteúdo não importado por configuração."
AVISO_UNIDADE_EM_FALTA = "Unidade não disponível na origem."
AVISO_METADADO_EM_FALTA = "'Registado por' não disponível na origem."


# ----------------------------------------------------------------------
# Estruturas de dados que o motor devolve.
# ----------------------------------------------------------------------
@dataclass
class Proposta:
    """Um componente de um registo, proposto para a folha. É sempre provisório (C-03)."""

    dominio: str
    intervencao: str
    componente: str
    linhas: list            # o conteúdo, linha a linha, tal como vem da origem
    id_registo: str
    registado_por: str      # nunca é "autor" (C-05)
    referencia_temporal: str
    aviso_heranca: bool = False
    avisos: list = field(default_factory=list)
    estado: str = "provisoria"

    @property
    def chave(self):
        """Identifica a proposta de forma única dentro do episódio."""
        return (self.dominio, self.intervencao, self.componente, self.id_registo)


@dataclass
class Aviso:
    """Aviso ao nível do domínio ou da intervenção (não é conteúdo clínico)."""

    dominio: str
    intervencao: str        # vazio quando o aviso é do domínio inteiro
    mensagem: str


@dataclass
class ResultadoImportacao:
    bloqueada: bool = False
    motivo_bloqueio: str = ""
    propostas: list = field(default_factory=list)
    avisos: list = field(default_factory=list)
    estado_dominios: dict = field(default_factory=dict)


# ----------------------------------------------------------------------
# Funções auxiliares: metadados e formatação de cada tipo de componente.
# ----------------------------------------------------------------------
def referencia_temporal(registo):
    """
    C-05: a referência temporal depende da programação do registo.
    - por turno: mostra o turno;
    - horário definido: mostra a hora declarada (que é editável na origem
      e por isso não prova o momento real da avaliação).
    """
    if registo.get("programacao") == "horario" and registo.get("hora_declarada"):
        return f"Hora declarada {registo['hora_declarada']} (turno {registo['turno']})"
    if registo.get("turno"):
        return f"Turno {registo['turno']}"
    return "Referência temporal não disponível na origem"


def formatar_frases(conteudo):
    # C-04: as frases passam tal como estão; não se junta nem se reescreve nada.
    return list(conteudo) if conteudo else None


def formatar_texto_livre(conteudo):
    # C-10: o texto livre passa inteiro, tal como foi escrito.
    # Não se procuram números nem horas dentro dele.
    return [conteudo] if conteudo and conteudo.strip() else None


def formatar_medicoes(conteudo, avisos):
    """
    C-08: todas as medições, cada uma com a sua hora.
    C-09: valor sempre com unidade; valores compostos (TA 98/60) ficam inteiros.
    C-10: não se calcula nada (nem somas, nem médias, nem tendências).
    """
    if not conteudo:
        return None
    linhas = []
    for medicao in conteudo:
        if medicao.get("unidade"):
            unidade = medicao["unidade"]
        else:
            unidade = "[unidade não disponível]"
            if AVISO_UNIDADE_EM_FALTA not in avisos:
                avisos.append(AVISO_UNIDADE_EM_FALTA)
        hora = medicao.get("hora") or "hora não disponível"
        linhas.append(f"{medicao['parametro']}: {medicao['valor']} {unidade} ({hora})")
    return linhas


def formatar_arvore(conteudo, filtro):
    """
    P2, árvore de avaliação. Três estados por item (C-07):
      - valor positivo (achado)
      - "não" registado explicitamente (negativo)
      - None = sem registo  -> NUNCA se mostra como "não" (AC-13)
    Com o filtro da Pele, mostram-se os achados e diz-se quantos negativos existem.
    """
    if not conteudo:
        return None
    linhas = []
    negativos = 0
    for item in conteudo:
        nome = f"{item['grupo']} › {item['item']}"
        valor = item.get("valor")
        if valor is None:
            linhas.append(f"{nome}: sem registo")
        elif valor == "não":
            negativos += 1
            if filtro != "positivos_e_indicar_negativos":
                linhas.append(f"{nome}: não")
        else:
            linhas.append(f"{nome}: {valor}")
    if filtro == "positivos_e_indicar_negativos" and negativos:
        linhas.append(f"Existem {negativos} item(ns) com negativo registado (não mostrados).")
    return linhas


def formatar_estado_execucao(conteudo, nota):
    """
    P4. ALT-10: execução sem nota mostra 'Realizada, sem nota'.
    Nunca se vai buscar o valor de um registo anterior (AC-17).
    """
    if not conteudo:
        return None
    texto = "Realizada" if conteudo == "realizada" else "Não realizada"
    if not (nota and nota.strip()):
        texto += ", sem nota"
    return [texto]


def construir_linhas(componente, registo, definicao, avisos):
    """Escolhe a função de formatação certa para cada tipo de componente."""
    conteudo = registo["componentes"].get(componente)
    if componente == "frases":
        return formatar_frases(conteudo)
    if componente in ("texto_livre", "observacoes", "nota_associada"):
        return formatar_texto_livre(conteudo)
    if componente == "medicoes":
        return formatar_medicoes(conteudo, avisos)
    if componente == "arvore":
        return formatar_arvore(conteudo, definicao.get("filtro_arvore"))
    if componente == "estado":
        return formatar_estado_execucao(conteudo, registo["componentes"].get("nota_associada"))
    return None


def tem_conteudo(valor):
    """Verdadeiro se um componente da origem tem alguma coisa escrita."""
    if valor is None:
        return False
    if isinstance(valor, str):
        return bool(valor.strip())
    return bool(valor)


# ----------------------------------------------------------------------
# Função principal.
# ----------------------------------------------------------------------
def importar(id_episodio, registos, configuracao, turno_atual, ordem_turnos):
    """
    Aplica as regras Core e devolve um ResultadoImportacao.

    id_episodio  -> episódio selecionado pelo enfermeiro
    registos     -> o que o leitor devolveu
    turno_atual  -> período de referência (por defeito, o turno atual)
    ordem_turnos -> {id_turno: ordem}, para saber o que é anterior
    """
    resultado = ResultadoImportacao()

    # C-02: se algum registo não pertence ao episódio selecionado,
    # a importação inteira é impedida. Não se importa "só a parte certa".
    for registo in registos:
        if registo["id_episodio"] != id_episodio:
            resultado.bloqueada = True
            resultado.motivo_bloqueio = (
                f"Registo {registo['id_registo']} pertence a outro episódio. Importação impedida."
            )
            return resultado

    ordem_atual = ordem_turnos[turno_atual]

    # Percorremos a configuração (e não os registos). Assim, intervenções
    # não configuradas, como a janela composta, nunca entram (C-11).
    dominio_teve_registo = {}
    dominio_teve_propostas = {}

    for dominio, definicao in intervencoes_configuradas(configuracao):
        dominio_teve_registo.setdefault(dominio, False)
        dominio_teve_propostas.setdefault(dominio, False)

        nome = definicao["intervencao"]
        da_intervencao = [r for r in registos if r["intervencao"] == nome]

        # C-08: só são elegíveis os registos do período de referência.
        no_periodo = [r for r in da_intervencao if r["turno"] == turno_atual]
        anteriores = [r for r in da_intervencao if ordem_turnos[r["turno"]] < ordem_atual]

        if not no_periodo:
            # ALT-04: só existe registo anterior -> não importar, só avisar.
            # (Se a intervenção for condicional e não tiver registo nenhum,
            # não há aviso individual: ALT-01.)
            if anteriores:
                turnos = ", ".join(sorted({r["turno"] for r in anteriores}))
                resultado.avisos.append(Aviso(
                    dominio, nome,
                    f"Sem registo neste turno. Existe registo anterior ao período (turno {turnos})."
                ))
            continue

        dominio_teve_registo[dominio] = True

        # C-08: vários registos no período -> todos, sem escolher pela hora.
        for registo in no_periodo:
            propostas_deste_registo = 0

            for componente in definicao["componentes"]:
                avisos = []
                linhas = construir_linhas(componente, registo, definicao, avisos)
                if not linhas:
                    continue

                # C-05: "registado por", nunca "autor".
                registado_por = registo.get("registado_por")
                if not registado_por:
                    registado_por = "não disponível na origem"
                    avisos.append(AVISO_METADADO_EM_FALTA)

                # C-06: aviso de herança decidido pela configuração do componente.
                herda = heranca_do_componente(configuracao, definicao["padrao"], componente) == "herda"

                resultado.propostas.append(Proposta(
                    dominio=dominio,
                    intervencao=nome,
                    componente=componente,
                    linhas=linhas,
                    id_registo=registo["id_registo"],
                    registado_por=registado_por,
                    referencia_temporal=referencia_temporal(registo),
                    aviso_heranca=herda,
                    avisos=avisos,
                ))
                propostas_deste_registo += 1

            if propostas_deste_registo:
                dominio_teve_propostas[dominio] = True
            else:
                # C-07 / ALT-12: há registo, mas o conteúdo está só em
                # componentes que a configuração exclui.
                excluidos_com_conteudo = [
                    c for c, v in registo["componentes"].items()
                    if c not in definicao["componentes"] and tem_conteudo(v)
                ]
                if excluidos_com_conteudo:
                    resultado.avisos.append(Aviso(dominio, nome, AVISO_CONTEUDO_NAO_IMPORTADO))

    # C-07: estado de cada domínio.
    for dominio in dominio_teve_registo:
        if not dominio_teve_registo[dominio]:
            resultado.estado_dominios[dominio] = "sem_informacao_importada"
            resultado.avisos.append(Aviso(dominio, "", AVISO_SEM_INFORMACAO))
        elif dominio_teve_propostas[dominio]:
            resultado.estado_dominios[dominio] = "com_propostas"
        else:
            resultado.estado_dominios[dominio] = "registo_sem_conteudo_importado"

    return resultado
