---
status: ativo
atualizado: 2026-10-12
---
# Runbook: Implantar uma versão

**Quando usar:** para pôr uma versão nova no servidor que já está ligado, ou para voltar à versão anterior.

## Pré-requisitos
- Servidor ligado: [Ligar e desligar o servidor](ligar-e-desligar-o-servidor.md). Ligar já implanta; este runbook é para depois.
- A versão é um commit (alteração registrada no repositório) da `main` cujo CI (as máquinas do GitHub que testam e publicam) terminou verde: é ele que publica as duas imagens (pacotes prontos para rodar) da versão.
- **O deploy ainda não copia o banco.** Voltar a versão troca a aplicação, mas não desfaz o que a versão nova tiver alterado no banco.

## Passos
1. **Implantar.** No GitHub: **Actions**, **deploy**, **Run workflow**. Campo de versão vazio implanta o último commit da `main`; para outra versão, informe os 7 primeiros caracteres do commit, ou mais.
2. **Ler o resumo.** A execução termina com `Deployed <versão>` e `Before it was: <versão anterior>`. A anterior é a que se usa para voltar.
3. **Voltar.** O mesmo botão, com a versão anterior no campo.

Antes de tocar no servidor, o fluxo confere que a versão é um commit da `main` e que as duas imagens existem. A aplicação é trocada sem reiniciar o banco.

A senha do banco nasce no servidor no primeiro deploy, fica só no arquivo `~/app/.env` dele e é mantida nos deploys seguintes.

Um deploy leva cerca de 1 minuto; bem mais que isso é sinal de imagem ainda não publicada ou de aplicação que não ficou saudável.

## Como confirmar que deu certo
- O resumo mostra a versão pedida em `Deployed`.
- De um computador da rede privada, o servidor diz o que está rodando, e a versão aparece depois dos dois-pontos:

```bash
ssh finance@personal-finance 'docker ps --format "{{.Image}}"'
```
- `http://personal-finance/api/health` responde `"status":"UP"`.

## Se der errado
- **`invalid version`**, **`matches no commit, or more than one`** ou **`is not a commit of main`:** o texto do campo não identifica um commit da `main`. Use mais caracteres ou confira o commit.
- **`the images of ... did not show up`:** o CI daquele commit ainda está rodando ou falhou. Veja a execução dele em **Actions**.
- **`the server did not answer`:** o servidor está desligado. Ligue com **server up**.
- **`has no production compose file`:** a versão é anterior à criação do deploy e não pode ser implantada.
- **`the application was not healthy after 3 minutes`:** o fluxo não volta sozinho. Implante a versão anterior do resumo e, para ver o motivo, rode no servidor `cd ~/app && docker compose logs backend`.
