# personal-finance

Aplicação de finanças pessoais que substitui o controle manual em planilha. É também o piloto de um fluxo de desenvolvimento agêntico (agentes de IA implementam, pessoas decidem e revisam) guiado por SDD (Spec-Driven Development: toda feature começa por uma especificação).

## Como rodar localmente
A aplicação ainda não existe. Hoje o que roda é o verificador de documentação:
```
python3 .claude/scripts/check_docs.py
```

## Como rodar os testes
```
python3 -m unittest discover -s .claude/scripts -p 'test_*.py'
```

## Como navegar pela documentação
1. `docs/product/vision.md`: o que é o produto e por quê.
2. `docs/product/glossary.md`: termos do domínio.
3. `docs/adr/`: decisões vigentes (status `aceito`), em ordem numérica. Leia a linha **Decisão** de cada uma; aprofunde só no que precisar.
4. `docs/specs/`: comportamento de cada feature.
5. `docs/runbooks/`: só quando for operar o sistema.

Para escrever documentos, siga `docs/standards/documentation.md`.
