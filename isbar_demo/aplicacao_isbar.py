"""
Componentes 5 e 6: aplicação de passagem de turno, versões e validação.

O conteúdo da folha pertence ao EPISÓDIO, não à cama. A cama é só a
localização (C-02). Por isso, mudar de cama não obriga a copiar nada.

Regras aplicadas aqui:
    C-01 só se importa quando o enfermeiro pede
    C-03 editar na folha não altera a origem
    C-12 campos de fonte externa ficam manuais
    C-14 nada é substituído em silêncio; validação por episódio, turno e
         transmissor; qualquer mudança depois de validar volta a "por validar"
         e não se valida com propostas por rever ou decisões pendentes
"""

import copy
from dataclasses import dataclass, field

from .leitor_origem import ErroAcessoOrigem
from .motor_importacao import importar


# ----------------------------------------------------------------------
# Estruturas de dados da folha.
# ----------------------------------------------------------------------
class ErroValidacao(Exception):
    """A validação foi recusada porque ainda há conteúdo por rever."""


@dataclass
class EntradaISBAR:
    """Um componente na folha, com a origem identificada."""

    proposta: object                  # a Proposta que lhe deu origem
    linhas: list                      # o conteúdo atual (pode ter sido editado)
    estado: str = "proposta"          # proposta (por rever) | aceite | editada | retirada
    decisao_pendente: list = None     # conteúdo novo da origem, à espera de decisão


@dataclass
class Versao:
    """Fotografia da folha de um episódio, no momento em que foi validada."""

    numero: int
    id_episodio: str
    turno: str
    transmissor: str
    conteudo: dict


@dataclass
class EpisodioISBAR:
    id_episodio: str
    cama: str
    entradas: dict = field(default_factory=dict)        # chave -> EntradaISBAR
    avisos: list = field(default_factory=list)          # avisos da última importação
    estado_dominios: dict = field(default_factory=dict)
    campos_manuais: dict = field(default_factory=dict)  # campo -> {"valor", "origem"}
    versoes: list = field(default_factory=list)
    validado: bool = False


@dataclass
class ResultadoAtualizacao:
    sucesso: bool
    mensagem: str
    novas: int = 0
    pendentes: int = 0


