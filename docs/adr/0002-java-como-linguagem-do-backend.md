---
status: aceito
atualizado: 2026-09-19
---
# ADR-0002: Usar Java como linguagem do backend

**Decisão:** escrever o backend em **Java**, porque é a linguagem de maior domínio de quem desenvolve o projeto, o que dá velocidade e senso crítico para revisar o que for gerado com ajuda de IA, e porque ela atende a tudo que o roadmap pede.

## Contexto
O projeto é tocado por uma pessoa, com experiência forte em backend Java e pouca em frontend. O aprendizado disponível é escasso e vale mais gasto no frontend e na infraestrutura. O backend precisa de transação de banco, regra de negócio tipada, importação de arquivos e tarefas agendadas, que qualquer candidato resolve.

## Alternativas descartadas
- **Kotlin:** roda na mesma plataforma e usa as mesmas bibliotecas. Ganha nulo verificado pelo compilador (elimina uma classe inteira de erro em tempo de execução) e menos código para o mesmo resultado. Perde alcance: há menos material e menos exemplos que em Java, inclusive para gerar código com IA, e o repositório também serve de vitrine num mercado onde a vaga de Java é mais comum.
- **TypeScript com Node:** usaria uma linguagem só no projeto inteiro, evitando troca de contexto entre backend e frontend. Em troca, joga fora a experiência mais forte de quem desenvolve e enfraquece o ponto forte do código, sem ganhar nada no que este sistema precisa.

## Consequências
- **Ganhos:** velocidade e revisão crítica na parte de maior domínio; ecossistema com solução madura para tudo que o roadmap prevê.
- **Custos:** duas linguagens no projeto (com o frontend), e mais código repetitivo do que haveria em Kotlin.
- **Passa a ser obrigatório:** a versão do Java fica fixada no arquivo de build, para máquina de desenvolvimento e CI compilarem igual. A política de versão vem no ADR do framework.
