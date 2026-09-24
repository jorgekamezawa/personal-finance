---
paths:
  - "backend/**"
---

# Convenções do backend

## Estrutura
- Um pacote por capacidade do negócio, dentro de `com.personalfinance`. Cada módulo tem `api/` (o que o vizinho pode importar), `domain/`, `application/` (com as portas) e `adapter/in`, `adapter/out` ([ADR-0011](../../docs/adr/0011-monolito-modular-com-hexagonal.md)).
- **A porta pertence a quem consome:** o módulo que precisa declara a interface na linguagem dele, e o adaptador de saída traduz e chama a `api/` do vizinho.
- Nenhum módulo usa repositório, entidade de banco ou tabela de outro.
- Reação a fato consumado usa evento de domínio; quem publica não conhece quem escuta.
- `shared/tipo` guarda só tipo de valor usado por dois ou mais módulos e sem dono natural. Regra de negócio nunca sobe para lá.

## Domínio
- Classe de domínio não tem anotação de framework, e isso é verificado por teste.
- Dinheiro é decimal exato; comparar com `compareTo`, nunca `equals`; arredondar só na fronteira em que vira dinheiro, no modo metade para o par ([ADR-0009](../../docs/adr/0009-dinheiro-em-decimal-exato.md)).
- Data da compra é data pura; instante do sistema é UTC com fuso.

## Banco
- Toda mudança de esquema entra como migração numerada, nunca alteração manual.
- Toda tabela de dado de usuário tem a coluna do grupo, e nenhuma consulta roda sem o filtro dele ([ADR-0012](../../docs/adr/0012-multi-tenant-por-coluna-de-grupo.md)).
- Identificador de registro é UUID versão 7.

## Testes
- Teste de domínio e de caso de uso roda sem Spring, sem banco e sem rede ([ADR-0013](../../docs/adr/0013-teste-de-regra-roda-sem-infraestrutura.md)).
- Dependência externa nesses testes entra como implementação falsa em memória, escrita no projeto, em vez de biblioteca de simulação: o teste verifica comportamento, não chamada.
- Teste que toca banco usa Postgres real em contêiner, na mesma versão de produção ([ADR-0014](../../docs/adr/0014-teste-de-banco-contra-postgres-real.md)).

## Configuração
- Toda configuração vem de variável de ambiente; nenhum endereço ou senha no código ([ADR-0020](../../docs/adr/0020-segredos-fora-do-ambiente-e-configuracao-por-variavel.md)).
- Endpoint de estado fica sob `/api`, como o resto da API.
