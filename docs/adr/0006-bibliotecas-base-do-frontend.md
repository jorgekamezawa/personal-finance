---
status: aceito
atualizado: 2026-09-19
---
# ADR-0006: Bibliotecas base do frontend

**Decisão:** usar **Mantine** (componentes visuais), **React Router v8 em modo de dados** (a própria rota declara como carregar e enviar dados, sem código de busca espalhado pelas telas), **TanStack Query** (dados vindos da API) e **`@mantine/form` com Zod** (formulário e validação), sem Tailwind. O critério foi ter o máximo pronto e integrado entre si, porque quem desenvolve tem pouca base em frontend e cada peça solta vira decisão de design ou cola entre bibliotecas.

## Contexto
Decorre do [ADR-0005](0005-frontend-spa-com-vite-e-react.md) e da comparação medida no [Spike-0001](../spikes/0001-mantine-ou-shadcn-como-base-visual.md). As telas são formulários rápidos no celular, listas com filtro e um resumo mensal. Trocar essas bibliotecas depois significa mexer em todas as telas, por isso a escolha é registrada aqui, enquanto as regras de uso no dia a dia ficam no perfil de stack do frontend.

## Alternativas descartadas
- **MUI no lugar do Mantine:** é a maior biblioteca do ecossistema, com cerca de quatro vezes mais downloads, o que significa mais exemplos e mais material quando algo dá errado. Em troca, o visual Material deixa todo app com a mesma cara, customizar é mais trabalhoso, e formulário, datas e gráficos vêm de pacotes separados. O Mantine entrega esses quatro no mesmo pacote e sobe de versão numa linha só.
- **shadcn/ui com Tailwind:** o código dos componentes é copiado para dentro do projeto, o que dá controle total e agrada quem gera código com IA. A correção feita na origem não chega sozinha: existe comando para comparar, mas a junção é manual, e o conjunto assume que quem usa tem critério de design para montar as telas.
- **React Hook Form no lugar do `@mantine/form`:** é o padrão de mercado e ganha em formulário grande com muitos campos. Os campos do Mantine são controlados (o valor vive no estado do React, não no próprio campo da tela), então cada um exigiria um invólucro extra, que é onde código gerado por IA erra em silêncio (campo que não valida, valor que não chega).

## Consequências
- **Ganhos:** componentes, formulário, datas, notificações e gráficos vindos de um pacote só; atualização por gerenciador de pacotes; menos decisões de design no caminho.
- **Custos:** menos material disponível que MUI; acessibilidade do Mantine tem falhas abertas, então tela crítica precisa de conferência manual; a validação do formulário é experiência de uso, e a regra que vale continua sendo a do backend.
- **Passa a ser obrigatório:** cor, tamanho e canto saem do sistema visual e entram no tema do Mantine, nunca direto na tela; versões fixadas no projeto, porque o React Router v8 removeu o pacote `react-router-dom` e quase todo exemplo antigo (inclusive gerado por IA) não compila; estilo pontual sai das propriedades do Mantine ou de CSS Modules, nunca de `style` no meio do JSX; nenhuma biblioteca de estado global entra sem necessidade demonstrada.
