---
status: aceito
atualizado: 2026-09-19
---
# ADR-0003: Usar Spring Boot como framework do backend

**Decisão:** usar **Spring Boot**, porque é o framework de maior domínio de quem desenvolve e já traz pronto quase tudo que o roadmap pede (acesso a banco, login, tarefas agendadas, importação em lote). Junto vai a política de versão: **usar a LTS (versão de suporte longo) mais recente do Java que o framework suporta bem e acompanhar a versão maior do framework em até um ciclo**, cerca de seis meses.

## Contexto
Decorre do [ADR-0002](0002-java-como-linguagem-do-backend.md). Um serviço só, poucos usuários, rodando num servidor com 4 GB de memória compartilhados com o banco. O sistema não tem requisito de subir em milissegundos nem de ligar e desligar sob demanda.

## Alternativas descartadas
- **Quarkus:** resolve as dependências na compilação, então sobe em cerca de 0,65s contra 1,9s, e em imagem nativa ocupa cerca de 70 MB contra 149 MB. Isso vira dinheiro quando são dezenas de serviços por máquina ou funções que ligam e desligam o tempo todo, o que não é o caso. Em troca, o catálogo de integrações é menor e o aprendizado seria novo.
- **Micronaut:** mesma ideia de resolver dependências na compilação, com tempo de subida parecido. A comunidade e o material são bem menores, o que significa mais tempo parado quando aparece um problema fora do caminho comum.

## Consequências
- **Ganhos:** biblioteca pronta para o que vier no roadmap; muito material e exemplo disponíveis, inclusive para gerar código com IA; caminho aberto para organizar módulos com Spring Modulith, se o ADR de arquitetura seguir por ali.
- **Custos:** cerca de 300 a 500 MB de memória em uso, que precisam caber no servidor junto com o banco; versão maior nova a cada seis meses para acompanhar.
- **Passa a ser obrigatório:** versão do Java e do framework fixadas no arquivo de build, que é a fonte única desses números; atualização de versão maior entra como tarefa própria, não misturada a uma feature.
