# UC-01 | Reutilização de registos de enfermagem na folha de passagem de turno

Especificação funcional preliminar · Versão 0.5 · novembro de 2026

> **Estado:** proposta conceptual. Não é integração implementada nem tem validação institucional. Os critérios de aceitação foram executados apenas numa demonstração com dados sintéticos ([docs/03](03_demonstracao_sintetica.md)).

# 1. Objetivo e limites

Permitir que um enfermeiro, por ação explícita, obtenha registos
associados a intervenções de enfermagem de referência e os use como
proposta de conteúdo nos domínios da folha de passagem de turno. O
conteúdo é revisto, pode ser editado, e a versão final é validada pelo
enfermeiro que transmite aquele doente no turno.

A obtenção de dados do SClínico é apenas conceptual. Não se afirma acesso
às estruturas internas, à API, aos códigos CIPE nem autorização
institucional.

Origem da informação: a estrutura das janelas de registo descrita neste
documento é a que vejo no ecrã do sistema em uso no meu serviço. Não houve
levantamento institucional autorizado, extração de dados nem uso de dados
de doentes, e não se incluem capturas de ecrã. Ao longo do documento,
«observado» indica o que vi diretamente, «declarado» o que descrevo da
prática sem o ter verificado no ecrã para este documento, e «por
confirmar» o que falta confirmar.

# 2. Rastreabilidade do problema

| **Observação no contexto real** | **Implicação funcional** |
|---|---|
| Registos estruturados do EHR nem sempre fornecem uma síntese adequada à passagem de turno. | Reutilização de registos produzidos no contexto clínico, com revisão humana. |
| Atualizar a folha à mão duplica informação já documentada no EHR. | Importação controlada e edição sem reescrever tudo. |
| A folha de passagem de turno é contínua: cada enfermeiro atualiza o conteúdo deixado pelo turno anterior. | A continuidade entre turnos vem da folha; a importação alimenta apenas o turno atual. |
| Alguns componentes herdam o conteúdo do registo anterior ao abrir a janela; outros abrem em branco, por vezes na mesma janela. | Herança configurada por componente; componentes herdáveis exibidos com aviso. |
| O campo «Registo» mostra quem gravou, mesmo que o conteúdo seja herdado de outro profissional. | Metadado exibido como «registado por»; nunca como autoria. |
| A data/hora é preenchida ao abrir a janela e pode ser alterada. Nas intervenções com horário definido, vem preenchida com a hora programada. | Hora tratada como declarada; não prova o momento da avaliação nem a ordem de gravação. |
| Nas intervenções programadas por turno, a referência temporal visível é o turno. | Referência temporal lida conforme a programação de cada registo. |
| Em P3 e P4 não há nota na janela. Para acrescentar texto (por exemplo, o débito de O2) é preciso abrir a lista de intervenções do turno, encontrar a intervenção e acrescentar uma nota associada. | A ausência de nota pode resultar de fricção da interface; nunca equivale a «sem O2» nem a «débito igual ao anterior». |
| Alguns dados clinicamente relevantes (volumes por sonda, débito de O2, horas de alteração do débito) só existem em texto livre. | Importação do texto tal como está; sem extração automática de valores. |
| A validação da passagem é responsabilidade do enfermeiro transmissor, por doente. | Validação associada a episódio, turno, profissional e versão; a cama é localização, não identificador clínico. |

# 3. Atores, pré-condições e pós-condições

| **Elemento** | **Definição** |
|---|---|
| Ator principal | Enfermeiro responsável pela transmissão do doente. |
| Atores de suporte | Sistema EHR de origem; componente de importação; aplicação de passagem de turno. |
| Pré-condições | Doente e episódio corretamente identificados; intervenções de referência e componentes a importar configurados por domínio; acesso institucional autorizado; período de referência configurado (por defeito, turno atual). |
| Condição de sucesso | Registos elegíveis apresentados por componente, com contexto de origem e aviso de herança quando aplicável; todas as propostas revistas; versão identificada e validada pelo responsável. |
| Condição alternativa | Sem registo, conteúdo não importado por configuração, dados insuficientes ou falha: aviso, preservação do conteúdo anterior e possibilidade de preenchimento manual. |

