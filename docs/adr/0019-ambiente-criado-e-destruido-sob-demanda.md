---
status: aceito
atualizado: 2026-09-24
---
# ADR-0019: Ambiente criado e destruído sob demanda, com o estado do banco fora do provedor

**Decisão:** o ambiente é **criado e destruído por código**, sem nada preservado no provedor (sem volume, sem imagem guardada, sem endereço fixo), e o estado do banco sobrevive como **cópia num armazenamento de objetos externo**, restaurada quando o ambiente sobe. Desligar significa destruir, e destruído o custo é zero.

## Contexto
Decorre do [ADR-0015](0015-servidor-proprio-com-conteineres.md), e vale enquanto o produto não for usado todo dia: ele vai ficar ligado por horas e desligado por dias. Nos provedores de servidor virtual, desligar a máquina **não** interrompe a cobrança: continuam sendo cobrados o disco e o endereço reservado. O nome estável de acesso vem da rede privada, então perder o endereço do provedor a cada criação não atrapalha.

## Alternativas descartadas
- **Manter o servidor sempre ligado:** nada para automatizar e o app sempre no ar. Paga o mês inteiro mesmo em semanas sem uso, que é o oposto do que se quer nesta fase.
- **Desligar sem destruir:** parece o caminho óbvio. Não zera a conta, porque disco e endereço continuam cobrados, e a economia fica pequena demais para justificar o hábito.
- **Preservar o disco do banco num volume separado:** dado intacto, sem restauração, e subir fica mais rápido. O volume é cobrado por GB enquanto existir, então o custo nunca chega a zero, e o caminho de restauração deixa de ser exercitado.
- **Guardar uma imagem da máquina inteira:** recria rápido e barato por GB. A imagem envelhece: os lançamentos gravados depois dela não existem, então ela protege o sistema e não o dado.
- **Banco gerenciado em plano grátis que dorme sozinho:** custo zero parado, sem restauração, e sempre disponível. Tira o dado financeiro de dentro do ambiente que controlamos e amarra o produto ao limite de um plano grátis de terceiro.

## Consequências
- **Ganhos:** custo zero com o ambiente destruído; a restauração é exercitada a cada subida, então ela nunca é uma surpresa no dia ruim.
- **Custos:** enquanto destruído, o app não existe; subir leva minutos, não segundos; a restauração vira caminho crítico, e falha nela é perda de dado.
- **Passa a ser obrigatório:**
  - criar e destruir sempre pelo código, nunca pelo painel do provedor, senão o ambiente recriado não é o mesmo;
  - destruir só depois que a cópia do banco estiver no armazenamento externo e verificada;
  - subir termina com a conferência de que o dado restaurado é o esperado;
  - destruir o ambiente não pode alcançar a cópia; como esse isolamento é garantido fica em aberto;
  - quando o uso virar diário, esta decisão é revista;
  - qual ferramenta descreve a infraestrutura em código fica em aberto.
