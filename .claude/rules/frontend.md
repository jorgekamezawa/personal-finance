---
paths:
  - "frontend/**"
---

# Convenções do frontend

## Visual
- A fonte do visual é o **Sistema visual**: https://claude.ai/artifact/D41TuG5ziw6nMii3tKNnCw. Lá moram cores, tipografia, espaçamentos e cantos, com a explicação de uso de cada um.
- Mudança visual **nasce no Sistema visual** e depois é aplicada em `src/theme.ts`. Nunca o contrário, e nunca direto na tela.
- Cor, tamanho e canto saem do tema. Nada de valor solto no componente.
- Ajuste que valha para todas as telas vai no tema, não no componente ([ADR-0006](../../docs/adr/0006-bibliotecas-base-do-frontend.md)).
- Componente próprio só quando a estrutura do componente da biblioteca não serve; ele vive em `src/components/` com nome de domínio. Nunca copiar código da biblioteca para dentro do projeto.
- Estilo pontual usa as propriedades do Mantine ou CSS Modules, nunca `style` solto no meio do JSX.

## Dados e estado
- Dado vindo da API passa por uma função em `src/api.ts` (ou módulo equivalente por assunto), nunca `fetch` espalhado na tela.
- Filtro, mês selecionado e afins moram na **URL**, não em estado global: link compartilhável, botão voltar correto e cache com chave natural.
- Depois de gravar, invalidar o cache da consulta afetada; senão a tela mostra o número velho.
- Nenhuma regra de negócio no frontend: a validação daqui é experiência de uso, a que vale é a do backend.

## Comentário e idioma
- Código, identificador e comentário em inglês; texto que aparece na tela fica em português.
- Comentário explica **por que**, nunca o que o código já diz, e não cita número de ADR.

## Qualidade
- `npm run typecheck`, `npm run lint` (com regras de acessibilidade) e `npm test` passam antes do PR; o build também roda no CI.
- Teste de componente exercita a tela como o usuário faz (preencher, enviar, ler o que aparece), com a API simulada.
- Arquivo exporta componente **ou** utilidades, não os dois, para o recarregamento rápido funcionar.

## Versões
- Node 24 (LTS atual) e as versões fixadas em `package.json`.
- O React Router v8 removeu o pacote `react-router-dom`: exemplo antigo, inclusive gerado por IA, não compila. Confira a versão antes de copiar código.