# 4. Origem da informação e mapeamento

## 4.1 Padrões de origem e componentes

| **Padrão** | **Componente** | **Herança** | **Base** |
|---|---|---|---|
| P1 Frases e texto livre | Frases selecionadas do catálogo de frases standard | Herda | Observado |
| P1 Frases e texto livre | Texto livre (campo de escrita na parte inferior da janela; designação técnica por confirmar) | Herda | Observado |
| P2 Avaliação por itens | Árvore: grupo › item › valor (sim/não ou valores múltiplos) | Herda | Observado |
| P2 Avaliação por itens | Observações (texto livre) | Em branco | Declarado |
| P2 Avaliação por itens | Resumo | Por confirmar | Excluído da importação até se saber se é gerado a partir da árvore ou escrito à mão |
| P3 Parâmetro numérico | Valor com unidade ou escala, limites, data/hora declarada; várias medições por registo | Em branco | Observado |
| P4 Execução | Estado realizada / não realizada | Em branco | Declarado |

P1 e P3 assentam em várias intervenções (ver 4.2). P2 assenta numa só
intervenção (Avaliar pele) e P4 numa só (Gerir oxigenoterapia); a
generalização destes dois padrões a outras intervenções é uma inferência
até haver mais exemplos.

Em todos os padrões, os metadados visíveis são «registado por» e a
referência temporal (ver «Programação» abaixo).

**Componente transversal: nota associada.** Em P3 e P4 não existe campo
de nota na janela. O texto acrescenta-se abrindo a lista de intervenções
do turno, procurando a intervenção e escrevendo uma nota associada. É
texto livre, abre em branco e não tem hora visível. Observado em Gerir
oxigenoterapia; declarado igual em P3. A nota pode conter horas e valores
escritos pelo enfermeiro (exemplo ilustrativo: «12:30h - 3L/min; 15h -
2L/min»). Essas horas são conteúdo, não metadados. Em P1, o texto livre
está na própria janela.

**Atributo do registo: programação.** No plano de cuidados, cada
intervenção é programada para cada doente:

- por turno: a referência temporal visível é o turno;
- horário definido: a hora programada vem pré-preenchida ao abrir a
  janela, pode ser alterada e fica registada a hora que estiver no
  campo. É, portanto, hora declarada. Exemplos: sinais vitais, avaliar
  sono e outras intervenções específicas do motivo de internamento.

A programação é definida por doente no plano de cuidados, não pelo
serviço. A mesma intervenção pode estar por turno num doente e com horário
noutro. A importação lê a programação de cada registo; não a configura por
intervenção.

Em Gerir oxigenoterapia, a hora da execução e a da nota não são visíveis.
Uma eventual hora interna está por confirmar (secção 9).

**Janelas compostas.** Uma janela composta (por exemplo, «Monitorizar
sinais vitais») é interface de entrada: ao gravar, gera intervenções
separadas, visíveis no plano, por valor e por característica. A
configuração aponta para essas intervenções finais, não para a janela. Não
se afirma nada sobre a forma de armazenamento interno.

**Função, não nome do campo.** O mapeamento faz-se pela função do
componente. A correspondência do nome «Observações» em P1 (frases
selecionadas ou texto livre) está por confirmar.

## 4.2 Mapeamento por domínio

A herança de cada componente segue a 4.1; não há exceções nesta matriz. A
coluna «Componentes a importar» é uma proposta de configuração para a
demonstração, não uma decisão institucional.

