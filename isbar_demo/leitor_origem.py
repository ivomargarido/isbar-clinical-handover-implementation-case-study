"""
Componentes 1 e 2: origem clínica (sintética) e leitor de origem.

Numa implementação real, o leitor dependeria de uma interface autorizada
com o EHR, que NÃO foi verificada. Aqui, o leitor só lê um ficheiro JSON
com dados sintéticos.

Regra importante: o leitor só LÊ. Nunca escreve na origem (C-03).
"""

import copy
import json
from pathlib import Path


class ErroAcessoOrigem(Exception):
    """Falha ao aceder à origem (usada para simular o ALT-07)."""


class LeitorOrigemSintetica:
    """Lê registos sintéticos a partir de um ficheiro JSON."""

    def __init__(self, caminho_ficheiro, simular_falha=False):
        # Carregamos o ficheiro uma vez. 'simular_falha' permite testar
        # o que acontece quando a origem não responde (AC-07).
        self._dados = json.loads(Path(caminho_ficheiro).read_text(encoding="utf-8"))
        self.simular_falha = simular_falha

    # ------------------------------------------------------------------
    # Turnos: precisamos da ordem para saber o que é "anterior ao período".
    # ------------------------------------------------------------------
    def ordem_dos_turnos(self):
        """Devolve um dicionário {id_turno: ordem}, por exemplo {'D1-M': 1}."""
        return {t["id"]: t["ordem"] for t in self._dados["turnos"]}

    # ------------------------------------------------------------------
    # Registos de um episódio.
    # ------------------------------------------------------------------
    def obter_registos(self, id_episodio):
        """
        Devolve CÓPIAS dos registos do episódio pedido.

        Devolvemos cópias para que nada do que a folha faça depois
        (editar, aceitar) consiga alterar a origem (C-03, AC-19).
        """
        if self.simular_falha:
            raise ErroAcessoOrigem("Origem indisponível (falha simulada).")

        registos = [r for r in self._dados["registos"] if r["id_episodio"] == id_episodio]
        return copy.deepcopy(registos)

    def registos_em_bruto(self):
        """Acesso direto aos dados, só para os testes confirmarem que a origem não mudou."""
        return self._dados["registos"]
