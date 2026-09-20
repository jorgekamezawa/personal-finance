---
status: aceito
atualizado: 2026-09-19
---
# ADR-0004: Usar Gradle como ferramenta de build do backend

**Decisão:** usar **Gradle**, com a configuração escrita em Kotlin, porque ele refaz só o que mudou e guarda cache, o que encurta o ciclo de recompilar e rodar teste, que é o ciclo do dia a dia.

## Contexto
Decorre do [ADR-0002](0002-java-como-linguagem-do-backend.md). O trabalho acontece em fatias pequenas, com teste rodando a cada mudança, então o tempo que importa é o da recompilação, não o do build limpo.

## Alternativas descartadas
- **Maven:** configuração declarativa em XML, previsível e legível por qualquer pessoa de Java, com convenção rígida que evita invenção. Perde no ciclo curto, porque não tem build incremental com cache, e customizar tarefa exige plugin e muito XML.
- **Bazel:** build incremental e reprodutível com cache distribuído, feito para repositórios gigantes com muitas linguagens. Aqui exigiria configuração própria para cada linguagem num projeto de duas pastas, desproporcional ao problema.

## Consequências
- **Ganhos:** recompilação e teste mais rápidos; autocompletar e erro em tempo de compilação no arquivo de build, por causa do Kotlin.
- **Custos:** o arquivo de build é código e pode virar bagunça se receber lógica demais; mais conceitos para quem só conhece Maven.
- **Passa a ser obrigatório:** o wrapper do Gradle fica versionado, para a máquina de desenvolvimento e o CI usarem a mesma versão; o arquivo de build guarda configuração, não lógica de aplicação.
