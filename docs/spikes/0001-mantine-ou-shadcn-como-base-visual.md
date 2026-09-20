---
status: ativo
atualizado: 2026-09-20
---
# Spike-0001: Mantine ou shadcn com Tailwind como base visual do frontend?

**Resposta:** Mantine. As duas chegaram ao mesmo resultado visual, mas no Mantine o ajuste ficou concentrado no tema, enquanto no shadcn ele se espalha pelos componentes copiados para dentro do projeto.

## Pergunta e critério
- **Pergunta:** qual das duas entrega as telas no padrão visual escolhido com menor custo de manutenção, para quem tem pouca experiência em frontend?
- **Prazo:** meio dia.
- **Pronto quando:** a mesma tela (registrar um gasto) estiver rodando nas duas, comparável no celular.

## O que foi feito
Dois projetos Vite com React 19, cada um com uma das bibliotecas, implementando a mesma tela a partir dos mesmos valores de cor, fonte e espaçamento. Código descartado depois da comparação.

## O que aprendemos
- **Ajuste visual:** a primeira versão em Mantine saiu com cara de biblioteca, diferente do desenho. Corrigir custou cerca de dez linhas no tema, e o efeito valeu para toda tela futura. No shadcn, o mesmo ajuste seria editar cada componente copiado em `src/components/ui`.
- **Formulário:** com o formulário do próprio Mantine, campo de seleção não precisou de invólucro. Na versão com React Hook Form, cada seleção exigiu um `Controller` (peça do React Hook Form que liga ao formulário um campo que não é o nativo do navegador).
- **Componentes prontos:** o Mantine trouxe campo de data; no shadcn o campo de data foi o nativo do navegador, porque calendário ali é mais um componente para instalar e manter.
- **JavaScript entregue:** 525 KB (Mantine) contra 452 KB (shadcn). Diferença sem efeito prático neste app.
- **Limite encontrado:** a etiqueta de categoria do Mantine traz marca de seleção embutida e não sai só com estilo, então virou um botão comum. Isso gerou a regra de quando criar componente próprio.

## Decorrência
[ADR-0006](../adr/0006-bibliotecas-base-do-frontend.md) e as três regras de customização que vão para o perfil de stack do frontend: ajuste visual no tema, componente próprio só quando a estrutura não serve, nunca copiar código da biblioteca para dentro do projeto.
