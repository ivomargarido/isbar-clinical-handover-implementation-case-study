"""
Percurso de demonstração, para ver o resultado sem ler os testes.

Corre com:  python3 demonstracao.py
DADOS SINTÉTICOS.
"""

from pathlib import Path

from isbar_demo.aplicacao_isbar import AplicacaoISBAR, ErroValidacao
from isbar_demo.configuracao import carregar_configuracao
from isbar_demo.leitor_origem import LeitorOrigemSintetica
from isbar_demo.saida_passagem import gerar_saida

RAIZ = Path(__file__).resolve().parent
TURNO = "D1-T"

# 1. Montar os componentes: leitor (origem sintética), configuração e aplicação.
leitor = LeitorOrigemSintetica(RAIZ / "dados" / "origem_sintetica.json")
configuracao = carregar_configuracao(RAIZ / "dados" / "configuracao.json")
app = AplicacaoISBAR(leitor, configuracao)

# 2. O enfermeiro abre o episódio (nada é importado ainda) e pede a atualização.
app.abrir_episodio("SINT-EP-A", "3")
resultado = app.atualizar_a_partir_do_ehr("SINT-EP-A", TURNO)
print(f"Importação: {resultado.mensagem} Propostas novas: {resultado.novas}\n")

# 3. Mostrar propostas e avisos, como o enfermeiro os veria para rever.
episodio = app.episodios["SINT-EP-A"]
print("PROPOSTAS (provisórias, por rever)")
for (dominio, intervencao, componente, id_registo), entrada in episodio.entradas.items():
    p = entrada.proposta
    marca = "  [pode conter conteúdo de registo anterior]" if p.aviso_heranca else ""
    print(f"- [{dominio}] {intervencao} / {componente}{marca}")
    for linha in entrada.linhas:
        print(f"    {linha}")
    print(f"    registado por: {p.registado_por} | {p.referencia_temporal} | {id_registo}")
    for aviso in p.avisos:
        print(f"    AVISO: {aviso}")

print("\nAVISOS DE DOMÍNIO E INTERVENÇÃO")
for aviso in episodio.avisos:
    alvo = aviso.intervencao or "(domínio)"
    print(f"- [{aviso.dominio}] {alvo}: {aviso.mensagem}")

# 4. Tentar validar sem rever: o sistema recusa (C-14).
try:
    app.validar("SINT-EP-A", "Enf. Transmissor Sintético", TURNO)
except ErroValidacao as erro:
    print(f"\n{erro}")

# 5. «Aceitar tudo» parcial: aceita só as propostas sem avisos (C-14).
aceites, por_rever = app.aceitar_tudo_sem_avisos("SINT-EP-A")
print(f"Aceitar tudo: {aceites} aceites; {por_rever} com aviso ficam por rever, uma a uma.")

# 6. O enfermeiro revê uma a uma as que têm aviso, retira uma proposta e valida.
for chave, entrada in episodio.entradas.items():
    if entrada.estado == "proposta":
        app.aceitar("SINT-EP-A", chave)
chave_respiracao = next(c for c in episodio.entradas if c[1] == "Avaliar respiração")
app.retirar("SINT-EP-A", chave_respiracao)
versao = app.validar("SINT-EP-A", "Enf. Transmissor Sintético", TURNO)
print(f"Validado: versão {versao.numero}, {versao.transmissor}, turno {versao.turno}.")

# 7. Um segundo doente, aberto mas não validado, e a folha de passagem.
app.abrir_episodio("SINT-EP-B", "7")
print("\n" + gerar_saida(app, TURNO))
