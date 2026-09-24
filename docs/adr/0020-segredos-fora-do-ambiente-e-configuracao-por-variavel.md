---
status: proposto
atualizado: 2026-09-24
---
# ADR-0020: Segredos guardados fora do ambiente e configuração por variável

**Decisão:** os segredos ficam guardados **fora do ambiente que é destruído**, no cofre de segredos do repositório, e são entregues ao servidor no momento em que ele é criado; a aplicação lê **toda** a configuração de variáveis de ambiente, sem endereço nem senha escritos no código.

## Contexto
Decorre do [ADR-0019](0019-ambiente-criado-e-destruido-sob-demanda.md): como o ambiente é destruído e recriado com frequência, qualquer segredo que more apenas nele desaparece junto. O mesmo artefato precisa rodar na máquina de desenvolvimento e no servidor, mudando só os valores.

## Alternativas descartadas
- **Arquivo de configuração mantido só no servidor:** simples e direto, e a aplicação lê sem intermediário. Ele some quando o ambiente é destruído, e recriar à mão a cada subida é o tipo de ritual que gera erro silencioso.
- **Segredos criptografados versionados no repositório:** ficam junto do código, com histórico e revisão em PR. Passa a existir uma chave que abre tudo, guardada por você em outro lugar, e vazamento dela é vazamento de todos os segredos de uma vez.
- **Gerenciador de segredos dedicado:** dá rotação, expiração e registro de quem leu o quê. É mais um serviço para subir, manter e pagar, e ele próprio precisa de uma credencial para ser acessado, o que só empurra o problema um nível.

## Consequências
- **Ganhos:** ambiente destruído não leva segredo junto; um lugar só para trocar uma senha; o mesmo artefato roda em qualquer ambiente.
- **Custos:** os segredos ficam sob a conta do repositório, e quem tiver acesso administrativo a ela alcança todos; o valor guardado não pode ser lido de volta, só substituído, então perder a cópia significa gerar outro.
- **Passa a ser obrigatório:**
  - nenhum segredo no repositório, nem em arquivo de exemplo: o exemplo traz os nomes das variáveis com valores vazios;
  - nenhum valor sensível aparece em log; como isso é garantido fica em aberto;
  - o frontend não recebe segredo: o que entra no build dele é público para quem abrir o navegador;
  - criar o ambiente inclui entregar a ele os segredos; destruir inclui não deixar cópia para trás.
