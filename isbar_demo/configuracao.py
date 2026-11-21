"""
Componente 3: configuração por serviço e domínio.

Tudo o que muda de serviço para serviço está no ficheiro de configuração,
e não no código. Critério de desenho da UC-01: acrescentar uma intervenção
a um domínio deve ser só configuração, sem mudar nenhuma regra Core.
"""

import json
from pathlib import Path


def carregar_configuracao(caminho_ficheiro):
    """Lê o ficheiro JSON de configuração e devolve-o como dicionário."""
    return json.loads(Path(caminho_ficheiro).read_text(encoding="utf-8"))


def heranca_do_componente(configuracao, padrao, componente):
    """
    Diz se um componente herda conteúdo do registo anterior.

    Devolve 'herda', 'em_branco' ou 'por_confirmar' (docs/01, secção 4.1).
    """
    return configuracao["heranca_por_padrao"][padrao].get(componente, "por_confirmar")


def intervencoes_configuradas(configuracao):
    """
    Percorre a configuração e devolve pares (domínio, definição da intervenção).

    Exemplo de definição:
        {"intervencao": "Avaliar pele", "padrao": "P2", "componentes": [...]}
    """
    for dominio, intervencoes in configuracao["dominios"].items():
        for definicao in intervencoes:
            yield dominio, definicao
