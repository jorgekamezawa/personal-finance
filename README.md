# personal-finance

Aplicação de finanças pessoais para registrar e entender gastos num lugar só, individualmente ou em grupo. Desenvolvida com um fluxo agêntico (agentes de IA implementam, pessoas decidem e revisam) guiado por SDD (Spec-Driven Development: toda feature começa por uma especificação).

## Como rodar localmente
Copie `.env.example` para `.env`, preencha os valores e suba tudo:
```
docker compose up -d --build
```
O app fica em `http://localhost:8081` (a porta vem de `APP_PORT`).

### Rodando backend e frontend fora do Docker
Para programar com recarregamento rápido, suba só o banco e rode os dois na máquina:
```
docker compose up -d db

cd backend && SPRING_PROFILES_ACTIVE=local ./gradlew bootRun
cd frontend && npm run dev
```
O frontend abre em `http://localhost:5173` e repassa `/api` para o backend em `localhost:8080`.
No IntelliJ, abra a pasta `backend`, rode a classe `Application` e marque o perfil `local`; nenhuma variável precisa ser configurada.

**Sobre as portas:** 5173 é a porta do servidor de desenvolvimento do Vite; 8081 é a porta publicada da pilha completa, onde o Caddy serve os arquivos já construídos.

**Sobre o `--build`:** o Docker sobe contêineres a partir de imagens já construídas. Mudou código, use `docker compose up -d --build` para reconstruir; para apenas religar, `docker compose up -d` basta.

## Como rodar os testes
```
cd backend && ./gradlew test      # regra e integração com Postgres real
cd frontend && npm test           # componentes
python3 .claude/scripts/check_docs.py   # documentos
```

## Como navegar pela documentação
1. `docs/product/vision.md`: o que é o produto e por quê.
2. `docs/product/glossary.md`: termos do domínio.
3. `docs/adr/`: decisões vigentes (status `aceito`), em ordem numérica. Leia a linha **Decisão** de cada uma; aprofunde só no que precisar.
4. `docs/specs/`: comportamento de cada feature.
5. `docs/runbooks/`: só quando for operar o sistema.

Para escrever documentos, siga `docs/standards/documentation.md`. As convenções de código de cada lado ficam em `.claude/rules/backend.md` e `.claude/rules/frontend.md`.