| **Domínio** | **Intervenção (nome observado)** | **Padrão** | **Componentes a importar (proposta)** | **Base / notas** |
|---|---|---|---|---|
| Eliminação | Vigiar eliminação urinária | P1 | Frases e texto livre | Observado |
| Eliminação | Vigiar eliminação intestinal | P1 | Frases e texto livre | Observado |
| Eliminação | Monitorizar eliminação urinária | P3 | Valores; nota associada | Declarado: janela igual à intestinal. Condicional: usada só com diurese pedida. |
| Eliminação | Monitorizar eliminação intestinal | P3 | Valores; nota associada | Observado |
| Eliminação (domínio por confirmar) | Monitorizar entradas e saídas de líquidos | Por confirmar | Por confirmar | Nome declarado; janela não observada. Usada quando é pedido balanço hídrico. |
| Comportamento | Vigiar comportamento | P1 | Só texto livre | As frases do catálogo não acrescentam informação útil à passagem. |
| Pele | Avaliar pele | P2 | Árvore com filtro (achados positivos e indicação de que existem negativos registados); observações | Resumo excluído até confirmação. |
| Alimentação | Vigiar refeição (inclui alimentação por sonda) | P1 | Frases e texto livre | Observado |
| Alimentação | Vigiar conteúdo gástrico | P1 | Frases e texto livre | Observado |
| Alimentação | Monitorizar conteúdo gástrico | P3 | Valores; nota associada | Observado |
| Hemodinâmica | Monitorizar FC, FR, temperatura, TA, SpO2 e dor (geradas a partir de «Monitorizar sinais vitais») | P3 | Valores; nota associada | Observado |
| Hemodinâmica | Avaliar respiração (gerada) | P1 | Frases e texto livre | Observado |
| Hemodinâmica | Características do pulso e da dor (geradas) | P1 | Frases e texto livre | Nomes por confirmar. |
| Hemodinâmica | Gerir oxigenoterapia | P4 | Estado; nota associada | Declarado. |

**Campos sem origem no EHR**

| **Domínio** | **Campo** | **Origem** | **Tratamento** |
|---|---|---|---|
| Hemodinâmica | Último antipirético e hora | Fonte externa (plataforma de medicação) | Preenchimento manual, identificado como fonte externa não integrada. |

As intervenções desta matriz são as que identifiquei a partir da minha
prática e não esgotam as possíveis: conforme os problemas do doente,
outras podem fazer sentido. A seleção final tem de resultar de uma
avaliação feita com a equipa do serviço. Nomes, identificadores técnicos,
CIPE, metadados e disponibilidade por interface teriam de ser confirmados
num levantamento autorizado.

# 5. Fluxo principal

1.  O enfermeiro realiza os registos de enfermagem no sistema clínico, nas
    intervenções de referência.

2.  Na preparação da passagem de turno, habitualmente no fim do turno,
    seleciona o doente/episódio e usa «Atualizar a partir do EHR». A ação
    pode ser repetida.

3.  O sistema procura registos elegíveis das intervenções configuradas
    para cada domínio, no contexto do episódio e do período de referência
    (por defeito, turno atual).

4.  O sistema apresenta, por domínio e por intervenção, cada componente
    configurado em separado (frases, texto livre, itens de avaliação,
    valores numéricos com unidade, execução, nota associada), com
    «registado por» e referência temporal, e assinala os componentes
    herdáveis. O conteúdo já existente na folha contínua mantém-se.

5.  O enfermeiro revê as propostas (aceitar, editar ou retirar). Pode usar
    «aceitar tudo», que aceita de uma vez só as propostas sem avisos; as
    que têm aviso revê-as uma a uma. Resolve as decisões pendentes,
    verifica a atualidade, a pertinência e a consistência clínica, e
    preenche à mão os campos de fonte externa.

6.  Quando não restam propostas por rever nem decisões pendentes, o
    enfermeiro valida a versão do doente/episódio para o turno.

7.  A versão validada integra a preparação global da passagem, com o
    estado de validação de cada doente.

# 6. Regras de negócio

## 6.1 Core (comum a todos os domínios)

