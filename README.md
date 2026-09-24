# personal-finance

Aplicação de finanças pessoais para registrar e entender gastos num lugar só, individualmente ou em grupo. Desenvolvida com um fluxo agêntico (agentes de IA implementam, pessoas decidem e revisam) guiado por SDD (Spec-Driven Development: toda feature começa por uma especificação).

## Como rodar localmente
Copie `.env.example` para `.env`, preencha os valores e suba tudo:
```
docker compose up -d --build
```
O app fica em `http://localhost:8081` (a porta vem de `APP_PORT`).

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
