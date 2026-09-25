# Como trabalhar neste repositório

## Regras invioláveis do fluxo
1. **Nada de commit antes da validação.** Terminou de desenvolver, **pare** e mostre o que foi feito: o que mudou, a evidência de que funciona (comando e saída real) e o que ficou de fora. Só depois da aprovação explícita de quem mantém o projeto vem `git commit`.
2. **Push e PR só depois do commit aprovado**, e também com aprovação explícita. Nunca encadeie desenvolvimento, commit, push e PR na mesma tacada.
3. **Aprovação vale para uma ação só.** Aprovar o desenvolvimento não aprova o commit; aprovar o commit não aprova o push nem o PR.
4. **Um PR aberto por vez.** Só comece o próximo depois que o anterior for mergeado.
5. **Atualizar branch é sempre por rebase**, nunca por merge da `main`.
6. **Documento só é commitado depois de aprovado.** Rejeitado durante a escrita, é apagado sem passar pelo git.
7. Antes de qualquer ação destrutiva (apagar arquivo, volume, branch, recurso em nuvem), pergunte.

Commit, push e abertura de PR passam por um hook que pede confirmação (`.claude/scripts/guard_git.py`), porque texto aqui é contexto e não garantia. O hook pergunta; quem aprova é a pessoa. A primeira aprovação vale para as outras duas ações por alguns minutos, porque na prática elas andam juntas.

## Fluxo de uma mudança
Proposta e decisões em aberto → aprovação → desenvolvimento → **parada para validação** → aprovação → commit → push e PR → merge feito por quem mantém o projeto.

## Onde cada coisa mora
| O quê | Onde |
|---|---|
| Por que escolhemos | `docs/adr/` |
| Experimento que decidiu algo | `docs/spikes/` |
| Regra de negócio | spec da feature em `docs/specs/` |
| Como fazer sempre | `.claude/rules/backend.md` e `frontend.md` |
| Passo a passo de operação | `docs/runbooks/` |
| Fornecedor, plano, preço, versão | runbook e arquivo de build |

## Padrões
- Documentos, specs, mensagem de commit e descrição de PR em português; código, nome de identificador e comentário em inglês.
- Documento segue `docs/standards/documentation.md` e passa por `.claude/scripts/check_docs.py` e pelo subagente `doc-reviewer`.
- Código passa por `.claude/scripts/check_code.py` e por `/code-review` antes de ser mostrado para validação.
- Pronto significa: build passa, suíte verde, sem aviso novo, e evidência mostrada.
- Subiu contêiner para testar, derrube ao terminar.