| **ID** | **Regra** |
|---|---|
| C-01 | A transferência depende de ação explícita do enfermeiro. |
| C-02 | A origem tem de corresponder ao doente e episódio selecionados; uma discrepância impede a importação. A cama não identifica o episódio. |
| C-03 | A informação importada é provisória, precisa de revisão humana, e a sua edição não altera o registo original. |
| C-04 | Cada componente é importado em separado e com origem identificada. Não há fusão de narrativas nem geração de texto a partir de opções. |
| C-05 | Metadados exibidos como «registado por» e referência temporal conforme a programação do registo: turno, ou hora declarada (editável na origem; nas intervenções com horário definido, pré-preenchida com a hora programada). Nunca se atribui autoria do conteúdo. A importação preserva, quando disponíveis, ID do registo, intervenção, episódio e referência temporal. |
| C-06 | A herança é configurada por componente. Componentes herdáveis são exibidos com o aviso «pode conter conteúdo de registo anterior», incluindo frases de normalidade e valores da árvore de avaliação. |
| C-07 | Quatro estados distintos: valor/achado; negativo registado explicitamente; registo existente sem componentes configurados para importar; sem registo. Ausência nunca equivale a «normal» nem a «não». O aviso «sem informação importada» aplica-se ao domínio quando nenhuma intervenção configurada tem registo. |
| C-08 | Só são elegíveis registos do período de referência; registos anteriores nunca são importados. Quando uma intervenção não tem registo no período mas tem registo anterior, assinala-se apenas que este existe, identificado pelo turno (ALT-04). Vários registos ou medições no período: todos apresentados com a referência temporal de cada um, sem seleção automática. |
| C-09 | Valores numéricos acompanham sempre a unidade ou escala. Valores compostos (por exemplo, TA) não se separam. Unidade não disponível na origem é assinalada e nunca presumida. |
| C-10 | Sem cálculos (somas, balanços), sem extração de números ou horas de texto livre, sem interpretação de tendências, sem resolução automática de incoerências e sem presumir que o último valor conhecido se mantém. O tratamento de valores calculados pela própria origem (por exemplo, um balanço mostrado pelo EHR) está por decidir (secção 9). |
| C-11 | Cada valor é lido de um único nível de registo (intervenção final), sem duplicados. |
| C-12 | Dados de outras plataformas não são importados; o campo correspondente fica marcado como manual. Não se afirma integração. |
| C-13 | Os metadados de registo não são usados para avaliar profissionais. |
| C-14 | Uma atualização não substitui em silêncio conteúdo editado ou validado. A validação ocorre por episódio, turno e enfermeiro transmissor; mudanças exigem nova validação. Não se valida enquanto houver propostas por rever ou decisões pendentes; propostas retiradas contam como revistas e não entram na versão validada nem na folha de passagem. «Aceitar tudo» aceita só propostas sem avisos (herança, unidade em falta, «registado por» em falta) e sem decisão pendente; as restantes revêm-se uma a uma. A impressão da folha de passagem não depende da validação (doentes por validar saem marcados). |

As intervenções usadas como fonte têm de ser clinicamente adequadas. Isto
é uma pré-condição de configuração, não uma regra de execução.

## 6.2 Configurável (por serviço e domínio)

| **Eixo** | **Exemplo** |
|---|---|
| Intervenções por domínio | Eliminação: Vigiar eliminação urinária e intestinal, Monitorizar eliminação urinária e intestinal |
| Padrão de cada intervenção | P1, P2, P3 ou P4 |
| Componentes a importar | Vigiar comportamento: só texto livre; Avaliar pele: árvore e observações, sem resumo |
| Tipo de herança por componente | Avaliar pele: árvore herda e observações abrem em branco, na mesma janela |
| Catálogos de frases e itens | Referência para apresentação; não usados para inferência |
| Filtro de apresentação | Pele: mostrar achados positivos e indicar que existem negativos registados |
| Período de referência | Por defeito, turno atual |
| Histórico de consulta | Desligado por defeito. Se ligado, mostra registos de turnos anteriores só para leitura, cada um identificado pelo seu turno; nunca os importa para os campos |
| Campos manuais | Último antipirético e hora |