# ----------------------------------------------------------------------
# A aplicação.
# ----------------------------------------------------------------------
class AplicacaoISBAR:
    def __init__(self, leitor, configuracao):
        self.leitor = leitor
        self.configuracao = configuracao
        self.episodios = {}          # id_episodio -> EpisodioISBAR

    # -------------------------- abrir e localizar --------------------------
    def abrir_episodio(self, id_episodio, cama):
        """
        Abre (ou cria) a folha do episódio.
        C-01: abrir NÃO importa nada. Só "atualizar_a_partir_do_ehr" importa.
        """
        if id_episodio not in self.episodios:
            episodio = EpisodioISBAR(id_episodio=id_episodio, cama=cama)
            # C-12: os campos de fonte externa existem desde o início, vazios
            # e marcados como manuais e não integrados.
            for campo in self.configuracao["campos_manuais"]:
                episodio.campos_manuais[campo["campo"]] = {"valor": "", "origem": campo["origem"]}
            self.episodios[id_episodio] = episodio
        return self.episodios[id_episodio]

    def mudar_cama(self, id_episodio, nova_cama):
        """
        Mudança de cama: muda a localização; o conteúdo segue o episódio.
        Não há nada para copiar (docs/02, To-Be, passo 7).
        """
        self.episodios[id_episodio].cama = nova_cama

    def episodio_na_cama(self, cama):
        """Devolve os episódios que estão numa cama (pode haver um novo na mesma cama)."""
        return [e for e in self.episodios.values() if e.cama == cama]

    def registar_alta(self, id_episodio):
        """A alta liberta a cama. O episódio e as suas versões não passam para ninguém."""
        self.episodios[id_episodio].cama = None

    # -------------------------- importação --------------------------
    def atualizar_a_partir_do_ehr(self, id_episodio, turno_atual):
        """
        Ação explícita do enfermeiro (C-01).
        Se a origem falhar, o conteúdo existente fica intacto (ALT-07).
        """
        episodio = self.episodios[id_episodio]

        try:
            registos = self.leitor.obter_registos(id_episodio)
        except ErroAcessoOrigem as erro:
            return ResultadoAtualizacao(False, f"Falha de acesso à origem: {erro} Preparação manual disponível.")

        resultado = importar(id_episodio, registos, self.configuracao,
                             turno_atual, self.leitor.ordem_dos_turnos())

        if resultado.bloqueada:
            # C-02 / AC-06: nada entra.
            return ResultadoAtualizacao(False, resultado.motivo_bloqueio)

        episodio.avisos = resultado.avisos
        episodio.estado_dominios = resultado.estado_dominios

        novas, pendentes = 0, 0
        for proposta in resultado.propostas:
            existente = episodio.entradas.get(proposta.chave)

            if existente is None:
                # Proposta nova: entra como provisória.
                episodio.entradas[proposta.chave] = EntradaISBAR(proposta=proposta, linhas=list(proposta.linhas))
                novas += 1
            elif existente.linhas != proposta.linhas:
                # C-14 / ALT-05 / ALT-06: há diferença, mas não se substitui.
                # Guarda-se como decisão pendente para o enfermeiro decidir.
                existente.decisao_pendente = list(proposta.linhas)
                pendentes += 1

        if novas:
            self._houve_alteracao(episodio)

        return ResultadoAtualizacao(True, "Importação concluída.", novas, pendentes)

    # -------------------------- revisão --------------------------
    def aceitar(self, id_episodio, chave):
        entrada = self.episodios[id_episodio].entradas[chave]
        entrada.estado = "aceite"
        self._houve_alteracao(self.episodios[id_episodio])

    def editar(self, id_episodio, chave, novas_linhas):
        """C-03: edita só a folha. A origem fica exatamente como estava."""
        entrada = self.episodios[id_episodio].entradas[chave]
        entrada.linhas = list(novas_linhas)
        entrada.estado = "editada"
        self._houve_alteracao(self.episodios[id_episodio])

    def aceitar_tudo_sem_avisos(self, id_episodio):
        """
        «Aceitar tudo» parcial (C-14).

        Aceita de uma vez só as propostas SEM avisos. As que têm aviso
        (herança, unidade em falta, "registado por" em falta) ou uma decisão
        pendente ficam por rever, uma a uma, porque podem estar desatualizadas.

        Devolve (quantas foram aceites, quantas ficaram por rever).
        """
        episodio = self.episodios[id_episodio]
        aceites, por_rever = 0, 0
        for entrada in episodio.entradas.values():
            if entrada.estado != "proposta":
                continue                        # já revista: não se mexe
            tem_aviso = (
                entrada.proposta.aviso_heranca
                or entrada.proposta.avisos
                or entrada.decisao_pendente is not None
            )
            if tem_aviso:
                por_rever += 1
            else:
                entrada.estado = "aceite"
                aceites += 1
        if aceites:
            self._houve_alteracao(episodio)
        return aceites, por_rever

    def retirar(self, id_episodio, chave):
        """
        O enfermeiro decide que esta proposta não entra na folha.
        A entrada fica marcada como retirada (não se apaga), para se saber
        que foi revista. Não entra na folha de passagem nem na versão validada.
        """
        entrada = self.episodios[id_episodio].entradas[chave]
        entrada.estado = "retirada"
        self._houve_alteracao(self.episodios[id_episodio])

    def resolver_pendente(self, id_episodio, chave, usar_nova):
        """
        ALT-05 / ALT-06: o enfermeiro decide sobre conteúdo novo vindo da origem.
        usar_nova=True  -> substitui pelo conteúdo novo
        usar_nova=False -> mantém o que está na folha
        """
        entrada = self.episodios[id_episodio].entradas[chave]
        if usar_nova:
            entrada.linhas = entrada.decisao_pendente
            entrada.estado = "aceite"
        entrada.decisao_pendente = None
        self._houve_alteracao(self.episodios[id_episodio])

    def por_rever(self, id_episodio):
        """Conta o que ainda impede a validação: propostas por abrir e decisões pendentes."""
        entradas = self.episodios[id_episodio].entradas.values()
        propostas = sum(1 for e in entradas if e.estado == "proposta")
        pendentes = sum(1 for e in entradas if e.decisao_pendente is not None)
        return propostas, pendentes

    def preencher_campo_manual(self, id_episodio, campo, valor):
        self.episodios[id_episodio].campos_manuais[campo]["valor"] = valor
        self._houve_alteracao(self.episodios[id_episodio])

    # -------------------------- validação e versões --------------------------
    def validar(self, id_episodio, transmissor, turno):
        """
        C-14: a validação fica associada a episódio, turno, transmissor e versão.
        Guarda uma cópia do conteúdo nesse momento.

        Não se valida enquanto houver propostas por
        rever ou decisões pendentes. "Validado" quer dizer que alguém olhou.
        A folha de passagem continua a poder ser impressa (sai NÃO VALIDADO).
        """
        propostas, pendentes = self.por_rever(id_episodio)
        if propostas or pendentes:
            raise ErroValidacao(
                f"Validação impedida: faltam rever {propostas} proposta(s) "
                f"e {pendentes} decisão(ões) pendente(s)."
            )

        episodio = self.episodios[id_episodio]
        fotografia = {
            "entradas": {chave: list(e.linhas) for chave, e in episodio.entradas.items()
                         if e.estado != "retirada"},
            "campos_manuais": copy.deepcopy(episodio.campos_manuais),
        }
        versao = Versao(
            numero=len(episodio.versoes) + 1,
            id_episodio=id_episodio,
            turno=turno,
            transmissor=transmissor,
            conteudo=fotografia,
        )
        episodio.versoes.append(versao)
        episodio.validado = True
        return versao

    def _houve_alteracao(self, episodio):
        """C-14 / AC-09: qualquer mudança depois de validar volta a 'por validar'."""
        episodio.validado = False
