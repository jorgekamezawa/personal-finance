---
status: aceito
atualizado: 2026-09-23
---
# ADR-0015: Rodar em servidor virtual próprio, com aplicação e banco em contêineres

**Decisão:** rodar em um **servidor virtual próprio**, com **aplicação e banco em contêineres** no mesmo servidor, porque é o arranjo mais barato que mantém o sistema fora da internet pública enquanto não houver login, e é o mesmo arranjo usado na máquina de desenvolvimento.

## Contexto
O primeiro corte é um MVP para um ou dois usuários, com banco pequeno ([ADR-0008](0008-postgresql-com-flyway.md)) e acesso privado por rede fechada; o lançamento público vem depois. Nessa escala, o custo de operar o servidor é pequeno e previsível, enquanto qualquer serviço cobrado por peça pesa mais que o próprio uso.

## Alternativas descartadas
- **Plataforma gerenciada (Fly.io, Render, Railway):** sobe com um comando, renova certificado e reinicia sozinha, e o banco gerenciado já vem com backup. O banco gerenciado custa um múltiplo do servidor inteiro, e o app nasce exposto na internet, o que obrigaria a ter login antes do tempo.
- **Nuvem grande (AWS, Google Cloud):** tem serviço pronto para cada necessidade. Para um serviço só, cobra caro pelas peças de rede e obriga a configurar permissões, balanceador e monitoramento antes de existir a primeira feature.
- **Instalar aplicação e banco direto no servidor, sem contêineres:** menos uma camada e menos memória gasta. A máquina de desenvolvimento e o servidor passam a ter versões diferentes de Java e de Postgres com o tempo, e voltar atrás numa atualização deixa de ser trocar a imagem por outra.
- **Servidor gratuito de uso contínuo:** existem ofertas permanentes sem custo. Elas recuperam a máquina quando ela fica ociosa, que é o perfil de um app de uso pessoal, e não garantem backup.

## Consequências
- **Ganhos:** custo fixo conhecido; controle total do que roda; o mesmo arranjo de contêineres roda na máquina de desenvolvimento e no servidor.
- **Custos:** atualizar o sistema operacional, acompanhar disco e memória e cuidar do backup passam a ser tarefa de quem desenvolve.
- **Passa a ser obrigatório:**
  - o fornecedor, o plano e a região ficam registrados no runbook de deploy, não aqui, porque mudam sem afetar a arquitetura;
  - o banco guarda os dados em volume nomeado, apagado só por comando explícito, nunca junto com os contêineres;
  - enquanto não houver login, o acesso é só pela rede privada, e nenhuma porta da aplicação fica aberta na internet;
  - existe backup do banco guardado fora do servidor, e a restauração é testada antes de existir dado que importe; frequência, destino e tempo de guarda ficam no runbook, com o passo a passo.