A programação (por turno ou horário definido) não é eixo configurável: é
definida no plano de cuidados de cada doente e lida em cada registo.

Critério de desenho: acrescentar uma intervenção a um domínio deve ser
apenas configuração, sem alterar nenhuma regra Core.

# 7. Cenários alternativos

| **ID** | **Situação** | **Resposta pretendida** |
|---|---|---|
| ALT-01 | Nenhuma intervenção configurada do domínio tem registo elegível | Avisar ao nível do domínio; não assumir normalidade; permitir preenchimento manual. Intervenções condicionais sem registo não geram aviso individual (por exemplo, Monitorizar eliminação urinária, usada só com diurese pedida). |
| ALT-02 | Múltiplos registos ou medições | Apresentar todos com a referência temporal de cada um; pedir seleção apenas quando o utilizador quiser reduzir; nunca escolher automaticamente. |
| ALT-03 | Conteúdo herdado de execução anterior | Exibir como proposta com aviso de herança; não declarar que foi reavaliado. |
| ALT-04 | Apenas registo anterior ao período de referência | Não importar. Avisar que existe registo anterior ao período, identificado pelo turno. O conteúdo já existente na folha contínua mantém-se. Se o histórico de consulta estiver ligado, o registo pode ser lido nessa vista. |
| ALT-05 | Alteração no EHR depois da importação | Na atualização seguinte, mostrar diferenças e preservar o conteúdo da folha até decisão. |
| ALT-06 | Edição manual prévia na folha | Pedir decisão antes de substituir ou acrescentar; exigir nova validação se houver alteração. |
| ALT-07 | Falha de acesso ou integração | Indicar a falha, não eliminar texto existente, permitir preparação manual. |
| ALT-08 | Mudança de cama ou novo episódio na mesma cama | Manter a associação pelo episódio e impedir a reutilização de validação de outro episódio. |
| ALT-09 | Registo com valor numérico novo e características herdáveis | Apresentar valores e características em separado; aviso de herança apenas nas características. |
| ALT-10 | Execução registada sem nota associada (por exemplo, oxigenoterapia sem débito) | Mostrar «realizada, sem nota». Não mostrar notas nem valores de turnos anteriores; não transportar valores. |
| ALT-11 | Informação relevante existente noutra plataforma | Campo manual identificado como fonte externa não integrada. |
| ALT-12 | Registo existente sem componentes configurados para importar (por exemplo, Vigiar comportamento só com frases selecionadas) | Avisar «existe registo na origem; conteúdo não importado por configuração». Não equivale a «sem informação importada». |

# 8. Critérios de aceitação

