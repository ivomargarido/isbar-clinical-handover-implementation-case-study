"""
Demonstração: importação controlada de registos para a folha de passagem de turno.

DADOS SINTÉTICOS. Esta demonstração não liga a nenhum sistema hospitalar
real e não usa dados de doentes. Simula, em código, os componentes 1 a 7
da arquitetura conceptual (docs/02, secção 4.1).

Módulos:
    leitor_origem      -> componentes 1 e 2 (origem sintética e leitor)
    configuracao       -> componente 3 (configuração por serviço e domínio)
    motor_importacao   -> componente 4 (regras Core, gera propostas)
    aplicacao_isbar    -> componentes 5 e 6 (folha, versões e validação)
    saida_passagem     -> componente 7 (folha de passagem)
"""
