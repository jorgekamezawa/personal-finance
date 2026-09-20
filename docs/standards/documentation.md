---
status: ativo
atualizado: 2026-09-19
---
# Padrão de documentação

Como escrever, organizar e verificar os documentos do projeto. Vale para documentos lidos por pessoas; `CLAUDE.md` e skills seguem o guia da Anthropic.

## Regras de escrita
1. **Resposta primeiro.** As primeiras linhas trazem a conclusão, a decisão ou o propósito. O detalhe vem depois.
2. **Um propósito por documento.** Dois propósitos, dois documentos.
3. **Sem enchimento.** Seção que não se aplica é apagada, não marcada como `N/A`.
4. **Fonte única.** Linke a informação; nunca copie.
5. **Listas e tabelas antes de prosa.** Parágrafos com no máximo 3 frases.
6. **Teste de corte.** Se apagar a frase não perde informação, apague.
7. **Explique no primeiro uso.** Termo de domínio ou pouco comum ganha uma explicação curta na primeira vez.
8. **Orçamento de tamanho.** Cada tipo tem um tamanho de referência. A verificação automática aponta quando passar; passar é permitido com motivo registrado.
9. **Diagramas em Mermaid** (diagrama escrito em texto, que o GitHub desenha), só quando substituem texto, não para enfeitar.
10. **Documento só existe quando tem gatilho.** O template fica pronto; o documento nasce quando o gatilho acontece.
11. **Sem travessão (`—`) nem meia-risca (`–`).** Use vírgula, dois-pontos, parênteses ou reescreva.

## Metadados
Todo documento começa com frontmatter (cabeçalho de metadados no topo do arquivo):
```yaml
---
status: rascunho | ativo | substituído | obsoleto
atualizado: AAAA-MM-DD
---
```
O ADR (registro de decisão de arquitetura) usa status próprio (ver seção ADR). O README não tem frontmatter: o GitHub o mostraria como tabela no topo da vitrine.

## Ciclo de vida
- O documento nasce do template em `docs/templates/` quando o gatilho do seu tipo acontece.
- Só é commitado depois de aprovado. Rejeitado durante a escrita é excluído, sem passar pelo git.
- Seções do template são obrigatórias, exceto as marcadas "só quando houver".

## Verificação
- **Script:** roda ao salvar arquivo em `docs/` e no CI. Erro: metadados ausentes, travessão, `N/A`, seção obrigatória ausente. Aviso: tamanho acima da referência.
- **doc-reviewer:** subagente com contexto limpo que confere as regras 1 a 7 ao terminar um documento. Aponta só violação deste padrão, não preferência de estilo.

## Catálogo
| Tipo | Para que serve | Gatilho | Dono | Tamanho ref. |
|---|---|---|---|---|
| Visão do produto | Problema, público, objetivos, o que fica fora | Início do projeto | produto | 60 linhas |
| ADR | Registrar uma decisão técnica, alternativas e consequências | Decisão cara de reverter ou que afeta vários módulos | técnico | 40 linhas |
| README | O que é o projeto, como rodar, como navegar pelos docs | Criação do repositório | técnico | 60 linhas |
| Runbook | Passo a passo de operação (rollback, restaurar backup) | Procedimento que alguém executaria sob pressão | técnico | 40 linhas |
| Glossário | Termos do produto e do projeto, com definição única | Termo usado em 2+ documentos | produto | sem limite |
| Spec de feature | A definir | A definir | ambos | a definir |

- Tamanho conta linhas não vazias, sem metadados e sem blocos de código. Valores iniciais, revisados com o uso.
- Roadmap e backlog ficam no GitHub Projects/Issues.
- Convenções de código vivem em `.claude/` como perfis de stack, não em `docs/`.

## ADR

### Quando abrir um ADR
Três perguntas, nesta ordem:
1. **É arquiteturalmente significativo?** Afeta a estrutura, uma qualidade importante (desempenho, segurança, custo) ou é caro de reverter. Se não, não vira ADR.
2. **Tem vida própria?** Se muda sem derrubar a decisão anterior, ADR próprio. Se só existe por causa dela (escolher o banco obriga a escolher a ferramenta de migração), é uma decisão de duas partes e fica junta.
3. **Muda de rotina?** Versão de linguagem, de framework ou de biblioteca muda todo ciclo. Nesse caso o ADR registra a **política** ("usar a LTS (versão de suporte longo) mais recente suportada pelo framework"), e o número vive no arquivo de build.

Decisão grande gera decisões menores: cada uma vira seu ADR, ligada à anterior pelo contexto. Assim, trocar de framework amanhã substitui um ADR só.

### Como escrever
- Status: `proposto` (em escrita e debate, antes da decisão) | `aceito` | `substituído`.
- **As alternativas respondem à mesma pergunta do ADR.** Ferramenta de build não é alternativa a linguagem.
- **Alternativa descartada é explicada pelo que ela faz na prática,** não pela categoria: quem nunca usou aquela ferramenta precisa entender a diferença.
- **O debate acontece antes, fora do ADR:** opções com prós, contras e consequências se discutem na conversa; o ADR registra o resultado e o motivo curto de cada descarte.
- Idealmente 3 opções (escolhida + 2 descartadas). Menos só se não houver alternativa real, e o contexto diz por quê.
- O porquê da decisão cabe em uma frase; se precisar, até 3 bullets logo abaixo.
- É um retrato do cenário atual. Aceito não se edita: se o cenário mudar, um novo ADR o substitui, e o antigo só recebe status `substituído` e o link.
- Arquivo: `NNNN-titulo-curto.md`, numeração sequencial.

## Estrutura de pastas
```
docs/
├── product/     vision.md, glossary.md
├── adr/         NNNN-titulo-curto.md
├── runbooks/
├── specs/
├── standards/   documentation.md
└── templates/
```
