---
status: aceito
atualizado: 2026-09-24
---
# ADR-0017: Publicar imagem a cada commit da main, e disparar o deploy à mão pelo GitHub

**Decisão:** a entrada na `main` **publica automaticamente** as imagens de backend e frontend, marcadas com o identificador do commit; o **deploy é disparado à mão**, por um fluxo do GitHub que recebe a versão e implanta no servidor, porque assim fica registrado quem implantou o quê e quando, e a migração de banco só roda quando alguém está olhando.

## Contexto
Decorre do [ADR-0015](0015-servidor-proprio-com-conteineres.md). O servidor não fica exposto na internet, então qualquer automação precisa entrar pela rede privada. As primeiras migrações vão rodar num banco que ainda está tomando forma, e o produto tem um ou dois usuários, então o custo de esperar alguém clicar é baixo.

## Alternativas descartadas
- **Deploy automático a cada merge:** elimina o passo manual e mantém o que está no ar igual à `main`. Uma migração de banco passaria a rodar sem ninguém acompanhando, e a primeira falha aconteceria no meio de outra tarefa; o ganho aparece quando há entregas frequentes, que não é o caso ainda.
- **Deploy rodado por comando no próprio servidor:** não precisa de credencial nova, porque quem entra é você. Não deixa registro de quem implantou qual versão, e é justamente esse registro que se quer quando algo quebrar.
- **Servidor observando o registro de imagens e se atualizando sozinho:** dispensa acesso de fora e passo manual. O deploy passa a acontecer quando o servidor decide, sem ordem garantida entre backend e frontend, e com migração rodando sozinha.
- **Publicar imagem só do artefato que mudou:** economiza alguns minutos por commit. Quebra a propriedade de que qualquer commit da `main` é implantável, porque um commit de documentação deixaria de ter imagem com aquele identificador.

## Consequências
- **Ganhos:** qualquer commit da `main` pode ser implantado e revertido; o histórico de deploys diz quem, o quê e quando; a versão nova só entra quando alguém decide.
- **Custos:** o que está no ar pode ficar atrás da `main` se ninguém disparar; o CI precisa de credencial para entrar na rede privada e no servidor, que passa a ser segredo a proteger e renovar.
- **Passa a ser obrigatório:**
  - a suíte de testes é portão da publicação: nada é publicado se ela falhar;
  - a imagem leva o identificador do commit, e voltar atrás é implantar o identificador anterior;
  - o servidor baixa imagem e nunca constrói;
  - o fluxo de deploy confere se as imagens daquela versão existem antes de tocar no servidor, e só considera o deploy concluído quando a verificação de saúde responde;
  - segredo nenhum entra no repositório: ficam nos segredos do GitHub e no arquivo de ambiente do servidor;
  - a suíte que serve de portão precisa ser rápida o bastante para rodar a cada publicação; como isso é organizado no PR é decisão própria.
