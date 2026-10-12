---
status: aceito
atualizado: 2026-10-12
---
# ADR-0022: Terraform descreve a infraestrutura em código

**Decisão:** o código que cria e destrói o ambiente é escrito em **Terraform**, porque ele compara o que está descrito com o que existe e aplica só a diferença, e o plugin (módulo que ensina a ferramenta a falar com um serviço) do provedor do servidor é mantido pelo próprio provedor.

## Contexto
O [ADR-0019](0019-ambiente-criado-e-destruido-sob-demanda.md) obriga a criar e destruir o ambiente sempre por código e deixou a ferramenta em aberto. O que precisa ser descrito é pouco: um servidor, um firewall, a entrada na rede privada e o armazenamento da cópia do banco. Quem executa é uma pessoa na própria máquina ou o CI (as máquinas do GitHub que rodam os fluxos do projeto), nunca os dois ao mesmo tempo.

## Alternativas descartadas
- **OpenTofu:** cópia de código aberto do Terraform, que lê os mesmos arquivos e usa os mesmos plugins, e ainda criptografa sozinha o registro do que criou. A compatibilidade com o plugin do provedor do servidor não pôde ser confirmada na fonte, e trocar depois custa pouco, porque os arquivos são os mesmos.
- **Pulumi:** a mesma ideia de descrever e aplicar a diferença, escrita em linguagem de programação (Java, TypeScript) em vez de arquivo de configuração. Para um servidor e um firewall, um programa com dependências e compilação pesa mais que o problema, e o registro do que foi criado fica por padrão no serviço da própria empresa, que seria mais uma conta.
- **Script com a linha de comando do provedor:** um shell que roda "crie o servidor" e "apague o servidor", sem nada a instalar além do cliente. Ele não sabe o que já existe: rodar duas vezes cria duas máquinas, e destruir depende de o script lembrar tudo o que criou.

## Consequências
- **Ganhos:** rodar de novo sem mudança não altera nada; destruir apaga exatamente o que foi criado; a mudança de infraestrutura passa por revisão em PR como qualquer código.
- **Custos:** passa a existir o **arquivo de estado** (registro que liga cada item do código ao recurso real que foi criado), e perdê-lo deixa recursos órfãos, que continuam sendo cobrados; a ferramenta só descobre falta de estoque de máquina ao falhar no meio da criação.
- **Passa a ser obrigatório:**
  - o arquivo de estado mora fora do ambiente que é destruído, num lugar que a pessoa e o CI alcancem; qual lugar fica no runbook de deploy;
  - o arquivo de estado nunca entra no repositório, porque guarda os segredos de tudo o que foi criado;
  - duas execuções nunca escrevem no mesmo estado ao mesmo tempo; se isso é garantido pela trava da própria ferramenta ou por fila no CI depende de um teste ainda não feito;
  - nenhum recurso é criado, alterado ou apagado pelo painel do provedor, senão o estado deixa de descrever a realidade;
  - a versão da ferramenta e a de cada plugin ficam fixadas no próprio código de infraestrutura.
