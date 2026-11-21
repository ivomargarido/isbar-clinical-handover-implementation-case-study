# Resultados dos testes de aceitação

Execução: 2026-11-21 00:35. DADOS SINTÉTICOS.

| Critério | Resultado |
|---|---|
| AC-01: Dado episódio correto e registo elegível, ao atualizar o conteúdo é provisório. | PASSOU |
| AC-02: Várias intervenções num domínio aparecem separadas por intervenção e componente. | PASSOU |
| AC-03: Dado campo editado, uma nova importação não o substitui em silêncio. | PASSOU |
| AC-04: Só existe registo anterior ao período: não é importado e surge aviso com o turno. | PASSOU |
| AC-05: Ausência de registo no domínio dá 'sem informação importada', nunca 'normal'. | PASSOU |
| AC-06: Dada incompatibilidade de episódio, a transferência é impedida. | PASSOU |
| AC-07: Dada falha de integração, o conteúdo existente permanece e a via manual continua acessível. | PASSOU |
| AC-08: Ao validar, ficam associados versão, episódio, turno e profissional. | PASSOU |
| AC-09: Dada uma versão validada, quando o conteúdo muda, volta ao estado por validar. | PASSOU |
| AC-10: Episódio novo na mesma cama não herda validação do episódio anterior. | PASSOU |
| AC-11: Metadados exibidos como 'registado por' e referência temporal; ausência assinalada. | PASSOU |
| AC-12: Componente herdável é exibido com aviso de herança. | PASSOU |
| AC-13: Item de avaliação sem registo nunca é apresentado como 'não'. | PASSOU |
| AC-14: Várias medições de um parâmetro aparecem em série, cada uma com hora e unidade. | PASSOU |
| AC-15: Valor registado através de janela composta aparece uma única vez. | PASSOU |
| AC-16: Campo de fonte externa está identificado como manual e não integrado. | PASSOU |
| AC-17: Execução sem nota não mostra nenhum valor presumido de registos anteriores. | PASSOU |
| AC-18: Dada a folha aberta sem ação do enfermeiro, nenhum conteúdo é importado. | PASSOU |
| AC-19: Conteúdo importado e editado na folha deixa a origem inalterada. | PASSOU |
| AC-20: Registo só com componentes excluídos dá o aviso do ALT-12, não 'sem informação importada'. | PASSOU |
| AC-21: Valor sem unidade na origem: a falta é assinalada e nenhuma unidade é presumida. | PASSOU |
| AC-22: Texto livre com horas e valores aparece só como texto; nada vira campo estruturado. | PASSOU |
| AC-23: Não se valida com propostas por rever ou decisões pendentes; resolvidas, a validação é aceite. | PASSOU |
| AC-24: Proposta retirada conta como revista, mas não entra na folha nem na versão validada. | PASSOU |
| AC-25: «Aceitar tudo» aceita só propostas sem avisos; as que têm aviso ficam por rever. | PASSOU |
| WF-01: Mudança de cama: o conteúdo segue o episódio, sem cópia (To-Be, passo 7). | PASSOU |
| WF-02: A saída de passagem nunca é bloqueada; doente por validar sai como NÃO VALIDADO. | PASSOU |
| WF-03: Intervenção condicional sem registo não gera aviso individual (ALT-01). | PASSOU |

Total: 28 de 28 passaram.
