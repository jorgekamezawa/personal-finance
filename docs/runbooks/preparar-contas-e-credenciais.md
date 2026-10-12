---
status: ativo
atualizado: 2026-10-12
---
# Runbook: Preparar contas e credenciais

**Quando usar:** ao montar a infraestrutura do zero, ou ao trocar uma credencial vazada ou vencida.

## Pré-requisitos
- Conta na Hetzner (onde roda o servidor) e na Cloudflare (onde ficam as cópias do banco), com o R2 (armazenamento de arquivos da Cloudflare) ativado.
- Terraform 1.15 (ferramenta que cria a infraestrutura a partir de arquivos) instalado e um par de chaves SSH (o que permite entrar no servidor sem senha) no computador.
- Todo valor obtido aqui vai para o arquivo `infra/.env.terraform`, criado no passo 1 e ignorado pelo git. Nenhum deles entra em commit, conversa ou captura de tela.

## Passos
O nome de cada credencial diz quem a usa, para saber qual apagar se uma vazar.
1. **Arquivo.** Na raiz do repositório, crie `infra/.env.terraform` com as sete linhas abaixo, ainda sem valor, e feche a leitura para outros usuários. Em cada passo, cole o valor logo depois do `=`, sem espaço.

```bash
HCLOUD_TOKEN=
CLOUDFLARE_API_TOKEN=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_ENDPOINT_URL_S3=
TF_VAR_cloudflare_account_id=
TF_VAR_ssh_public_key=
```
```bash
chmod 600 infra/.env.terraform
```
2. **Hetzner, projeto.** No console, crie o projeto `personal-finance`. Resultado: projeto vazio na lista.
3. **Hetzner, token.** Dentro do projeto: **Security**, **API tokens**, **Generate API token**, descrição `terraform-local`, permissão **Read & Write**. O token aparece uma vez só; ele vira `HCLOUD_TOKEN`.
4. **Cloudflare, bucket do estado.** No R2, crie o bucket (pasta de arquivos do R2) `personal-finance-tfstate`, com **Location** em **Automatic** e **Default Storage Class** em **Standard**. Não escolha jurisdição: ela muda o endereço do bucket e o `init` deixa de achá-lo. É o único recurso criado pelo painel: o Terraform precisa dele para guardar o arquivo de estado (registro do que ele criou) antes de conseguir criar qualquer coisa.
5. **Cloudflare, chave do estado.** Em **Manage account**, **Account API tokens**, **Create Token**, com **Start from scratch**:
   - Nome `personal-finance-tfstate`, **No expiration**, filtro de IP vazio.
   - Alvo: troque **Entire Account** por **R2 Buckets** e escolha só `personal-finance-tfstate`. A permissão só aparece depois disso.
   - Permissão: **Read** e **Edit** em **Workers R2 Storage Bucket Item**. A tela de revisão deve listar uma política só.
   - A tela final aparece uma vez só. **Account ID** vira `TF_VAR_cloudflare_account_id`, **Access Key ID** vira `AWS_ACCESS_KEY_ID`, **Secret Access Key** vira `AWS_SECRET_ACCESS_KEY` e **S3 API endpoint** vira `AWS_ENDPOINT_URL_S3`. O campo **Your API Token** não é usado.
6. **Cloudflare, token de administração.** Mesmo caminho, nome `personal-finance-terraform`, alvo em **Entire Account**. Busque `R2` e marque **Read** e **Edit** em **Workers R2 Storage**, com **No expiration** e filtro de IP vazio. Na tela final, o campo **Your API Token** vira `CLOUDFLARE_API_TOKEN`; é ele que cria o bucket das cópias e a trava de retenção (regra que impede apagar ou substituir uma cópia por 30 dias).
7. **Chave SSH.** No terminal Linux em que o repositório está (no Windows, o do WSL, o Linux que roda dentro do Windows), rode `cat ~/.ssh/id_ed25519.pub`: ele imprime uma linha que começa com `ssh-ed25519`. É a metade pública da chave, que não é segredo. A linha inteira, entre aspas porque tem espaços, vira `TF_VAR_ssh_public_key`. Se o arquivo não existir, crie o par antes com `ssh-keygen -t ed25519`.
8. **Carregar as credenciais.** Na raiz do repositório. O comando não imprime nada e vale só para aquele terminal: abriu outro, rode de novo.

