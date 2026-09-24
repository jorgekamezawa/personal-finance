---
status: aceito
atualizado: 2026-09-19
---
# ADR-0001: Usar repositório único sem ferramenta de monorepo

**Decisão:** usar um **repositório único (monorepo) sem ferramenta de monorepo**. Ou seja, cada pasta mantém o build nativo dela (`./gradlew build` no `backend/`, `npm run build` no `frontend/`) e quem decide o que rodar é o filtro de caminho do CI, em vez de uma ferramenta na raiz que monta o grafo de dependências e guarda cache.

## Contexto
Um desenvolvedor, dois artefatos (Java com Gradle, React com Vite) e deploy conjunto. Specs e ADRs precisam viver ao lado do código que descrevem. Não há biblioteca compartilhada entre backend e frontend, nem CI lento para otimizar.

## Alternativas descartadas
- **Repositórios separados:** o custo é coordenar versão e histórico entre dois repositórios, e a spec fica longe de metade do código. O ganho (times em ritmos diferentes, permissões separadas) não existe com um desenvolvedor.
- **Monorepo com Nx ou Turborepo:** resolvem build incremental, cache compartilhado e dependências entre pacotes. Esse ganho aparece com muitos pacotes interdependentes e build lento; aqui são dois artefatos independentes com build rápido, então sobra configuração e aprendizado sem problema correspondente. Podem ser adotados depois sem mudar a estrutura de pastas.

## Consequências
- **Ganhos:** uma versão para tudo; um só lugar para configurar CI e deploy; documentação junto do código.
- **Custos:** o histórico mistura backend e frontend, e distinguir a origem de cada commit passa a depender de convenção; um mesmo repositório passa a disparar o CI dos dois artefatos, e como isso é organizado fica em aberto.
- **Passa a ser obrigatório:** pastas `backend/`, `frontend/` e `docs/` na raiz.
