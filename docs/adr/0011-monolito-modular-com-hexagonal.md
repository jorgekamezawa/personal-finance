---
status: aceito
atualizado: 2026-09-20
---
# ADR-0011: Monolito modular com hexagonal em todos os módulos

**Decisão:** organizar o backend como **monolito modular**, um módulo por capacidade do negócio (lançamento, meio de pagamento, categoria, membro, relatório, importação), com **arquitetura hexagonal em todos eles**: domínio sem framework, casos de uso declarando as portas de que precisam, e adaptadores de entrada e saída. A única regra verificada por teste que quebra o build é o domínio não depender de framework.

## Contexto
O backend é um serviço só ([ADR-0003](0003-spring-boot-como-framework-do-backend.md)), com regras que erram dinheiro se estiverem erradas: mês de referência, rateio de parcelas e resumo mensal. Os módulos ainda vão mudar de forma nas primeiras features, e quem desenvolve trabalha sozinho, então o custo de uma regra automática errada é maior que o risco que ela evita.

## Alternativas descartadas
- **Camadas clássicas (controller, service, repository):** menos arquivos e leitura imediata. Com o tempo o serviço vira depósito de regra misturada com acesso a banco, e testar a regra do mês de referência passa a exigir subir Spring e banco, trocando segundos por minutos a cada rodada.
- **Hexagonal só nos módulos com regra, camadas no CRUD:** é a recomendação comum do DDD (desenho orientado ao domínio), investir modelagem no domínio principal e manter o apoio simples. Descartada porque dois estilos exigem decidir o estilo de cada módulo novo, e a consistência vale mais aqui do que os arquivos economizados num cadastro.
- **Módulo reagindo a fato consumado por chamada direta, em vez de evento:** é mais fácil de seguir no código, porque o caminho aparece inteiro. Cria dependência de quem publica para quem reage (e ciclo, quando os dois precisam um do outro), e coloca o trabalho do vizinho dentro da mesma transação: se atualizar o resumo falhar, o lançamento não é gravado.
- **Nenhum núcleo compartilhado, cada módulo dono dos próprios tipos de valor:** deixa os módulos totalmente independentes. Dinheiro e mês de referência são vocabulário do produto inteiro, então a cópia em cada módulo obriga a traduzir em toda fronteira e faz a mesma regra existir em quatro lugares.
- **Verificação completa de módulos barrando o build** (ciclos e acesso a pacote interno): pega invasão entre módulos cedo. Como porteiro do CI, engessa o refatoramento numa fase em que os módulos ainda estão mudando de forma; fica como comando rodado sob demanda.

## Consequências
- **Ganhos:** regra testável sem subir Spring nem banco; um só jeito de organizar código; troca de banco ou de framework atinge adaptador, não domínio.
- **Custos:** cadastro simples ganha mais arquivos do que precisaria; a fronteira entre módulos depende de revisão, não de teste.
- **Passa a ser obrigatório:**
  - **Pastas do módulo:** `api/` (o que o vizinho pode importar), `domain/`, `application/` com as portas, `adapter/in` e `adapter/out`.
  - **A porta pertence a quem consome.** O módulo que precisa declara a interface na linguagem dele; o adaptador de saída traduz e chama a `api/` do vizinho. Nenhum módulo usa repositório, entidade de banco ou tabela de outro.
  - **Reação a fato consumado usa evento de domínio.** Quem publica não conhece quem escuta; o ouvinte roda depois que a transação confirma.
  - **Núcleo compartilhado mínimo** em `shared/tipo`: só tipo de valor (dinheiro, mês de referência, identificador), sem framework, e só entra o que dois ou mais módulos usam e que não tem módulo dono. Regra de negócio de um módulo nunca sobe para lá.
  - **Domínio sem anotação de framework**, garantido por teste que quebra o build.
  - Quando a forma dos módulos estabilizar, reavaliar se a verificação completa entra no CI.
