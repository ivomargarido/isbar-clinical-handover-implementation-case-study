# Plano de implementação no serviço

Versão 0.1 · novembro de 2026

> **Estado:** plano conceptual e genérico. Não é um plano aprovado nem em execução, não tem datas nem pessoas reais, e é distinto de qualquer plano institucional.

No serviço só está implementada e em uso a folha de passagem de turno em
Word/VBA. Base de dados, tratamento de dados e indicadores não existem. A
proposta que este plano implementaria ([docs/01](01_UC-01_especificacao_funcional.md)
e [docs/02](02_workflow_to-be_e_arquitetura.md)) é conceptual e foi testada
apenas com dados sintéticos ([docs/03](03_demonstracao_sintetica.md)).

A secção 1 é experiência real: o que aprendi ao pôr a folha de passagem de
turno em uso no meu serviço, contado de memória e sem medição. As restantes
secções são proposta.

# 1. O que aprendi com a folha de passagem de turno

| # | O que aconteceu | Consequência no plano |
|---|---|---|
| 1 | A equipa aderiu depressa. Na minha perceção, porque os botões tornaram o registo mais fácil desde o primeiro dia. Não medi. | O ganho tem de ser visível no primeiro turno. A proposta tira a escrita em dobro mas acrescenta revisão e validação: esse saldo é o principal risco de adesão (R1). |
| 2 | Fiz a formação um a um, a mostrar as funcionalidades a cada colega. | Formação curta junto ao posto, apoiada por colegas de referência, para não depender de uma pessoa. |
| 3 | A equipa começou a usar a folha antes de eu terminar as correções. O suporte ficou comigo, com problemas quase todos os dias. | Uso real só depois de um critério de saída dos testes. Versão de teste separada da oficial. Registo de problemas. Suporte distribuído e limitado no tempo. |
| 4 | Ensinei três colegas a cuidar da folha em pormenor, e o trabalho diário de correções foi desaparecendo. | Colegas de referência escolhidos antes do arranque, com formação aprofundada; são a primeira linha de suporte. |
| 5 | Um erro persistente (texto fora dos campos) só ficou resolvido quando o reproduzi com a colega que o provocava. | Erros reportados reproduzem-se com quem os encontrou, antes de corrigir. |
| 6 | Uma regra de validação no fecho bloqueia a impressão estruturada; quando isso acontece, a equipa imprime diretamente do Word, sem estrutura e com mais papel. | Uma regra que impede a saída não impede a passagem, só a desorganiza. A impressão nunca é bloqueada; o doente sai «NÃO VALIDADO» (docs/02). |
| 7 | A recuperação depende de poucas pessoas e de passos manuais: copiar doente a doente para um modelo de reserva, mudar o nome, apagar o ficheiro com erro; desproteger e voltar a proteger. Uma vez a proteção não foi reposta e a estrutura da folha acabou alterada. | Procedimentos de manutenção escritos. Passos críticos automáticos ou confirmados. Administração nominal e registada. Nunca apagar a versão com erro antes de perceber o que aconteceu. Esconder um ficheiro não é protegê-lo. |
| 8 | Preparei a folha para uma futura base de dados pseudonimizada, que não avançou. | Proteção de dados (acesso, retenção, pseudonimização, aprovação) tratada antes do arranque, como pré-condição. |

Cronologia, com a incerteza que tem: a folha está em uso pelo menos desde
o início de setembro de 2026. Houve correções quase diárias no início e
poucas ou nenhumas a partir do fim de setembro ou início de outubro, por
estimativa minha. A exceção foi o erro de texto fora dos campos, corrigido
em novembro, sem novos casos reportados desde então.

# 2. Pré-condições (antes de começar)

- Interface autorizada com a origem, ou decisão explícita de não a ter.
- Intervenções de referência, componentes a importar e regras revistos com
  a equipa do serviço, a partir desta primeira proposta, e validados por
  enfermeiros como clinicamente adequados. A lista atual é um ponto de
  partida, não uma lista fechada.
- Proteção de dados aprovada: quem acede, o que se guarda, por quanto
  tempo, e se há pseudonimização.
- Plano B escrito e testado: via manual (ALT-07) e impressão sem bloqueio.
- Ambiente de teste separado do oficial, só com dados fictícios.
- Colegas de referência escolhidos e formados.
- Procedimentos de manutenção escritos.
- Medição de base recolhida (secção 7).

# 3. Papéis (genéricos)

| Papel | Responsabilidade |
|---|---|
| Enfermeiro responsável clínico do projeto | Regras, critérios de aceitação, configuração, decisões de comportamento. |
| Chefia de enfermagem | Patrocínio, tempo para formação, decisão de avançar, ajustar ou parar. |
| Colegas de referência | Formação na equipa, primeira linha de suporte, registo de problemas. |
| Enfermeiros utilizadores | Uso, revisão e validação por doente; reporte de problemas. |
| Sistemas de informação | Interface, ambientes, segurança, cópias de segurança. |
| Proteção de dados | Parecer sobre acesso, retenção e pseudonimização. |
| Manutenção técnica | Alterações à ferramenta, com teste, uma de cada vez. |

# 4. Fases

