---
status: aceito
atualizado: 2026-09-23
---
# ADR-0013: Teste de regra roda sem infraestrutura

**Decisão:** teste de domínio e de caso de uso roda **sem infraestrutura**, ou seja, sem carregar Spring, sem banco e sem rede, porque é isso que dá retorno em milissegundos e sustenta o ciclo de escrever teste, ver falhar e corrigir.

## Contexto
Decorre do [ADR-0011](0011-monolito-modular-com-hexagonal.md), que isolou o domínio do framework. Esse isolamento só se paga se o teste de regra de fato rodar sem subir nada; caso contrário, a estrutura extra de portas e adaptadores fica sem contrapartida.

## Alternativas descartadas
- **Carregar o framework nos testes de regra, por comodidade:** evita escrever a montagem dos objetos no teste, porque o framework injeta tudo. Cada classe de teste passa a custar segundos em vez de milissegundos, e o domínio acaba amarrado ao framework por baixo dos panos, desfazendo o motivo do [ADR-0011](0011-monolito-modular-com-hexagonal.md).
- **Testar regra só através da API, subindo a aplicação:** garante que o caminho inteiro funciona. A falha passa a apontar para a ponta, e não para a regra errada, e cada combinação de caso de borda custa uma requisição completa, o que torna caro testar as muitas faixas de fechamento de fatura e arredondamento.

## Consequências
- **Ganhos:** retorno imediato ao mexer em regra; o teste vira ferramenta de escrita, não etapa final.
- **Custos:** o teste monta os objetos na mão, então mudança de construtor aparece em vários testes; parte da montagem precisa de construtores de teste bem feitos.
- **Passa a ser obrigatório:** nenhum teste de domínio ou de caso de uso carrega o framework; como as dependências externas são substituídas nesses testes é convenção, e vive no perfil de stack.
