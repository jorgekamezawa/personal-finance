---
status: aceito
atualizado: 2026-09-20
---
# ADR-0010: Gravar o mês de referência no lançamento

**Decisão:** o **mês de referência** (o mês em que o gasto conta) é calculado na gravação, pela regra do meio de pagamento, e **guardado no lançamento**. A leitura só lê; nada é recalculado ao montar relatório.

## Contexto
Decorre do [ADR-0008](0008-postgresql-com-flyway.md). O mês em que um gasto conta depende do meio de pagamento, e cada meio tem a sua regra, detalhada na spec da feature correspondente. O que importa aqui é que essas regras mudam com o tempo, quando o usuário troca de cartão ou corrige o dia de fechamento.

## Alternativas descartadas
- **Calcular na leitura, a partir da regra atual do cartão:** ficaria sempre coerente com a configuração do momento. O problema é que corrigir um dia de fechamento reescreveria o passado em silêncio: relatórios já conferidos mudariam sozinhos, e o total de um mês fechado deixaria de ser confiável.
- **Guardar o instante completo da compra e derivar a data:** preservaria a hora para quando a importação de extrato trouxer esse dado. Obriga a escolher um fuso para converter o instante em dia toda vez que o mês é calculado, e um erro nessa conversão joga a compra para o mês errado; a data pura não tem essa armadilha.
- **Guardar os dois, o mês calculado e o mês corrigido à mão:** parece prudente e dobra a chance de divergência, porque passa a existir duas verdades para a mesma pergunta. Correção à mão é feita no próprio campo gravado.

## Consequências
- **Ganhos:** histórico estável; relatório é leitura simples, sem recalcular regra; correção manual do usuário vale sobre a regra automática.
- **Custos:** mudar a regra de um cartão não corrige o passado sozinho; recalcular lançamentos antigos é ação explícita, com aviso de quantos lançamentos mudam.
- **Passa a ser obrigatório:**
  - as regras de cada meio de pagamento vivem na spec da feature; este ADR decide só quando o valor é calculado e onde ele fica guardado;
  - data da compra é data pura, sem hora; quando a importação de extrato trouxer hora, ela entra como coluna opcional, sem mexer na data da compra;
  - carimbos do sistema (criação, alteração) são instantes em UTC, em coluna com fuso;
  - existe um fuso de referência que define quando o dia vira; de quem é esse fuso e qual é o padrão são regra de negócio, e vivem na spec;
  - a API entrega data como `2026-09-20` e mês de referência como `2026-10`; `20/09/2026` e "Outubro" só existem na tela.
