# Operar issues e board pelo gh

Comandos validados neste projeto. Nada aqui é fixo de um repositório: tudo é descoberto na hora.

## Conteúdo
- Descobrir repositório, board e IDs
- Criar issue, sub-issue e adicionar ao board
- Mudar status e ordem
- Armadilhas

## Descobrir repositório, board e IDs
```bash
gh repo view --json nameWithOwner -q .nameWithOwner
gh project list --owner <owner> --format json -q '.projects[] | "\(.number) \(.title)"'
# campo Status e opções (IDs das colunas)
gh api graphql -f query='{ user(login:"<owner>"){ projectV2(number:<n>){ id
  field(name:"Status"){ ... on ProjectV2SingleSelectField { id options{ id name } } } } } }'
```
Ler board exige o scope `read:project`; criar issue e ligar sub-issue exige só `repo`. Conferir com `gh auth status`; adicionar com `gh auth refresh -h github.com -s project`.

## Criar issue, sub-issue e adicionar ao board
```bash
gh issue create --title "<título>" --body "<corpo>" --label "type: story" --milestone "1. MVP"
```
Uma flag `--label` por label, nunca várias numa string só.

O `gh` não cria sub-issue; o vínculo é por API, usando o **id** da issue (não o número):
```bash
gh api -X POST repos/<owner>/<repo>/issues/<numero_do_pai>/sub_issues -f sub_issue_id=<id_do_filho>
```

Adicionar ao board e marcar a coluna:
```bash
gh api graphql -f query='mutation{ addProjectV2ItemById(input:{projectId:"<PVT_...>",contentId:"<id_da_issue>"}){item{id}} }'
gh api graphql -f query='mutation{ updateProjectV2ItemFieldValue(input:{projectId:"<PVT_...>",itemId:"<PVTI_...>",
  fieldId:"<PVTSSF_...>",value:{singleSelectOptionId:"<id_da_opção>"}}){projectV2Item{id}} }'
```

## Mudar ordem
A ordem no board é posição do item, não número da issue:
```bash
gh api graphql -f query='mutation{ updateProjectV2ItemPosition(input:{projectId:"<PVT_...>",itemId:"<este>",
  afterId:"<vem depois deste>"}){items(first:1){totalCount}} }'
```

## Armadilhas
- **Renomear coluna, nunca substituir.** Em `updateProjectV2Field`, mandar as opções sem o `id` apaga as antigas e cria outras; as automações que apontavam para elas quebram e são desligadas. Passe sempre o `id` de cada opção.
- **A API não cria automação.** Só existe `deleteProjectV2Workflow`. Ligar e configurar automação é na tela. Um board novo pode ser criado como cópia (`copyProjectV2`) de um que já tenha as automações certas.
- **A API não agrupa view.** Cria e edita view (`createProjectV2View`, `updateProjectV2View`), mas "Group by" é na tela.
- **Item recém-adicionado demora a aparecer** na listagem. Se um script for reaplicar posições logo depois, rode de novo em vez de tratar como erro.
- **A automação de sub-issues já adiciona os filhos ao board.** Adicionar o pai e depois o filho dá "Content already exists in this project": trate como item já existente.
- **Número de issue nunca é reaproveitado.** Apagar deixa buraco; por isso a estrutura é aprovada antes de criar.
