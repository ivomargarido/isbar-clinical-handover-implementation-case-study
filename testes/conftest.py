"""
Preparação comum aos testes e escrita da tabela de resultados.

Cada teste começa com uma aplicação nova, para que nenhum teste
dependa do que outro fez antes.
"""

import sys
from datetime import datetime
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from isbar_demo.aplicacao_isbar import AplicacaoISBAR  # noqa: E402
from isbar_demo.configuracao import carregar_configuracao  # noqa: E402
from isbar_demo.leitor_origem import LeitorOrigemSintetica  # noqa: E402

FICHEIRO_ORIGEM = RAIZ / "dados" / "origem_sintetica.json"
FICHEIRO_CONFIG = RAIZ / "dados" / "configuracao.json"
TURNO_ATUAL = "D1-T"


@pytest.fixture
def leitor():
    return LeitorOrigemSintetica(FICHEIRO_ORIGEM)


@pytest.fixture
def configuracao():
    return carregar_configuracao(FICHEIRO_CONFIG)


@pytest.fixture
def app(leitor, configuracao):
    return AplicacaoISBAR(leitor, configuracao)


@pytest.fixture
def app_importada(app):
    """Aplicação com o episódio A aberto na cama 3 e já importado no turno atual."""
    app.abrir_episodio("SINT-EP-A", "3")
    app.atualizar_a_partir_do_ehr("SINT-EP-A", TURNO_ATUAL)
    return app


# ----------------------------------------------------------------------
# Tabela de resultados: cada teste tem uma docstring "AC-xx: critério".
# No fim da execução, escrevemos resultados_testes.md.
# ----------------------------------------------------------------------
_resultados = []


def pytest_runtest_logreport(report):
    if report.when == "call" or (report.when == "setup" and report.outcome != "passed"):
        _resultados.append((report.nodeid, report.outcome))


def pytest_sessionfinish(session, exitstatus):
    descricoes = {}
    for item in session.items:
        doc = (item.function.__doc__ or "").strip().splitlines()
        descricoes[item.nodeid] = doc[0] if doc else item.name

    linhas = [
        "# Resultados dos testes de aceitação",
        "",
        f"Execução: {datetime.now():%Y-%m-%d %H:%M}. DADOS SINTÉTICOS.",
        "",
        "| Critério | Resultado |",
        "|---|---|",
    ]
    for nodeid, resultado in _resultados:
        estado = {"passed": "PASSOU", "failed": "FALHOU"}.get(resultado, resultado.upper())
        linhas.append(f"| {descricoes.get(nodeid, nodeid)} | {estado} |")

    total = len(_resultados)
    passaram = sum(1 for _, r in _resultados if r == "passed")
    linhas += ["", f"Total: {passaram} de {total} passaram."]
    (RAIZ / "resultados_testes.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")