| Fase | Objetivo | Entregáveis | Critério de saída |
|---|---|---|---|
| 1 Preparação | Cumprir as pré-condições | Lista de pré-condições assinada | Todas cumpridas ou dispensadas por escrito |
| 2 Configuração e testes | Configurar e testar com dados fictícios | Configuração; AC-01 a AC-24 executados no ambiente de teste | Todos os critérios passam; nenhum erro que comprometa o uso |
| 3 Formação | Preparar a equipa | Sessões curtas junto ao posto; formação aprofundada dos colegas de referência | Colegas de referência autónomos; equipa informada da mudança de prática |
| 4 Piloto controlado | Usar em contexto real, em âmbito limitado: primeiro numa área de internamento com menor volume e permanência até 24 horas (cerca de três turnos, o que permite testar continuidade e herança); depois numa área de maior permanência | Registo de problemas; medição | Critérios da secção 8 cumpridos em cada fase do piloto |
| 5 Estabilização | Corrigir e consolidar, com acompanhamento próximo e limitado no tempo | Correções testadas; procedimentos atualizados | Pedidos de suporte em descida e sem erros graves |
| 6 Avaliação e decisão | Decidir com base na medição | Relatório antes/depois | Decisão: avançar, ajustar ou parar |

# 5. Mudança de prática

O que muda para o enfermeiro (docs/02):

- deixa de escrever em dobro o conteúdo coberto pela importação;
- passa a rever cada proposta (aceitar, editar, retirar) e só depois
  valida;
- a validação por doente substitui a confirmação verbal em equipa antes da
  impressão;
- na mudança de cama deixa de copiar campos.

O que não muda: a passagem continua oral, no gabinete; a folha antiga
anotada à mão pode continuar a circular.

A revisão obrigatória antes de validar é a mudança com mais custo. Tem de
ser explicada: «validado» passa a querer dizer que alguém olhou.

# 6. Riscos e mitigação

| # | Risco | Mitigação |
|---|---|---|
| R1 | O trabalho acrescentado (revisão, validação) supera o poupado e a adesão cai | Medição antes/depois; ajustar a configuração (menos componentes importados); critério de paragem |
| R2 | Validação por rotina, sem rever | Revisão obrigatória antes de validar (C-14); «aceitar tudo» parcial: aceita só propostas sem avisos, e as que têm aviso (herança, unidade em falta, registado por em falta) revêm-se uma a uma |
| R3 | Conteúdo antigo na folha contínua parece atual | Risco residual da UC-01; revisão humana em cada turno. O «aceitar tudo» parcial protege só as propostas importadas, não o conteúdo que já está na folha |
| R4 | Falha da origem | Via manual (ALT-07); conteúdo existente preservado |
| R5 | Suporte dependente de uma ou poucas pessoas | Colegas de referência; procedimentos escritos; administração nominal |
| R6 | Alteração indevida da estrutura da ferramenta | Permissões; reposição automática da proteção; registo de alterações |
| R7 | Dados pessoais em saídas arquivadas | Pré-condição de proteção de dados; retenção definida |
| R8 | Uso real antes de estabilizar | Critério de saída da fase 2; versão de teste separada |
| R9 | Folha antiga anotada à mão circula na passagem | Fora do âmbito da ferramenta; tratar como prática na formação |

# 7. Medição antes e depois (só definições)

Regras: só valores agregados; sem avaliação de profissionais (C-13);
medição de base recolhida antes de qualquer mudança. Não há valores neste
documento.

| Medida | Definição |
|---|---|
| Tempo de preparação da passagem | Minutos por doente para preparar a folha, por amostragem |
| Escrita em dobro | Campos escritos à mão que já existiam no registo de origem |
| Qualidade das propostas | Proporção de propostas editadas ou retiradas |
| Doentes por validar | Doentes impressos com «NÃO VALIDADO», por turno |
| Uso do «aceitar tudo» | Proporção de revisões feitas com «aceitar tudo» |
| Pedidos de suporte | Número e tipo, por semana |
| Falhas de importação | Número, por semana |
| Perceção da equipa | Inquérito curto antes e depois |

# 8. Avançar, ajustar, parar e voltar atrás

- **Avançar:** critérios da fase 4 cumpridos; sem erros graves; perceção
  da equipa sem agravamento.
- **Ajustar:** propostas muito editadas ou retiradas; tempo de preparação
  sem melhoria. Reduz-se ou muda-se a configuração e repete-se o piloto.
- **Parar:** qualquer importação para o episódio errado; perda de conteúdo;
  pedidos de suporte sem descida.
- **Voltar atrás:** regressar à folha atual. O plano B tem de estar testado
  antes do piloto.

Os limiares concretos definem-se com a equipa antes do piloto.

# 9. Manutenção e suporte

- Um responsável nominal pela configuração.
- Alterações uma de cada vez, testadas no ambiente de teste, com teste de
  aceitação, antes de chegarem à versão oficial.
- Procedimentos de recuperação escritos; a versão com erro guarda-se
  antes de corrigir.
- Modelo de recuperação num local controlado e só de leitura, não
  escondido.
- Cópias de segurança testadas: alguém experimenta repor uma cópia antes de
  ser preciso.
- Registo de problemas, com quem reportou e como se reproduziu.

# 10. Limites

Plano genérico e conceptual. Não substitui avaliação institucional,
parecer de proteção de dados nem decisão da chefia. Não define datas,
duração do piloto nem pessoas. A secção 1 é experiência real, contada de
memória, sem medição.

# 11. Decisões

| Decisão | Estado |
|---|---|
| «Aceitar tudo» parcial: aceita só propostas sem avisos; as que têm aviso revêm-se uma a uma | Decidido; incluído na UC-01 (C-14) e testado na demonstração (AC-25) |
| Piloto em duas fases: área de menor volume e permanência até 24 horas; depois área de maior permanência | Decidido |
| Limiares dos critérios da secção 8 | A definir com a equipa e a chefia, antes do piloto |
