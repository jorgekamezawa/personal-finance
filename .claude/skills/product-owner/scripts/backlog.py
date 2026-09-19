"""Cria milestones, épicos e histórias no GitHub e coloca tudo no board, na ordem do arquivo.

Uso:
  python3 backlog.py plano.json --dry-run   mostra o que faria, sem criar nada
  python3 backlog.py plano.json             cria

Formato do plano.json:
{
  "milestones": [{"title": "1. MVP", "description": "..."}],
  "epics": [
    {"milestone": "1. MVP", "title": "Lançamentos", "body": "...",
     "stories": [{"title": "Registrar gasto", "body": "..."}]}
  ]
}

Repositório, board e IDs são descobertos pelo gh. Exige as labels `type: epic` e `type: story`
e o scope `project` no token (gh auth refresh -h github.com -s project).
"""

import json
import subprocess
import sys

BACKLOG_OPTION = "Backlog"


def gh(*args, stdin=None):
    out = subprocess.run(["gh", *args], input=stdin, capture_output=True, text=True)
    if out.returncode or '"errors"' in out.stdout:
        raise SystemExit(f"falhou: gh {' '.join(args)}\n{out.stderr}{out.stdout}")
    return out.stdout


def api(method, path, **fields):
    return json.loads(gh("api", "-X", method, path, "--input", "-", stdin=json.dumps(fields)) or "{}")


def gql(query, **variables):
    body = json.dumps({"query": query, "variables": variables})
    return json.loads(gh("api", "graphql", "--input", "-", stdin=body))["data"]


def descobrir():
    repo = gh("repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner").strip()
    owner, name = repo.split("/")
    data = gql("""query($o:String!,$n:String!){ repository(owner:$o,name:$n){
        projectsV2(first:10){ nodes{ id number title
          field(name:"Status"){ ... on ProjectV2SingleSelectField { id options{ id name } } } } } } }""",
               o=owner, n=name)["repository"]["projectsV2"]["nodes"]
    if not data:
        raise SystemExit("nenhum board ligado a este repositório")
    if len(data) > 1:
        raise SystemExit("mais de um board ligado; resolva qual usar antes de rodar")
    board = data[0]
    campo = board["field"]
    opcao = next(o["id"] for o in campo["options"] if o["name"] == BACKLOG_OPTION)
    return repo, board, campo["id"], opcao


def milestones_existentes(repo):
    return {m["title"]: m["number"] for m in json.loads(gh("api", f"repos/{repo}/milestones?state=all"))}


def itens_do_board(numero_board, owner):
    nodes = gql("""query($o:String!,$n:Int!){ user(login:$o){ projectV2(number:$n){
        items(first:100){ nodes{ id content{ ... on Issue { id } } } } } } }""",
                o=owner, n=numero_board)["user"]["projectV2"]["items"]["nodes"]
    return {n["id"]: n["content"]["id"] for n in nodes if n.get("content")}


def main(argv):
    if not argv:
        raise SystemExit(__doc__)
    plano = json.load(open(argv[0], encoding="utf-8"))
    dry = "--dry-run" in argv
    repo, board, campo_id, opcao_backlog = descobrir()
    owner = repo.split("/")[0]
    existentes = milestones_existentes(repo)

    if dry:
        print(f"repositório: {repo}\nboard: #{board['number']} {board['title']}\n")
        for m in plano.get("milestones", []):
            print(f"{'já existe' if m['title'] in existentes else 'criar'} milestone: {m['title']}")
        for e in plano["epics"]:
            print(f"\ncriar épico [{e['milestone']}]: {e['title']}")
            for s in e.get("stories", []):
                print(f"  criar história: {s['title']}")
        total = len(plano["epics"]) + sum(len(e.get("stories", [])) for e in plano["epics"])
        print(f"\ntotal: {total} issues. Nada foi criado.")
        return 0

    for m in plano.get("milestones", []):
        if m["title"] not in existentes:
            novo = api("POST", f"repos/{repo}/milestones", title=m["title"],
                       description=m.get("description", ""))
            existentes[m["title"]] = novo["number"]
            print(f"milestone criado: {m['title']}")

    criadas = []
    for e in plano["epics"]:
        epico = api("POST", f"repos/{repo}/issues", title=e["title"], body=e.get("body", ""),
                    milestone=existentes[e["milestone"]], labels=["type: epic"])
        criadas.append(epico)
        print(f"épico #{epico['number']}: {epico['title']}")
        for s in e.get("stories", []):
            hist = api("POST", f"repos/{repo}/issues", title=s["title"], body=s.get("body", ""),
                       milestone=existentes[e["milestone"]], labels=["type: story"])
            api("POST", f"repos/{repo}/issues/{epico['number']}/sub_issues", sub_issue_id=hist["id"])
            criadas.append(hist)
            print(f"  história #{hist['number']}: {hist['title']}")

    # A automação de sub-issues pode já ter adicionado filhos ao board; só entra o que falta.
    no_board = set(itens_do_board(board["number"], owner).values())
    for issue in criadas:
        if issue["node_id"] not in no_board:
            gql("""mutation($p:ID!,$c:ID!){ addProjectV2ItemById(input:{projectId:$p,contentId:$c}){item{id}} }""",
                p=board["id"], c=issue["node_id"])

    itens = {v: k for k, v in itens_do_board(board["number"], owner).items()}
    anterior = None
    for issue in criadas:
        item = itens.get(issue["node_id"])
        if not item:  # o board demora a listar item recém-criado; rode o script de novo
            print(f"aviso: #{issue['number']} ainda não apareceu no board; rode de novo para ordenar")
            continue
        gql("""mutation($p:ID!,$i:ID!,$f:ID!,$o:String!){ updateProjectV2ItemFieldValue(input:{projectId:$p,
            itemId:$i,fieldId:$f,value:{singleSelectOptionId:$o}}){projectV2Item{id}} }""",
            p=board["id"], i=item, f=campo_id, o=opcao_backlog)
        if anterior:
            gql("""mutation($p:ID!,$i:ID!,$a:ID!){ updateProjectV2ItemPosition(input:{projectId:$p,itemId:$i,
                afterId:$a}){items(first:1){totalCount}} }""", p=board["id"], i=item, a=anterior)
        anterior = item
    print(f"\n{len(criadas)} issues no board, em Backlog, na ordem do plano.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
