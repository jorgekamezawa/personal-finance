---
status: aceito
atualizado: 2026-09-20
---
# ADR-0009: Representar dinheiro em decimal exato

**Decisão:** dinheiro é **decimal exato** do banco à API (coluna `numeric(15,2)`, `BigDecimal` no Java, texto decimal no JSON), arredondado só quando o número vira dinheiro, no modo **metade para o par** (a fração exata de meio centavo vai para o dígito par mais próximo).

## Contexto
Decorre do [ADR-0008](0008-postgresql-com-flyway.md). O produto soma centenas de lançamentos por mês e compara meses entre si, então viés de arredondamento aparece no resultado. Compra parcelada divide um total em partes, e a soma das partes precisa bater com o total.

## Alternativas descartadas
- **Centavos em número inteiro:** impossível perder centavo, e somar no navegador fica seguro. Em troca, toda leitura e escrita converte, e esquecer uma divisão por cem gera erro de cem vezes; no relatório, a divisão se espalha pelas consultas.
- **Ponto flutuante (`double`):** é o caminho fácil quando o valor vem de JSON, e erra em silêncio. O erro aparece só no total do mês, quando já não dá para saber qual lançamento o causou.
- **Arredondar sempre para cima na metade:** é o modo mais conhecido e cria viés sistemático para cima; num relatório com centenas de somas, o total fica maior que a realidade. O modo metade para o par é também a regra da norma brasileira de arredondamento.

## Consequências
- **Ganhos:** soma e média corretas sem conversão; um formato só atravessando banco, backend e API.
- **Custos:** em Java, comparar valores exige `compareTo` e não `equals`; toda divisão precisa declarar o arredondamento.
- **Passa a ser obrigatório:**
  - arredondar só na fronteira em que o número vira dinheiro, no modo metade para o par;
  - dividir um total em parcelas é rateio, não arredondamento: um teste garante que a soma das parcelas é igual ao total, e em qual parcela a sobra de centavos cai é regra de negócio, que vive na spec;
  - a API entrega dinheiro como texto decimal; `R$ 128,90` só existe na tela.
