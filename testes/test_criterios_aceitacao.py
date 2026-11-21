"""
Testes de aceitação AC-01 a AC-25 da especificação UC-01 (docs/01) e três
testes do workflow To-Be (WF-01 a WF-03, docs/02).

Cada teste diz na primeira linha da docstring que critério verifica.
DADOS SINTÉTICOS.
"""

import copy

from conftest import FICHEIRO_ORIGEM, TURNO_ATUAL
from isbar_demo.aplicacao_isbar import ErroValidacao
from isbar_demo.leitor_origem import LeitorOrigemSintetica
from isbar_demo.motor_importacao import (
    AVISO_CONTEUDO_NAO_IMPORTADO,
    AVISO_METADADO_EM_FALTA,
    AVISO_SEM_INFORMACAO,
    AVISO_UNIDADE_EM_FALTA,
)
from isbar_demo.saida_passagem import gerar_saida

EP_A = "SINT-EP-A"
EP_B = "SINT-EP-B"


# ----------------------------------------------------------------------
# Funções de apoio, só para os testes ficarem curtos.
# ----------------------------------------------------------------------
def entradas_de(app, episodio, intervencao=None, componente=None):
    """Lista as entradas da folha, filtrando por intervenção e/ou componente."""
    resultado = []
    for (dom, interv, comp, reg), entrada in app.episodios[episodio].entradas.items():
        if intervencao and interv != intervencao:
            continue
        if componente and comp != componente:
            continue
        resultado.append(entrada)
    return resultado


def rever_tudo(app, episodio):
    """Simula o enfermeiro a rever e aceitar todas as propostas do episódio."""
    for chave in list(app.episodios[episodio].entradas):
        app.aceitar(episodio, chave)


def todas_as_linhas(app, episodio):
    return [linha for e in app.episodios[episodio].entradas.values() for linha in e.linhas]


def avisos_de(app, episodio, dominio=None, intervencao=None):
    return [
        a.mensagem for a in app.episodios[episodio].avisos
        if (dominio is None or a.dominio == dominio)
        and (intervencao is None or a.intervencao == intervencao)
    ]


# ----------------------------------------------------------------------
# Critérios de aceitação AC-01 a AC-25
# ----------------------------------------------------------------------
def test_ac01_conteudo_provisorio(app_importada):
    """AC-01: Dado episódio correto e registo elegível, ao atualizar o conteúdo é provisório."""
    entradas = app_importada.episodios[EP_A].entradas.values()
    assert entradas, "devia haver propostas importadas"
    assert all(e.estado == "proposta" for e in entradas)
    assert all(e.proposta.estado == "provisoria" for e in entradas)


def test_ac02_separado_por_intervencao_e_componente(app_importada):
    """AC-02: Várias intervenções num domínio aparecem separadas por intervenção e componente."""
    chaves = [c for c in app_importada.episodios[EP_A].entradas if c[0] == "Eliminação"]
    pares = {(c[1], c[2]) for c in chaves}
    assert ("Vigiar eliminação urinária", "frases") in pares
    assert ("Vigiar eliminação urinária", "texto_livre") in pares
    assert ("Vigiar eliminação intestinal", "frases") in pares
    assert ("Monitorizar eliminação intestinal", "medicoes") in pares
    # Cada par (intervenção, componente) é uma entrada própria: nada foi fundido.
    assert len(pares) == len(chaves)


def test_ac03_sem_substituicao_silenciosa(app_importada):
    """AC-03: Dado campo editado, uma nova importação não o substitui em silêncio."""
    chave = next(c for c in app_importada.episodios[EP_A].entradas
                 if c[1] == "Vigiar eliminação urinária" and c[2] == "texto_livre")
    app_importada.editar(EP_A, chave, ["Texto editado pelo enfermeiro."])

    # Simulamos uma alteração na origem depois da importação (ALT-05).
    for r in app_importada.leitor.registos_em_bruto():
        if r["id_registo"] == "SINT-R001":
            r["componentes"]["texto_livre"] = "Texto alterado na origem."

    resultado = app_importada.atualizar_a_partir_do_ehr(EP_A, TURNO_ATUAL)
    entrada = app_importada.episodios[EP_A].entradas[chave]
    assert entrada.linhas == ["Texto editado pelo enfermeiro."]
    assert entrada.decisao_pendente == ["Texto alterado na origem."]
    assert resultado.pendentes == 1


