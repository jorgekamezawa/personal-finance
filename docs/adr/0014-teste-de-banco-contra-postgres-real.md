---
status: aceito
atualizado: 2026-09-23
---
# ADR-0014: Teste de banco roda contra Postgres real em contêiner

**Decisão:** todo teste que toca o banco roda contra **Postgres real, em contêiner descartável criado pelo próprio teste**, na mesma versão de produção e com as migrações aplicadas antes, porque só assim o teste prova o que o banco de verdade aceita.

## Contexto
Decorre do [ADR-0008](0008-postgresql-com-flyway.md). O que precisa ser provado contra banco é mapeamento, migração e consulta de relatório, e é aí que moram os erros de tipo, de fuso e de arredondamento que o produto não pode ter.

## Alternativas descartadas
- **Banco em memória (H2) em modo de compatibilidade:** sobe em milissegundos e dispensa Docker. Cobre parte do SQL e falha justamente em coluna JSON, coluna calculada e funções de janela, que o relatório vai usar; pior, aceita instrução que o Postgres recusa, então o teste passa e produção quebra.
- **Banco compartilhado de desenvolvimento, sempre ligado:** dispensa subir contêiner a cada execução. Os testes passam a depender do estado deixado pela execução anterior, falham de forma intermitente e travam quando duas pessoas (ou o CI) rodam ao mesmo tempo.

## Consequências
- **Ganhos:** erro de mapeamento, migração e tipo aparece na máquina de quem escreveu; a migração é exercitada a cada execução, então o caminho de subida em produção já vem testado.
- **Custos:** Docker passa a ser pré-requisito na máquina e no CI; a primeira classe de teste de banco leva alguns segundos para o contêiner subir.
- **Passa a ser obrigatório:** a versão do Postgres no teste é a mesma de produção, fixada num lugar só; cada execução começa de um banco limpo, com as migrações aplicadas; nenhum teste depende de dado deixado por outro.