```bash
set -a && . ./infra/.env.terraform && set +a
```
9. **Preparar.** Baixa os plugins e conecta ao bucket do estado. Resultado: `Terraform has been successfully initialized!`

```bash
terraform -chdir=infra/persistent init
```
10. **Ver o plano.** Mostra o que seria criado, sem criar nada. Resultado: `Plan: 4 to add, 0 to change, 0 to destroy.` Qualquer número diferente em `destroy`, pare.

```bash
terraform -chdir=infra/persistent plan
```
11. **Aplicar.** Mostra o plano de novo e só cria depois que você digita `yes`. Resultado: `Apply complete! Resources: 4 added, 0 changed, 0 destroyed.`

```bash
terraform -chdir=infra/persistent apply
```

### Credenciais do CI
12. **Rede privada, duas credenciais.** O CI (as máquinas do GitHub que rodam os botões de ligar e desligar o servidor) entra na rede com credenciais próprias. No painel do Tailscale (o serviço da rede privada): **Settings**, **Trust credentials**, **Credential**, **OpenID Connect**, com **Issuer** em **GitHub**. São duas porque uma máquina recebe todas as etiquetas da credencial que a pôs na rede, e o CI não pode ter a etiqueta do servidor. Nenhuma guarda segredo: o GitHub prova quem está rodando.

| Description | Permissão | Etiqueta |
|---|---|---|
| `personal-finance-server` | **Auth Keys**, **Write** | `tag:financas-server` |
| `personal-finance-ci` | **Auth Keys**, **Write** | `tag:financas-ci` |

O **Subject** das duas é o prefixo abaixo seguido de `:ref:refs/heads/main`, o que restringe o uso à `main`:

```bash
gh api repos/<dono>/<repositório>/actions/oidc/customization/sub --jq .sub_claim_prefix
```
13. **GitHub, variáveis.** Cada credencial mostra um **Client ID** e um **Audience**, que não são segredos:

```bash
gh variable set TS_SERVER_CLIENT_ID --body "<client id de personal-finance-server>"
gh variable set TS_SERVER_AUDIENCE --body "<audience de personal-finance-server>"
gh variable set TS_CI_CLIENT_ID --body "<client id de personal-finance-ci>"
gh variable set TS_CI_AUDIENCE --body "<audience de personal-finance-ci>"
```
14. **GitHub, segredos.** Quatro valores do arquivo do passo 1. O comando pede o valor e não o mostra na tela. O endereço do bucket do estado entra como segredo porque contém o identificador da conta, e os registros de execução de um repositório público são públicos.

```bash
gh secret set TF_HCLOUD_TOKEN            # HCLOUD_TOKEN
gh secret set TF_AWS_ACCESS_KEY_ID       # AWS_ACCESS_KEY_ID
gh secret set TF_AWS_SECRET_ACCESS_KEY   # AWS_SECRET_ACCESS_KEY
gh secret set TF_STATE_ENDPOINT          # AWS_ENDPOINT_URL_S3
```

O `plan` e o `apply` avisam que a trava de retenção não pode ser apagada pelo Terraform. É esperado: tirar a regra do código não a remove, só o painel remove.

## Como confirmar que deu certo
- `terraform -chdir=infra/persistent plan` responde `No changes`.
- `git status` não lista `infra/.env.terraform`.
- No painel: o bucket `personal-finance-backups` tem uma regra de trava de 30 dias, e a Hetzner mostra o firewall (filtro de quem alcança o servidor) `personal-finance-closed` sem regra de entrada e a chave `personal-finance-admin`.

## Se der errado
- **Carregar o arquivo responde `command not found`:** a linha indicada tem espaço e está sem aspas; é o caso da chave SSH. Corrija e carregue de novo.
- **`init` falha com erro de credencial ou de endereço:** confira `AWS_ENDPOINT_URL_S3` e se a chave do passo 5 alcança o bucket do estado.
- **`plan` falha com 403 na Cloudflare:** o token do passo 6 não tem permissão de administração do R2. Crie outro e apague o anterior.
- **`Error acquiring the state lock`:** outra execução está em andamento ou morreu no meio. Confirme que nenhuma está rodando antes de usar `terraform force-unlock <ID>`.
- **O botão do CI falha com `token exchange failed with status 403`:** o **Subject** da credencial não bate com o que o GitHub envia. Confira o prefixo com o comando do passo 12.
- **Credencial vazou:** apague-a no painel do fornecedor, gere outra pelo mesmo passo e troque o valor no arquivo.