def test_ac04_registo_anterior_nao_importado(app_importada):
    """AC-04: Só existe registo anterior ao período: não é importado e surge aviso com o turno."""
    assert entradas_de(app_importada, EP_A, "Vigiar refeição") == []
    avisos = avisos_de(app_importada, EP_A, intervencao="Vigiar refeição")
    assert any("registo anterior ao período" in a and "D1-M" in a for a in avisos)


def test_ac05_sem_registo_nunca_normal(app):
    """AC-05: Ausência de registo no domínio dá 'sem informação importada', nunca 'normal'."""
    app.abrir_episodio(EP_B, "7")
    app.atualizar_a_partir_do_ehr(EP_B, TURNO_ATUAL)
    episodio = app.episodios[EP_B]
    assert set(episodio.estado_dominios.values()) == {"sem_informacao_importada"}
    assert all(AVISO_SEM_INFORMACAO in avisos_de(app, EP_B, dominio=d) for d in episodio.estado_dominios)
    assert episodio.entradas == {}
    assert not any("normal" in a.mensagem.lower() for a in episodio.avisos)


def test_ac06_episodio_incompativel_impede_importacao(app, leitor):
    """AC-06: Dada incompatibilidade de episódio, a transferência é impedida."""
    # Leitor com erro de associação: pedem-lhe o B e devolve registos do A.
    leitor.obter_registos = lambda _id: LeitorOrigemSintetica(FICHEIRO_ORIGEM).obter_registos(EP_A)
    app.abrir_episodio(EP_B, "7")
    resultado = app.atualizar_a_partir_do_ehr(EP_B, TURNO_ATUAL)
    assert resultado.sucesso is False
    assert "outro episódio" in resultado.mensagem
    assert app.episodios[EP_B].entradas == {}


def test_ac07_falha_mantem_conteudo_e_via_manual(app_importada):
    """AC-07: Dada falha de integração, o conteúdo existente permanece e a via manual continua acessível."""
    antes = {c: list(e.linhas) for c, e in app_importada.episodios[EP_A].entradas.items()}
    app_importada.leitor.simular_falha = True

    resultado = app_importada.atualizar_a_partir_do_ehr(EP_A, TURNO_ATUAL)
    depois = {c: list(e.linhas) for c, e in app_importada.episodios[EP_A].entradas.items()}

    assert resultado.sucesso is False
    assert "Preparação manual disponível" in resultado.mensagem
    assert antes == depois
    app_importada.preencher_campo_manual(EP_A, "Último antipirético e hora", "Paracetamol 16h (sintético)")
    assert app_importada.episodios[EP_A].campos_manuais["Último antipirético e hora"]["valor"]


def test_ac08_validacao_associa_versao_episodio_turno_profissional(app_importada):
    """AC-08: Ao validar, ficam associados versão, episódio, turno e profissional."""
    rever_tudo(app_importada, EP_A)
    versao = app_importada.validar(EP_A, "Enf. Transmissor Sintético", TURNO_ATUAL)
    assert (versao.numero, versao.id_episodio, versao.turno, versao.transmissor) == \
        (1, EP_A, TURNO_ATUAL, "Enf. Transmissor Sintético")
    assert app_importada.episodios[EP_A].validado is True


def test_ac09_mudanca_apos_validar_volta_a_por_validar(app_importada):
    """AC-09: Dada uma versão validada, quando o conteúdo muda, volta ao estado por validar."""
    rever_tudo(app_importada, EP_A)
    app_importada.validar(EP_A, "Enf. Transmissor Sintético", TURNO_ATUAL)
    chave = next(iter(app_importada.episodios[EP_A].entradas))
    app_importada.editar(EP_A, chave, ["Alterado depois de validar."])
    assert app_importada.episodios[EP_A].validado is False


def test_ac10_episodio_novo_na_mesma_cama_sem_validacao_herdada(app_importada):
    """AC-10: Episódio novo na mesma cama não herda validação do episódio anterior."""
    rever_tudo(app_importada, EP_A)
    app_importada.validar(EP_A, "Enf. Transmissor Sintético", TURNO_ATUAL)
    app_importada.registar_alta(EP_A)
    novo = app_importada.abrir_episodio(EP_B, "3")
    assert novo.validado is False
    assert novo.versoes == []
    assert novo.entradas == {}


