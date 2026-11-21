# Demonstração sintética e testes de aceitação

> **Dados sintéticos.** Esta demonstração não liga a nenhum sistema hospitalar e não usa dados de doentes. Episódios, registos, profissionais e valores são inventados. Não é integração implementada nem validação institucional.

No serviço só está implementada e em uso a folha de passagem de turno em
Word/VBA. Base de dados, tratamento de dados e indicadores não existem.
Este código simula, com dados sintéticos, a proposta descrita em:

- [docs/01](01_UC-01_especificacao_funcional.md): especificação funcional UC-01 (regras C-01 a C-14, critérios AC-01 a AC-25);
- [docs/02](02_workflow_to-be_e_arquitetura.md): workflow To-Be e arquitetura conceptual.

## Como correr

Requer Python 3.10 ou superior e `pytest`.

```bash
python demonstracao.py           # importa, mostra propostas e avisos, valida e gera a folha
python -m pytest testes -v       # corre os testes e escreve resultados_testes.md
```

## Estrutura

| Ficheiro | Componente da arquitetura (docs/02) |
|---|---|
| `dados/origem_sintetica.json` | 1. Origem clínica (sintética) |
| `isbar_demo/leitor_origem.py` | 2. Leitor de origem (só lê, entrega cópias) |
| `dados/configuracao.json`, `isbar_demo/configuracao.py` | 3. Configuração por serviço e domínio |
| `isbar_demo/motor_importacao.py` | 4. Motor de importação (regras Core) |
| `isbar_demo/aplicacao_isbar.py` | 5. Aplicação de passagem de turno e 6. Versões e validação |
| `isbar_demo/saida_passagem.py` | 7. Saída de passagem (texto, em vez de PDF) |
| `testes/test_criterios_aceitacao.py` | AC-01 a AC-25 e três testes do workflow (WF-01 a WF-03) |
| `resultados_testes.md` | Tabela gerada automaticamente em cada execução |
| `docs/04_guia_de_leitura_dos_testes.md` | O que cada teste verifica, em linguagem corrente |

## Dados sintéticos

- Dois turnos: D1-M (anterior) e D1-T (atual, período de referência).
- Episódio SINT-EP-A, cama 3: registos nos cinco domínios, construídos para
  cobrir os critérios (herança, várias medições, unidade em falta, texto
  livre com valores, componente excluído, registo só no turno anterior,
  execução sem nota, janela composta, «registado por» em falta).
- Episódio SINT-EP-B: sem registos; serve para «sem informação importada»,
  episódio incompatível e episódio novo na mesma cama.
- Os nomes das intervenções geradas a partir de «Monitorizar sinais vitais»
  (por exemplo, «Monitorizar frequência cardíaca») são aproximações; os
  nomes reais estão por confirmar (docs/01, secção 9).

## Resultado

Os 28 testes passam: 25 critérios de aceitação e 3 testes do workflow
(mudança de cama, impressão nunca bloqueada, intervenção condicional sem
aviso). Ver `resultados_testes.md`.

Para confirmar que os testes não passam por acaso, estraguei de propósito
cada regra principal, uma de cada vez (C-01, C-02, C-03, C-06, C-08, C-09,
C-14, o AC-13, o bloqueio da validação e o «aceitar tudo» parcial), e
verifiquei que pelo menos um teste falhava. No caso da proteção da origem
(C-03), o teste não deu pelo erro à primeira; reforcei o AC-19 e passou a
detetá-lo.

## Limites

- Sem interface, sem base de dados, sem autenticação, sem trilho de
  auditoria, sem ligação a sistemas reais.
- A saída de passagem é texto simples, não PDF.
- Os testes confirmam que o código cumpre os critérios escritos. Não
  confirmam que os critérios são clinicamente adequados nem que a proposta
  poupa tempo; isso exigiria revisão clínica e medição em contexto
  autorizado.
