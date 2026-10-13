---
status: ativo
atualizado: 2026-10-12
---
# Runbook: Ligar e desligar o servidor

**Quando usar:** para pôr o sistema no ar a partir do nada, ou para tirá-lo. Ligado, o servidor é cobrado por hora; desligado, deixa de existir.

## Pré-requisitos
- Camada persistente aplicada e credenciais do CI (as máquinas do GitHub que rodam os botões) cadastradas: [Preparar contas e credenciais](preparar-contas-e-credenciais.md).
- As etiquetas `tag:financas-server` e `tag:financas-ci` existem na política da rede privada, que é mantida fora deste repositório.
- **Desligar ainda não copia o banco.** Enquanto a cópia não existir, o que estiver no servidor se perde ao desligar.

## Passos
1. **Ligar.** No GitHub: **Actions**, **server up**, **Run workflow**, na branch `main`. Com os campos como vêm, cria o servidor e implanta o último commit da `main`.
   - Outra versão: preencha o campo da versão.
   - Servidor vazio: desmarque a caixa de implantar.

Etapas de criar o servidor, na ordem:

| Etapa | O que faz |
|---|---|
| Choose the machine and create the server | Pega no estoque a máquina mais barata da escada (lista de tamanhos em ordem de preço) e cria o servidor |
| Join the private network | Põe a máquina do CI na rede privada |
| Wait for the server to be ready | Espera Docker, swap (memória de reserva em disco) e a entrada do servidor na rede |
| Prove the CI cannot be root | Falha se o CI abrir sessão como administrador |

Depois dessas etapas roda o deploy, descrito em [Implantar uma versão](implantar-uma-versao.md).

2. **Desligar.** **Actions**, **server down**, **Run workflow**, e digite `destroy` no campo de confirmação. O botão tira o servidor da rede privada e depois o destrói.

Criar o servidor leva de 2 a 4 minutos, quase tudo na espera pela máquina se preparar; com o deploy, some cerca de 1 minuto. Desligar leva menos de 1 minuto.

O arquivo de estado do Terraform (registro do que ele criou) fica num bucket (pasta de armazenamento de arquivos) próprio na Cloudflare, `personal-finance-tfstate`, fora do servidor: ele precisa sobreviver quando o servidor é destruído e ser alcançado pelo CI.

## Como confirmar que deu certo
- **Ligado:** o resumo da execução mostra a máquina criada e a versão implantada, e `http://personal-finance`, de um aparelho da rede privada, abre o sistema.
- **Desligado:** a execução termina com `Destroy complete! Resources: 2 destroyed.`, e o servidor some do painel do provedor e da lista de máquinas da rede privada.

## Se der errado
- **`nothing on the ladder is in stock`:** nenhuma máquina da escada tem estoque. A mensagem lista o que há em cada cidade; tente de novo mais tarde.
- **`token exchange failed with status 403`:** a rede privada recusou a identidade do CI. O botão só é aceito na `main`; confira o **Subject** das credenciais (o texto que diz de qual repositório e branch o pedido pode vir).
- **`description had invalid characters`:** a descrição da chave de entrada tem caractere que a rede recusa, como vírgula.
- **A espera se esgota:** a máquina não terminou de se preparar. Rode **server down** e ligue de novo.
- **`the CI opened a root session`:** a política da rede está larga demais. Corrija a política antes de usar o servidor.
- **`server down` avisa que o servidor não respondeu:** ele é destruído assim mesmo, mas a rede só o esquece mais tarde. Se o próximo nascer antes disso, ganha outro nome e a espera falha: apague a máquina antiga na lista da rede privada.
- **`Error acquiring the state lock`** (trava que impede duas execuções de mexer na infraestrutura ao mesmo tempo)**:** outra execução está em andamento ou morreu no meio; veja o runbook de credenciais.