def test_ac11_metadados_registado_por_e_referencia_temporal(app_importada):
    """AC-11: Metadados exibidos como 'registado por' e referência temporal; ausência assinalada."""
    for entrada in app_importada.episodios[EP_A].entradas.values():
        p = entrada.proposta
        assert p.registado_por and p.referencia_temporal
        assert not hasattr(p, "autor")
    # R001 é por turno -> mostra o turno; R040 tem horário -> mostra a hora declarada.
    r001 = entradas_de(app_importada, EP_A, "Vigiar eliminação urinária")[0].proposta
    r040 = entradas_de(app_importada, EP_A, "Monitorizar frequência cardíaca", "medicoes")[0].proposta
    assert r001.referencia_temporal == "Turno D1-T"
    assert r040.referencia_temporal.startswith("Hora declarada 20:00")
    # R002 não tem "registado por" na origem -> a falta é assinalada.
    r002 = entradas_de(app_importada, EP_A, "Vigiar eliminação intestinal")[0].proposta
    assert r002.registado_por == "não disponível na origem"
    assert AVISO_METADADO_EM_FALTA in r002.avisos


def test_ac12_componente_herdavel_com_aviso(app_importada):
    """AC-12: Componente herdável é exibido com aviso de herança."""
    respiracao = entradas_de(app_importada, EP_A, "Avaliar respiração", "frases")[0]
    fc = entradas_de(app_importada, EP_A, "Monitorizar frequência cardíaca", "medicoes")[0]
    assert respiracao.proposta.aviso_heranca is True      # P1, frases: herda
    assert fc.proposta.aviso_heranca is False             # P3, medições: abre em branco


def test_ac13_item_sem_registo_nunca_e_nao(app_importada):
    """AC-13: Item de avaliação sem registo nunca é apresentado como 'não'."""
    linhas = entradas_de(app_importada, EP_A, "Avaliar pele", "arvore")[0].linhas
    assert "Integridade › Edema: sem registo" in linhas
    assert not any("Edema: não" in linha for linha in linhas)
    # O negativo explícito (Úlcera: não) não se mostra, mas indica-se que existe (filtro da Pele).
    assert any("negativo registado" in linha for linha in linhas)


def test_ac14_serie_com_referencia_temporal_e_unidade(app_importada):
    """AC-14: Várias medições de um parâmetro aparecem em série, cada uma com hora e unidade."""
    linhas = entradas_de(app_importada, EP_A, "Monitorizar frequência cardíaca", "medicoes")[0].linhas
    assert linhas == ["FC: 120 bpm (16:00)", "FC: 128 bpm (20:00)"]
    # Valor composto não é separado (C-09).
    ta = entradas_de(app_importada, EP_A, "Monitorizar tensão arterial", "medicoes")[0].linhas
    assert ta == ["TA: 98/60 mmHg (16:00)"]


def test_ac15_valor_de_janela_composta_aparece_uma_vez(app_importada):
    """AC-15: Valor registado através de janela composta aparece uma única vez."""
    ocorrencias = [linha for linha in todas_as_linhas(app_importada, EP_A) if "FC: 128" in linha]
    assert len(ocorrencias) == 1
    assert entradas_de(app_importada, EP_A, "Monitorizar sinais vitais") == []


def test_ac16_campo_de_fonte_externa_manual_e_nao_integrado(app_importada):
    """AC-16: Campo de fonte externa está identificado como manual e não integrado."""
    campo = app_importada.episodios[EP_A].campos_manuais["Último antipirético e hora"]
    assert "não integrada" in campo["origem"]
    assert campo["valor"] == ""                            # a importação não o preenche


def test_ac17_execucao_sem_nota_sem_valor_presumido(app_importada):
    """AC-17: Execução sem nota não mostra nenhum valor presumido de registos anteriores."""
    o2 = entradas_de(app_importada, EP_A, "Gerir oxigenoterapia")
    assert [e.linhas for e in o2] == [["Realizada, sem nota"]]
    # A nota do turno anterior (R044, '3L/min') não aparece em lado nenhum.
    assert not any("L/min" in linha for linha in todas_as_linhas(app_importada, EP_A))