| **ID** | **Critério verificável** |
|---|---|
| AC-01 | Dado episódio correto e registo elegível, quando se atualiza, então o conteúdo é apresentado como provisório. |
| AC-02 | Dadas várias intervenções num domínio, quando se atualiza, então os conteúdos aparecem separados por intervenção e componente. |
| AC-03 | Dado campo editado, quando ocorre nova importação, então nenhuma substituição é silenciosa. |
| AC-04 | Dado só existir registo anterior ao período de referência, quando se atualiza, então o registo não é importado e surge aviso de que existe registo anterior, identificado pelo turno. |
| AC-05 | Dada ausência de registo no domínio, quando se atualiza, então surge «sem informação importada», nunca «normal» por defeito. |
| AC-06 | Dada incompatibilidade de episódio, quando se tenta importar, então a transferência é impedida. |
| AC-07 | Dada falha de integração, quando se atualiza, então o conteúdo existente permanece e a via manual continua acessível. |
| AC-08 | Dado conteúdo revisto, quando o responsável valida, então versão, episódio, turno e profissional ficam associados. |
| AC-09 | Dada uma versão validada, quando o conteúdo muda, então volta ao estado por validar. |
| AC-10 | Dado um episódio novo na mesma cama, quando se prepara a passagem, então não é herdada validação do episódio anterior. |
| AC-11 | Dada informação importada, quando se consulta a origem, então os metadados disponíveis aparecem como «registado por» e referência temporal (turno ou hora declarada); a ausência de metadados é assinalada. |
| AC-12 | Dado um componente herdável, quando é importado, então é exibido com aviso de herança. |
| AC-13 | Dado um item de avaliação sem registo, quando é importado, então nunca é apresentado como «não». |
| AC-14 | Dadas várias medições de um parâmetro, quando são importadas, então surge a série com a referência temporal e a unidade/escala de cada valor. |
| AC-15 | Dado um valor registado através de janela composta, quando é importado, então aparece uma única vez. |
| AC-16 | Dado um campo de fonte externa, quando se prepara a folha, então está identificado como manual e não integrado. |
| AC-17 | Dada uma execução sem nota, quando é importada, então não é apresentado nenhum valor presumido a partir de registos anteriores. |
| AC-18 | Dada a folha aberta sem ação do enfermeiro, então nenhum conteúdo é importado. |
| AC-19 | Dado conteúdo importado e editado na folha, então o registo de origem mantém-se inalterado. |
| AC-20 | Dado registo existente apenas com componentes excluídos por configuração, quando se atualiza, então surge o aviso do ALT-12 e não «sem informação importada». |
| AC-21 | Dado valor numérico sem unidade na origem, quando é importado, então a falta de unidade é assinalada e nenhuma unidade é presumida. |
| AC-22 | Dado texto livre com horas e valores (exemplo ilustrativo: «12:30h - 3L/min; 15h - 2L/min»), quando é importado, então aparece só como texto e nenhum valor ou hora é apresentado como campo estruturado. |
| AC-23 | Dadas propostas por rever ou decisões pendentes, quando se tenta validar, então a validação é recusada com indicação do que falta rever; resolvidas, a validação é aceite. |
| AC-24 | Dada uma proposta retirada, quando se valida e se gera a folha de passagem, então a proposta conta como revista e não aparece na versão validada nem na folha. |
| AC-25 | Dadas propostas com e sem aviso, quando se usa «aceitar tudo», então só as propostas sem aviso ficam aceites; as que têm aviso continuam por rever e a validação continua recusada até serem revistas. |

**Rastreabilidade regra → critério**

| **Regra** | **Critérios** |
|---|---|
| C-01 | AC-18 |
| C-02 | AC-06, AC-10 |
| C-03 | AC-01, AC-19 |
| C-04 | AC-02 |
| C-05 | AC-11 |
| C-06 | AC-12 |
| C-07 | AC-05, AC-13, AC-20 |
| C-08 | AC-04, AC-14 |
| C-09 | AC-14, AC-21 |
| C-10 | AC-17, AC-22 |
| C-11 | AC-15 |
| C-12 | AC-16 |
| C-13 | Não testável na aplicação; verificação por governação institucional. |
| C-14 | AC-03, AC-08, AC-09, AC-23, AC-24, AC-25 |

**Estado dos testes:** os critérios AC-01 a AC-25 estão implementados
como testes automáticos na demonstração com dados sintéticos e passam
todos. Isto confirma que o código da demonstração cumpre os critérios
escritos. Não é validação clínica, teste em contexto real nem prova de
ganho de tempo. Numa implementação real, a aceitação dependeria de revisão
clínica, segurança e autorização institucional.

# 9. Questões abertas e dependências

