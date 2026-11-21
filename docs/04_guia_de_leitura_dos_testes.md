# Guia de leitura dos testes

O que cada teste verifica, sem código. Dados sintéticos.

| Teste | Situação | O que se espera | Regra |
|---|---|---|---|
| AC-01 | O enfermeiro importa os registos do turno | Aparecem como propostas, por rever | C-03 |
| AC-02 | Eliminação com três intervenções | Cada intervenção e cada componente em separado; nada é fundido | C-04 |
| AC-03 | O enfermeiro editou um texto e depois a origem mudou | Fica o texto editado; o novo aparece como decisão pendente | C-14 |
| AC-04 | A refeição só foi registada de manhã | Não é importada; aviso de que existe registo do turno da manhã | C-08 |
| AC-05 | Criança sem registos | «Sem informação importada» em todos os domínios, nunca «normal» | C-07 |
| AC-06 | A origem devolve registos de outra criança | Importação bloqueada; nada entra | C-02 |
| AC-07 | A origem está em baixo | O que já estava na folha fica; o preenchimento manual continua | ALT-07 |
| AC-08 | O enfermeiro valida | Ficam registados versão, episódio, turno e enfermeiro | C-14 |
| AC-09 | Alguém altera depois de validar | Volta a «por validar» | C-14 |
| AC-10 | Alta e nova criança na mesma cama | A nova criança não herda validação nem conteúdo | C-02 |
| AC-11 | Ver a origem de uma proposta | «Registado por» e turno ou hora declarada; se faltar, diz que falta | C-05 |
| AC-12 | Avaliar respiração (frases) | Aviso «pode conter conteúdo de registo anterior»; a FC não tem esse aviso | C-06 |
| AC-13 | Pele: edema sem registo | Aparece «sem registo», nunca «não» | C-07 |
| AC-14 | FC medida às 16h e às 20h | As duas, cada uma com hora e unidade; a TA 98/60 não é partida | C-08, C-09 |
| AC-15 | FC gravada pela janela de sinais vitais | Aparece uma só vez | C-11 |
| AC-16 | Último antipirético | Campo manual, marcado como fonte externa não integrada | C-12 |
| AC-17 | O2 feito sem nota; de manhã a nota dizia 3L/min | «Realizada, sem nota»; o 3L/min não aparece | C-10 |
| AC-18 | Abrir a folha da criança | Nada é importado até o enfermeiro pedir | C-01 |
| AC-19 | Editar na folha | O registo de origem fica igual | C-03 |
| AC-20 | Comportamento só com frases, que estão excluídas | Aviso «existe registo, não importado por configuração», e não «sem informação» | C-07 |
| AC-21 | Dejeções sem unidade na origem | «Unidade não disponível» e aviso; não se inventa unidade | C-09 |
| AC-22 | Texto livre «16h - 20 ml; 20h - 15 ml» | Fica como texto; não vira medições | C-10 |
| AC-23 | Validar sem rever as propostas | Recusado: «faltam rever 12 propostas»; depois de resolver tudo, aceite | C-14 |
| AC-24 | Retirar uma proposta | Conta como revista; não sai na folha nem na versão validada | C-14 |
| AC-25 | Carregar em «aceitar tudo» | Aceita só as propostas sem aviso (5); as 7 com aviso (herança, unidade em falta) ficam por abrir; a validação continua recusada até as rever | C-14 |
| WF-01 | A criança muda da cama 3 para a 5 | O conteúdo segue a criança; não há nada para copiar | To-Be, passo 7 |
| WF-02 | Imprimir com uma criança por validar | Imprime; essa criança sai «NÃO VALIDADO» | To-Be, passo 5 |
| WF-03 | Diurese não pedida, sem registo | Sem aviso individual | ALT-01 |

**Como sei que os testes não passam por acaso.** Estraguei de propósito
cada regra principal, uma de cada vez. Os testes tinham de falhar, e
falharam. Num caso (a proteção do registo de origem) o teste não deu pelo
erro à primeira e foi reforçado.