def test_ac18_sem_acao_do_enfermeiro_nada_e_importado(app, leitor):
    """AC-18: Dada a folha aberta sem ação do enfermeiro, nenhum conteúdo é importado."""
    chamadas = []
    original = leitor.obter_registos
    leitor.obter_registos = lambda id_ep: chamadas.append(id_ep) or original(id_ep)
    episodio = app.abrir_episodio(EP_A, "3")
    assert episodio.entradas == {}
    assert chamadas == []                                  # o leitor nem foi chamado


def test_ac19_editar_na_folha_nao_altera_a_origem(app_importada):
    """AC-19: Conteúdo importado e editado na folha deixa a origem inalterada."""
    origem_antes = copy.deepcopy(app_importada.leitor.registos_em_bruto())
    for chave in list(app_importada.episodios[EP_A].entradas):
        app_importada.editar(EP_A, chave, ["Editado."])
    assert app_importada.leitor.registos_em_bruto() == origem_antes

    # Segunda proteção: mesmo que alguém mexa diretamente no que o leitor
    # devolveu, a origem não muda (o leitor entrega cópias).
    devolvidos = app_importada.leitor.obter_registos(EP_A)
    devolvidos[0]["componentes"]["texto_livre"] = "Alterado fora da origem."
    assert app_importada.leitor.registos_em_bruto() == origem_antes


def test_ac20_registo_so_com_componentes_excluidos(app_importada):
    """AC-20: Registo só com componentes excluídos dá o aviso do ALT-12, não 'sem informação importada'."""
    assert entradas_de(app_importada, EP_A, "Vigiar comportamento") == []
    avisos = avisos_de(app_importada, EP_A, dominio="Comportamento")
    assert AVISO_CONTEUDO_NAO_IMPORTADO in avisos
    assert AVISO_SEM_INFORMACAO not in avisos
    assert app_importada.episodios[EP_A].estado_dominios["Comportamento"] == "registo_sem_conteudo_importado"


def test_ac21_unidade_em_falta_assinalada_e_nao_presumida(app_importada):
    """AC-21: Valor sem unidade na origem: a falta é assinalada e nenhuma unidade é presumida."""
    entrada = entradas_de(app_importada, EP_A, "Monitorizar eliminação intestinal", "medicoes")[0]
    assert entrada.linhas == ["Dejeções: 1 [unidade não disponível] (18:00)"]
    assert AVISO_UNIDADE_EM_FALTA in entrada.proposta.avisos


def test_ac22_texto_livre_com_valores_fica_so_texto(app_importada):
    """AC-22: Texto livre com horas e valores aparece só como texto; nada vira campo estruturado."""
    gastrico = entradas_de(app_importada, EP_A, "Vigiar conteúdo gástrico")
    assert [(e.proposta.componente, e.linhas) for e in gastrico] == \
        [("texto_livre", ["16h - 20 ml; 20h - 15 ml"])]
    # Nenhuma medição foi criada a partir deste registo (R031).
    assert not any(c[3] == "SINT-R031" and c[2] == "medicoes"
                   for c in app_importada.episodios[EP_A].entradas)


def test_ac23_validacao_impedida_com_conteudo_por_rever(app_importada):
    """AC-23: Não se valida com propostas por rever ou decisões pendentes; resolvidas, a validação é aceite."""
    # (a) Logo após importar: há propostas por rever -> recusa.
    try:
        app_importada.validar(EP_A, "Enf. Transmissor Sintético", TURNO_ATUAL)
        assert False, "a validação devia ter sido recusada"
    except ErroValidacao as erro:
        assert "faltam rever 12 proposta(s)" in str(erro)
    assert app_importada.episodios[EP_A].validado is False

    # (b) Tudo revisto, mas surge uma decisão pendente -> recusa outra vez.
    rever_tudo(app_importada, EP_A)
    for r in app_importada.leitor.registos_em_bruto():
        if r["id_registo"] == "SINT-R001":
            r["componentes"]["texto_livre"] = "Texto alterado na origem."
    app_importada.atualizar_a_partir_do_ehr(EP_A, TURNO_ATUAL)
    try:
        app_importada.validar(EP_A, "Enf. Transmissor Sintético", TURNO_ATUAL)
        assert False, "a validação devia ter sido recusada"
    except ErroValidacao as erro:
        assert "1 decisão(ões) pendente(s)" in str(erro)

    # (c) Decisão resolvida -> a validação é aceite.
    chave = next(c for c, e in app_importada.episodios[EP_A].entradas.items() if e.decisao_pendente)
    app_importada.resolver_pendente(EP_A, chave, usar_nova=False)
    versao = app_importada.validar(EP_A, "Enf. Transmissor Sintético", TURNO_ATUAL)
    assert versao.numero == 1

    # A folha continua a imprimir mesmo sem validação (WF-02 cobre a marca).