| **Prioridade** | **Questão** | **Forma de resolução** |
|---|---|---|
| Alta | Identificadores e datas efetivamente disponibilizados pelo EHR | Análise de interface ou documentação autorizada. |
| Alta | Existência de hora de gravação separada da hora declarada, incluindo hora interna das execuções P4 e das notas associadas | Análise de interface autorizada. |
| Alta | Existência de marca que distinga conteúdo herdado de conteúdo alterado (por componente e por item) | Validação com a equipa técnica. |
| Alta | Monitorizar entradas e saídas de líquidos: padrão, componentes, domínio, e se a janela mostra um balanço calculado na origem (decide a aplicação da C-10) | Observação da janela; depois, levantamento autorizado. |
| Alta | Exatidão e adequação clínica das intervenções de referência | Inventário no serviço e validação por enfermeiros responsáveis. |
| Alta | Gestão de alterações, autenticação e trilho de auditoria | Requisitos de segurança e governação institucional. |
| Média | Unidades de Monitorizar eliminação urinária, eliminação intestinal e conteúdo gástrico; significado de L. Inf. e L. Sup. | Levantamento autorizado. |
| Média | Resumo de Avaliar pele: gerado a partir da árvore ou escrito à mão | Observação da janela. |
| Média | Designação técnica do campo de texto livre em P1 e correspondência de «Observações» | Observação da janela. |
| Média | Significado das marcas de item em Avaliar pele (parênteses retos, asterisco) | Levantamento autorizado. |
| Média | Nomes das intervenções geradas a partir de «Monitorizar sinais vitais» e das características do pulso e da dor | Confirmação no serviço. |
| Média | Tempo e esforço acrescido ou poupado, incluindo o da revisão obrigatória antes de validar | Medição antes e depois; não assumir melhoria. |
| Média | Adaptação a internamento de adultos | Análise de práticas e intervenções desse contexto; não generalizar o padrão de herança observado. |

# 10. Delimitação e riscos residuais

Este caso de uso é uma prova funcional. Não propõe leitura não autorizada
do SClínico, modificação dos registos do EHR, integração com outras
plataformas, interpretação automática de CIPE, cálculo ou interpretação
clínica automática, geração de juízos clínicos nem implantação em
produção. Não elimina o julgamento do enfermeiro. Os limites da origem
(por exemplo, volumes e débitos apenas em texto livre) não são corrigidos
pela importação.

Risco residual: numa folha contínua, conteúdo escrito em turnos anteriores
pode ficar sem ser revisto e parecer atual. Indicar em cada campo o turno
da última alteração resolveria parte do problema, mas carregaria demasiado
a folha, e por isso não foi adotado. O risco fica mitigado apenas pela
revisão e validação humanas em cada turno (C-14). A revisão obrigatória
antes de validar e o «aceitar tudo» parcial aplicam-se às propostas
importadas, não ao conteúdo que já está na folha. O desenho não resolve
este risco.

# 11. Decisões de desenho

| **Decisão** | **Estado** |
|---|---|
| Atualização sempre por ação do enfermeiro | Decidido |
| Validação por episódio, turno e enfermeiro transmissor | Decidido |
| Uma ou várias intervenções de referência por domínio | Decidido |
| Quatro padrões de origem; a configuração aponta para intervenções finais | Decidido |
| Herança «herda» / «em branco» por componente, com aviso | Decidido |
| Nota associada como componente transversal; programação lida por registo | Decidido |
| Metadados como «registado por» e referência temporal (turno ou hora declarada) | Decidido |
| Sem cálculos, extração de texto, interpretação de tendências ou valores presumidos | Decidido |
| Período de referência = turno atual; continuidade pela folha contínua | Decidido |
| Registo anterior ao período: avisar só quando não há registo no período, nunca importar | Decidido |
| Vários registos: mostrar todos, sem seleção automática | Decidido |
| Vigiar comportamento: importar só texto livre | Decidido |
| Não validar com propostas por rever; retirar uma proposta conta como revisão | Decidido |
| «Aceitar tudo» aceita só propostas sem avisos | Decidido |
| Indicação do turno da última alteração em cada campo | Rejeitado (carrega demasiado a folha); fica como risco residual |
| Tratamento de valores calculados pela origem (balanço) | Aberto |
| Integração e acesso técnico ao SClínico | Não verificados; fora do âmbito |
