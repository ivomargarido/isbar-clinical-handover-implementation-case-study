# Passagem de turno ISBAR: case study de implementação configurável

> **Âmbito.** No meu serviço só está implementada e em uso uma folha de passagem de turno em Word/VBA, organizada segundo o método ISBAR e feita por mim. Base de dados, tratamento de dados e indicadores não existem. Este repositório é um case study conceptual: especificação, workflow, demonstração com **dados sintéticos** e plano de implementação. Não há integração com sistemas hospitalares nem dados de doentes.

Sou enfermeiro há 8 anos numa urgência pediátrica e unidade de cuidados especiais pediátricos de um hospital da Grande Lisboa. Da passagem de turno depende a continuidade dos cuidados e a segurança da criança.

Criei uma folha de passagem de turno em Word que, na minha perceção, tornou a passagem mais fácil para mim e para a equipa. Há um problema que a folha não resolve: durante o turno, registamos a mesma informação duas vezes, primeiro no SClínico e depois na folha.

Este case study pergunta o que seria preciso para a folha receber esses registos sem tirar o controlo a quem passa o turno.

## O que existe e o que não existe

| | Estado |
|---|---|
| Folha de passagem de turno em Word/VBA | Em uso no serviço. Não faz parte deste repositório. |
| Especificação funcional, workflow, plano de implementação | Conceptual. |
| Demonstração em Python | Funciona, com dados sintéticos e sem interface. |
| Ligação ao SClínico ou a outro sistema | Não existe. Não foi verificada nenhuma interface. |

## Uma primeira fase

Isto é uma primeira fase, não um desenho fechado. As intervenções que usei como fonte dos registos são as que me ocorreram a partir da minha prática; consoante os problemas de cada criança, outras fariam sentido. Antes de qualquer uso no serviço, a escolha das intervenções, dos componentes a importar e das próprias regras teria de ser avaliada e trabalhada com a equipa, para ajustar a proposta às necessidades reais do serviço. A configuração foi pensada para isso: acrescentar ou trocar intervenções não obriga a mudar as regras.

## Como ler este repositório

| Documento | O que tem |
|---|---|
| [01 · Especificação funcional (UC-01)](docs/01_UC-01_especificacao_funcional.md) | Regras (C-01 a C-14), cenários alternativos e 25 critérios de aceitação. A estrutura de origem foi observada por mim no ecrã, sem levantamento autorizado. |
| [02 · Workflow To-Be e arquitetura](docs/02_workflow_to-be_e_arquitetura.md) | Como a passagem funciona hoje, como funcionaria com importação, o que não resolve e os componentes. |
| [03 · Demonstração sintética](docs/03_demonstracao_sintetica.md) | O que o código simula e os resultados dos testes. |
| [04 · Guia de leitura dos testes](docs/04_guia_de_leitura_dos_testes.md) | Cada teste numa linha, sem código: a situação, o que se espera, a regra. |
| [05 · Plano de implementação](docs/05_plano_de_implementacao.md) | Plano genérico, com as lições reais de pôr a folha Word em uso. |

Os diagramas estão em Mermaid e aparecem como gráficos no GitHub.

## Demonstração

Requer Python 3.10 ou superior.

```bash
pip install -r requirements.txt
python demonstracao.py           # importa, mostra propostas e avisos, valida e gera a folha
python -m pytest testes -v       # corre os testes e escreve resultados_testes.md
```

Resultado: **28 de 28 testes passam** (25 critérios de aceitação e 3 testes do workflow). Para confirmar que os testes não passam por acaso, estraguei cada regra principal de propósito, uma de cada vez, e verifiquei que pelo menos um teste falhava. Num caso o teste não deu pelo erro à primeira e foi reforçado.

Algumas decisões que os testes verificam:

- nada é importado sem o enfermeiro pedir, e o registo de origem nunca é alterado;
- um item sem registo nunca aparece como «não»;
- valores escritos em texto livre ficam como texto, sem extração;
- não se valida um doente com propostas por rever; «aceitar tudo» só aceita as que não têm aviso;
- a impressão da folha nunca é bloqueada: o doente por validar sai marcado.

## Limites

Os testes confirmam que o código cumpre os critérios escritos. Não confirmam que os critérios são clinicamente adequados nem que a proposta poupa tempo. Isso exigiria revisão clínica, autorização institucional e medição no serviço.

## Apoio de IA

Defini as regras e os critérios de aceitação a partir da prática da passagem de turno. O código, os testes e parte da redação foram feitos com apoio de IA (Claude). Confirmei que cada teste verifica o critério que diz verificar e corri os testes no meu computador.

## Autor

Ivo Margarido, enfermeiro.
