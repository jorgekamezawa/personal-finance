# Checklist antes de entregar um ADR

Confira item a item antes de mostrar o texto. Cada linha aqui nasceu de um erro real, apontado por revisão.

## Conteúdo
- [ ] A primeira frase diz **a decisão e o porquê**, não só a decisão.
- [ ] A decisão responde **uma** pergunta. Duas decisões com vida própria viram dois ADRs.
- [ ] As alternativas respondem **à mesma pergunta** do ADR. Ferramenta de build não é alternativa a linguagem.
- [ ] Cada alternativa é explicada **pelo que faz na prática**, de modo que quem nunca usou entenda a diferença. Nada de descartar por categoria.
- [ ] Idealmente 3 opções (escolhida e 2 descartadas). Menos só quando não existe alternativa real, e o contexto diz por quê.
- [ ] O debate não está aqui: prós, contras e comparação ficaram na conversa; o ADR guarda o resultado.

## Consequências
- [ ] **Nenhuma consequência escolhe.** Para cada item: existia alternativa plausível que este ADR não debateu? Se existia, é decisão nova.
- [ ] Decisão nova encontrada vira ADR próprio, e aqui fica só a menção de que está em aberto, **sem apontar para um ADR que ainda não existe**.
- [ ] Consequência não decide o futuro ("quando X, faremos Y"): registre que a decisão será revista, e pare aí.

## Fronteiras
- [ ] Regra de negócio não está aqui: ela vive na spec da feature.
- [ ] Convenção de código não está aqui: ela vive no perfil de stack.
- [ ] Fornecedor, plano, preço e número de versão não estão aqui: vivem no runbook ou no arquivo de build.
- [ ] Nenhum argumento de portfólio, de consistência com outro projeto ou de vontade de aprender.

## Forma
- [ ] Termo de domínio explicado no primeiro uso, entre parênteses e em poucas palavras.
- [ ] Lista ou tabela em vez de prosa; parágrafo com no máximo 3 frases.
- [ ] Nada copiado de outro documento: linke a fonte.
- [ ] Sem travessão e sem meia-risca.
- [ ] Status `proposto` enquanto se decide; vira `aceito` na aprovação.

## Depois de escrever
- [ ] Script de verificação de documentos rodado, sem erro.
- [ ] Subagente `doc-reviewer` chamado, apontamentos aplicados ou recusados com motivo.
- [ ] Texto mostrado para aprovação antes do commit.
