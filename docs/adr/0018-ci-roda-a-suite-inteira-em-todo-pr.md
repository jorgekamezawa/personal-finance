---
status: aceito
atualizado: 2026-09-24
---
# ADR-0018: O CI roda a suíte inteira em todo PR

**Decisão:** todo PR roda **a suíte inteira** (backend, frontend e verificação dos documentos), sem filtrar por pasta alterada, porque enquanto a execução leva poucos minutos o filtro economiza pouco e traz de volta um problema conhecido de verificação obrigatória.

## Contexto
Decorre do [ADR-0001](0001-repositorio-unico-sem-ferramenta-de-monorepo.md), que deixou em aberto como um repositório com dois artefatos organiza o CI. Hoje a suíte é pequena: teste de regra roda em milissegundos ([ADR-0013](0013-teste-de-regra-roda-sem-infraestrutura.md)) e o teste de banco sobe um contêiner uma vez ([ADR-0014](0014-teste-de-banco-contra-postgres-real.md)).

## Alternativas descartadas
- **Filtrar pelo gatilho do fluxo, rodando só o que mudou:** é o caminho direto, e tem uma armadilha documentada: quando o fluxo é pulado por filtro, a verificação obrigatória dele fica **pendente para sempre**, e o PR não pode ser mergeado.
- **Filtrar dentro do fluxo, com um job agregador como verificação obrigatória:** resolve a armadilha, porque o agregador sempre roda. Acrescenta um job que existe só para satisfazer a regra de proteção e uma etapa de detecção do que mudou, para economizar poucos minutos numa suíte que ainda é curta.

## Consequências
- **Ganhos:** nenhum PR passa sem que backend e frontend tenham sido testados; a configuração do CI cabe numa leitura; some a classe de problema da verificação pendente.
- **Custos:** mudança só de documentação também roda a suíte inteira, gastando minutos de máquina.
- **Passa a ser obrigatório:** medir o tempo da suíte de vez em quando; quando ela passar de alguns minutos no PR, esta decisão é revista.
