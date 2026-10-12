---
status: aceito
atualizado: 2026-10-12
---
# ADR-0023: Destruir o ambiente não alcança a cópia do banco

**Decisão:** o arquivo com a cópia do banco fica protegido por **três barreiras**, porque cada uma impede um acidente que as outras deixam passar.

| Barreira | O que é | Acidente que ela impede |
|---|---|---|
| **Duas camadas de código** | A infraestrutura fica em duas pastas separadas. A **persistente** descreve o que nunca é apagado: o bucket (pasta num serviço de armazenamento de arquivos) das cópias, o firewall (filtro de quem alcança o servidor) e as regras da rede privada. A **efêmera** descreve só o servidor. O comando de destruir roda apenas na efêmera | Desligar o servidor apagar junto o bucket das cópias |
| **Chave do servidor com permissão mínima** | A chave que o servidor usa para falar com o bucket só permite gravar e ler arquivos dentro dele. Não permite apagar o bucket nem mudar as regras dele | Um script com defeito no servidor, ou alguém que roube essa chave, apagar o bucket inteiro |
| **Trava de retenção** | Regra do próprio bucket: arquivo gravado passa um prazo sem poder ser apagado nem substituído, seja qual for a chave usada | A cópia de hoje, estragada, ser gravada por cima da cópia boa de ontem; ou a chave roubada apagar os arquivos um por um |

## Contexto
- **O que é a cópia:** um arquivo único com todos os dados, gerado pelo próprio banco antes de o servidor ser destruído e enviado para o bucket, que fica em outra empresa que não a do servidor.
- **Por que ela é crítica:** pelo [ADR-0019](0019-ambiente-criado-e-destruido-sob-demanda.md), enquanto o ambiente está destruído esse arquivo é o único lugar onde os dados existem. Perder o arquivo é perder todos os lançamentos.
- **Por que destruir é perigoso:** pelo [ADR-0022](0022-terraform-descreve-a-infraestrutura.md), o comando de destruir apaga tudo o que está descrito na pasta em que ele roda. Bucket e servidor na mesma pasta seriam apagados juntos.

## Alternativas descartadas
- **Uma pasta só, com o bucket marcado como "não destruir":** a ferramenta tem uma marca que, posta num recurso, faz o comando de destruir parar com erro. Na prática o comando para e não apaga nada, nem o servidor, então desligar exigiria apontar recurso por recurso a cada vez. No dia em que alguém tirar a marca para simplificar, o mesmo comando apaga bucket e cópias.
- **Bucket criado à mão, clicando no painel do serviço:** o código não sabe que ele existe, então destruir não o alcança. A trava e as permissões passam a existir só na tela do painel, sem revisão e sem histórico de quem mudou, e recriar igual depois de um engano depende de lembrar o que foi clicado.
- **Enviar cada cópia para dois buckets, em empresas diferentes:** protege contra perder a conta inteira numa delas. Não impede nenhum dos três acidentes, porque o mesmo script com defeito grava a cópia estragada nos dois, e ainda dobra as contas e as chaves a guardar.

## Consequências
- **Ganhos:** desligar o servidor é um comando só, que não tem como tocar nas cópias; uma cópia estragada não elimina a boa anterior; quem roubar a chave do servidor não consegue apagar o histórico.
- **Custos:** montar o projeto do zero exige rodar as duas pastas, na ordem; a chave do servidor continua lendo as cópias, então quem a roubar lê os dados; cópia estragada ocupa espaço até a trava vencer; apagar o bucket de propósito exige esperar o prazo.
- **Passa a ser obrigatório:**
  - cada cópia é gravada com nome próprio, com data e hora, porque gravar por cima é barrado;
  - a camada efêmera depende de recursos da persistente; como ela os referencia fica em aberto;
  - se a camada persistente não existir, criar o servidor falha, em vez de subir sem firewall;
  - o prazo da trava e por quanto tempo as cópias são guardadas ficam no runbook de backup.
