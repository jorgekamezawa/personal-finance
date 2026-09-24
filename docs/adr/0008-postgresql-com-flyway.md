---
status: aceito
atualizado: 2026-09-20
---
# ADR-0008: Usar PostgreSQL com Flyway

**Decisão:** usar **PostgreSQL** como banco principal e **Flyway** para versionar o esquema, porque os dados do produto são relacionais, o relatório mensal é a função central, e os dois pontos sensíveis (dinheiro exato e data com fuso) têm tratamento nativo aqui.

## Contexto
Um serviço Java ([ADR-0003](0003-spring-boot-como-framework-do-backend.md)) num servidor com 4 GB, poucos usuários. Os dados se ligam entre si: lançamento pertence a categoria, meio de pagamento e membro; parcela pertence a uma compra; o resumo do mês soma tudo isso. O esquema vai mudar a cada feature.

O que pesa na escolha, nesta ordem:
1. dinheiro exato;
2. data com fuso e fronteira de mês;
3. transação confiável;
4. migração segura;
5. consulta de relatório simples;
6. pouco esforço de operação.

## Alternativas descartadas
- **MySQL ou MariaDB.** Empata no dinheiro: o tipo decimal também é exato. Perde em três pontos concretos:
  - **Migração:** comando que altera estrutura (criar tabela, alterar coluna) confirma a transação sozinho e não pode ser desfeito, então uma migração que falha no meio deixa o banco pela metade. No Postgres, alteração de estrutura roda dentro de transação e volta inteira se falhar, que é exatamente o que o Flyway precisa.
  - **Fuso:** o tipo com data e hora sem fuso é o caminho comum, o tipo com fuso vale só de 1970 a 2038, e usar nome de fuso ("America/Sao_Paulo") exige carregar tabelas extras no servidor. O Postgres guarda o instante em UTC e converte na leitura, com os nomes de fuso já disponíveis.
  - **Integridade por configuração:** a recusa de valor inválido depende do modo estrito, que é padrão, mas é um interruptor que pode ser desligado; e alguns cortes de texto continuam silenciosos. No Postgres, tipo errado é sempre erro.
- **MongoDB.** O ganho dele é esquema flexível, útil para guardar o extrato importado como veio. Esse ganho o Postgres também entrega, com coluna JSON, sem abrir mão do resto. E perde no que importa aqui:
  - **Transação:** transação que envolve mais de um documento exige réplica configurada; instância única não faz transação. Num servidor só, ou se monta um arranjo de réplica artificial, ou se abre mão de gravar compra e parcelas de forma atômica. A própria documentação avisa que transação distribuída custa mais e não substitui modelagem.
  - **Relatório:** somar gastos por categoria e por mês é uma consulta de uma linha em SQL, contra uma montagem de estágios de agregação.
  - **Dinheiro:** existe tipo decimal exato, mas o caminho natural do driver e dos objetos é ponto flutuante, e é nesse caminho que centavos se perdem.
- **SQLite.** Zero operação e backup por cópia de arquivo são reais. Em troca:
  - **Dinheiro:** não existe tipo decimal; número vira ponto flutuante ou texto, e a exatidão passa a depender de convenção do código.
  - **Concorrência:** um escritor por vez. Funciona para uma pessoa e começa a travar quando a segunda pessoa do grupo entra, que é o próximo passo do produto.
  - **Saída cara:** trocar de banco depois é migrar dados reais, a migração mais arriscada que existe.
- **Liquibase no lugar do Flyway**, para a parte de migração: descreve a mudança em XML ou YAML e traduz para cada banco. Isso compensa quando o mesmo produto roda em bancos diferentes, o que não é o caso; aqui, arquivo SQL numerado é mais legível e mais fácil de revisar em PR.

## Consequências
- **Ganhos:** dinheiro exato, fuso resolvido pelo banco, transação para operações compostas, migração que volta atrás quando falha e relatório em SQL simples.
- **Custos:** 200 a 300 MB de memória no servidor, dividido com a aplicação; backup e atualização do banco viram tarefa de operação, com runbook próprio.
- **Passa a ser obrigatório:** toda mudança de esquema entra como arquivo de migração numerado, nunca alteração manual no banco. Como dinheiro e datas são representados, e onde o extrato bruto importado é guardado, são decisões próprias e ficam em aberto.
