---
status: aceito
atualizado: 2026-09-20
---
# ADR-0007: Entregar o app como PWA instalável, com aviso de nova versão

**Decisão:** entregar o frontend como **PWA (site que o celular instala pelo ícone e abre em tela cheia)**, com **service worker** (programa que o navegador mantém em segundo plano) guardando só o casco do app (os arquivos da interface, sem nenhum dado) e avisando quando há versão nova, para o usuário recarregar quando quiser.

## Contexto
Decorre do [ADR-0005](0005-frontend-spa-com-vite-e-react.md). O uso principal é registrar gasto no celular, logo após a compra, e o objetivo de fazer isso em menos de 30 segundos vem da [visão do produto](../product/vision.md). Não há requisito de funcionar sem internet, e os dados são financeiros.

## Alternativas descartadas
- **Atualização silenciosa:** o app trocaria de versão sozinho, sem ninguém ficar para trás. Como a troca recarrega a página, ela pode apagar o formulário em preenchimento, justamente no momento mais usado do app.
- **Só ícone e nome, sem service worker:** configuração mínima, e no iPhone a instalação continuaria funcionando. No Android o navegador normalmente não oferece instalar sem service worker, e cada abertura baixaria tudo de novo.

## Consequências
- **Ganhos:** abre pelo ícone, em tela cheia, sem passar por loja de aplicativos; abertura rápida, porque o casco do app fica no aparelho; quem está usando decide quando atualizar.
- **Custos:** mais uma peça para configurar e entender; configuração errada entrega versão velha ou guarda dado que não deveria.
- **Passa a ser obrigatório:**
  - nenhuma resposta da API é guardada em cache: o que fica no aparelho é só HTML, JavaScript, CSS e ícones;
  - sem internet, o app abre e avisa que precisa de conexão, em vez de mostrar número desatualizado;
  - o cache dos arquivos do casco é responsabilidade do servidor web, e as regras estão no [ADR-0016](0016-servidor-web-na-frente-servindo-o-frontend.md); sem elas, o deploy deixa o app preso na versão antiga.
