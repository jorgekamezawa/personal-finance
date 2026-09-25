---
status: aceito
atualizado: 2026-09-24
---
# ADR-0021: Regra de código é verificada por ferramenta no build, e o CI só confere

**Decisão:** a regra de código do backend é verificada por **ferramenta que roda no build local**, e o **CI apenas confere**, sem corrigir e sem dar push, porque a falha precisa aparecer para quem está escrevendo, no comando que essa pessoa já roda, e não no PR.

São três ferramentas, cada uma com um alvo:
- **Teste de arquitetura** (ArchUnit): lê o código já compilado e vive como teste comum na suíte. Duas regras: o núcleo (domínio e tipos compartilhados) não depende de framework, que é o que o [ADR-0011](0011-monolito-modular-com-hexagonal.md) manda verificar, e nenhuma classe constrói dinheiro a partir de `double`.
- **Formatador** (Spotless com palantir-java-format): estilo fixo, que a ferramenta impõe e não se configura; os valores estão registrados no perfil de stack do backend. Um comando arruma, outro só confere.
- **Linter de defeito** (Error Prone): roda dentro da compilação. Comparar dinheiro com `equals` quebra a compilação, e construir dinheiro a partir de um número com vírgula escrito no código também; os outros achados dele saem conforme a severidade que cada um já tem. O caso em que o valor vem de variável escapa dele, e é por isso que a mesma proibição aparece como regra de arquitetura.

## Contexto
O [ADR-0011](0011-monolito-modular-com-hexagonal.md) exigiu que o domínio sem framework fosse garantido por teste que quebra o build, e deixou a ferramenta em aberto. Quem desenvolve trabalha sozinho, sem segundo par de olhos na revisão, e parte do código nasce de geração automática, que formata de um jeito diferente a cada vez. Erro de dinheiro é o mais caro deste sistema ([ADR-0009](0009-dinheiro-em-decimal-exato.md)), e até aqui a regra dele só existia escrita.

## Alternativas descartadas
- **Varredura de texto no CI, dentro do script de convenções que já existe:** não custa dependência nova, e tem dois furos. Lê linha de `import`, então escapa anotação escrita com nome completo no meio do código, e quem quebra a regra só descobre no PR, porque na máquina o teste segue verde.
- **Formatador do Google:** é o mais difundido e o melhor integrado a editor. Seu estilo é fixo em 2 espaços e 100 colunas e não se configura, então o primeiro uso reescreveria todo arquivo existente e afastaria o código do padrão de 4 espaços que o Java usa desde sempre.
- **Checkstyle ou PMD como linter:** já vêm embutidos na ferramenta de build, sem plugin novo. O forte dos dois é reclamar de estilo, que o formatador já resolve sozinho, e ambos exigem um arquivo de regras próprio para manter; sobraria a menor fatia do que falta, pelo maior trabalho de configuração.
- **CI que corrige o formato e comita por conta própria:** pouparia um comando de quem escreve. Exigiria dar permissão de escrita no repositório para o fluxo automático, ou seja, uma superfície de segurança nova em troca de conveniência.
- **Tratar todo aviso do compilador como erro:** parece o portão mais rígido, e é rígido no lugar errado. Ele conta avisos e transforma a contagem em falha, então uma biblioteca que depreciou um método barra o build sem existir erro nenhum no código escrito.

## Consequências
- **Ganhos:** a violação aparece no comando que quem escreve já roda, antes do PR; o diff de revisão mostra só o que mudou de verdade, sem linha remexida por formatação; a regra de dinheiro deixa de depender de alguém lembrar dela.
- **Custos:** quatro dependências novas no build, com o tempo de execução delas somado a cada compilação; o formatador impõe um estilo que ninguém escolhe caso a caso; aviso de compilador passa a sair no log sem barrar nada, então depende de alguém ler.
- **Passa a ser obrigatório:**
  - Rodar o formatador antes de mostrar código para validação; o commit é barrado quando o formato está fora, e o CI confere sem nunca corrigir.
  - O teste de arquitetura vive na suíte comum, não em tarefa separada nem em subprojeto.
  - Ferramenta nova só entra como porteiro do build depois de registrada aqui.
  - Número de versão de cada ferramenta vive no arquivo de build, nunca neste documento.