def test_ac24_proposta_retirada_fora_da_folha_e_da_versao(app_importada):
    """AC-24: Proposta retirada conta como revista, mas não entra na folha nem na versão validada."""
    chave = next(c for c in app_importada.episodios[EP_A].entradas if c[1] == "Avaliar respiração")
    rever_tudo(app_importada, EP_A)
    app_importada.retirar(EP_A, chave)
    versao = app_importada.validar(EP_A, "Enf. Transmissor Sintético", TURNO_ATUAL)
    assert chave not in versao.conteudo["entradas"]
    assert "Eupneica" not in gerar_saida(app_importada, TURNO_ATUAL)


def test_ac25_aceitar_tudo_so_aceita_propostas_sem_avisos(app_importada):
    """AC-25: «Aceitar tudo» aceita só propostas sem avisos; as que têm aviso ficam por rever."""
    aceites, por_rever = app_importada.aceitar_tudo_sem_avisos(EP_A)
    entradas = app_importada.episodios[EP_A].entradas.values()

    for entrada in entradas:
        p = entrada.proposta
        if p.aviso_heranca or p.avisos:
            assert entrada.estado == "proposta"      # continua por rever
        else:
            assert entrada.estado == "aceite"

    # Com os dados sintéticos: 5 sem aviso, 7 com aviso (6 de herança, 1 sem unidade).
    assert (aceites, por_rever) == (5, 7)

    # A validação continua recusada enquanto as 7 não forem revistas (C-14).
    try:
        app_importada.validar(EP_A, "Enf. Transmissor Sintético", TURNO_ATUAL)
        assert False, "a validação devia ter sido recusada"
    except ErroValidacao as erro:
        assert "faltam rever 7 proposta(s)" in str(erro)


# ----------------------------------------------------------------------
# Testes do workflow To-Be (docs/02).
# ----------------------------------------------------------------------
def test_wf01_mudanca_de_cama_conteudo_segue_episodio(app_importada):
    """WF-01: Mudança de cama: o conteúdo segue o episódio, sem cópia (To-Be, passo 7)."""
    antes = {c: list(e.linhas) for c, e in app_importada.episodios[EP_A].entradas.items()}
    app_importada.mudar_cama(EP_A, "5")
    episodio = app_importada.episodios[EP_A]
    assert episodio.cama == "5"
    assert {c: list(e.linhas) for c, e in episodio.entradas.items()} == antes
    assert app_importada.episodio_na_cama("3") == []


def test_wf02_impressao_nunca_bloqueada_marca_nao_validado(app_importada):
    """WF-02: A saída de passagem nunca é bloqueada; doente por validar sai como NÃO VALIDADO."""
    app_importada.abrir_episodio(EP_B, "7")                 # aberto, não validado
    rever_tudo(app_importada, EP_A)
    app_importada.validar(EP_A, "Enf. Transmissor Sintético", TURNO_ATUAL)
    texto = gerar_saida(app_importada, TURNO_ATUAL)
    assert "Cama 3 | SINT-EP-A | VALIDADO" in texto
    assert "Cama 7 | SINT-EP-B | NÃO VALIDADO" in texto


def test_wf03_intervencao_condicional_sem_aviso_individual(app_importada):
    """WF-03: Intervenção condicional sem registo não gera aviso individual (ALT-01)."""
    assert avisos_de(app_importada, EP_A, intervencao="Monitorizar eliminação urinária") == []
