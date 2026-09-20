---
status: aceito
atualizado: 2026-09-19
---
# ADR-0005: Construir o frontend como SPA com Vite e React

**Decisão:** construir o frontend como **SPA (aplicação de página única, que baixa o JavaScript uma vez e monta as telas no navegador)** com **Vite e React**, porque o produto é privado e não precisa aparecer em buscadores, então renderizar telas no servidor só acrescentaria um processo Node em produção ao lado do backend Java. O build gera arquivos estáticos, servidos por um servidor web comum.

## Contexto
O produto é privado, atrás de login, então não precisa aparecer em buscadores. O backend já é um serviço Java ([ADR-0003](0003-spring-boot-como-framework-do-backend.md)) e tudo roda num servidor com 4 GB de memória. Quem desenvolve tem pouca base em frontend, então caminho comum e material abundante valem mais que elegância técnica.

## Alternativas descartadas
- **Next.js:** renderiza as telas no servidor, o que ajuda buscadores e a velocidade da primeira tela exibida. Exigiria um processo Node em produção junto do Java e abriria a porta para regra de negócio migrar para o lado Node, competindo com o backend. Os ganhos dele dependem de SEO, que um app atrás de login não tem.
- **TanStack Start:** também usa Vite, com rotas e dados tipados ponta a ponta e melhor desempenho em teste de carga. O ecossistema é jovem, com menos material e menos exemplos, o que pesa justamente para quem tem pouca base no assunto.

## Consequências
- **Ganhos:** um artefato estático, sem servidor de aplicação no frontend; ferramental padrão, com material farto; caminho direto para o app instalável no celular.
- **Custos:** a primeira abertura baixa mais JavaScript que uma página renderizada no servidor; a tela inicial em branco precisa de cuidado; nenhuma página é indexável, o que exigiria repensar a base se um dia houver parte pública.
- **Passa a ser obrigatório:** o frontend fala com o backend só por API; nenhuma regra de negócio vive no frontend; o servidor web entrega os arquivos estáticos e redireciona rotas desconhecidas para a página inicial da SPA.
