---
status: aceito
atualizado: 2026-09-23
---
# ADR-0012: Multi-tenant compartilhado, com coluna de grupo em toda tabela

**Decisão:** o sistema nasce **multi-tenant** (vários grupos atendidos pela mesma instalação) no grau **compartilhado**: um banco, um esquema, e **cada tabela com a coluna do grupo**, aplicada por filtro automático no mapeamento, porque custa quase nada hoje e não fecha a porta para um grau mais isolado depois. Um único ponto resolve de qual grupo é a requisição.

## Contexto
O produto é para qualquer pessoa, sozinha ou dividindo as finanças com outras ([visão do produto](../product/vision.md)), então dois grupos diferentes nunca podem ver os dados um do outro. No primeiro corte não há login: o acesso é privado, por rede fechada, e existe um grupo só. Todo grau de isolamento discutido aqui é uma forma de multi-tenant; o que muda é onde a separação acontece.

## Alternativas descartadas
- **Multi-tenant por esquema, um esquema de banco por grupo:** isolamento mais forte, e backup ou exportação de um grupo fica trivial. Em troca, cada migração roda em todos os esquemas e criar grupo vira tarefa de infraestrutura, peso que não se paga com um grupo em uso.
- **Multi-tenant por banco, um banco por grupo:** isolamento máximo, e inviável no servidor de 4 GB e no custo previsto.
- **Não ter grupo agora e acrescentar depois:** economizaria alguns dias no começo. Depois exigiria migrar dados reais, encontrar todas as consultas e reescrevê-las, que é ordens de grandeza mais caro.
- **Identificador de registro em número sequencial, ou em UUID aleatório:** o número sequencial ocupa menos espaço no índice e é mais rápido de escrever; o UUID aleatório não colide, mas espalha a escrita no índice. O número sequencial colide ao mover um grupo para outro banco e expõe quantos lançamentos existem; por isso fica o UUID ordenado, que não colide e mantém a escrita em sequência.
- **Segurança em nível de linha do Postgres desde já** (o banco recusa linha de outro grupo, mesmo com erro no código): é a rede de proteção mais forte. Complica migração e teste agora, então fica ligada ao lançamento público, quando existir login e mais de um grupo de verdade.

## Consequências
- **Ganhos:** custo quase zero hoje; o código nunca supõe "um grupo só"; quando o login entrar, muda apenas de onde vem o identificador do grupo.
- **Custos:** o isolamento é lógico, então um erro de mapeamento pode vazar dado entre grupos; a rede de proteção no banco fica para depois.
- **Passa a ser obrigatório:**
  - toda tabela de dados do usuário tem a coluna do grupo, inclusive as de apoio: tabela sem ela é o que trava a migração para outro grau;
  - um único ponto resolve o grupo da requisição, hoje devolvendo o grupo único e amanhã o da sessão; nenhum caso de uso descobre isso por outro caminho;
  - identificador de registro é UUID ordenado (versão 7), para mover um grupo de banco sem colisão e para não expor contagem na API;
  - nenhuma chave estrangeira cruza grupos, e nenhuma consulta roda sem o filtro do grupo;
  - mudar de grau depois (esquema ou banco por grupo) troca o resolvedor e migra os dados daquele grupo, sem mexer em regra de negócio.
