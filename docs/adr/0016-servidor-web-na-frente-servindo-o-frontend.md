---
status: aceito
atualizado: 2026-09-23
---
# ADR-0016: Servidor web na frente serve o frontend e repassa a API

**Decisão:** o frontend é servido por um **servidor web próprio (Caddy)** que também **repassa `/api` para o backend**, porque assim app e API ficam na **mesma origem**, o que elimina de uma vez a permissão entre origens diferentes, o cookie de sessão entre domínios e o escopo do service worker. Esse servidor vem dentro da imagem do frontend e é a porta de entrada do sistema.

## Contexto
Decorre do [ADR-0005](0005-frontend-spa-com-vite-e-react.md) e do [ADR-0015](0015-servidor-proprio-com-conteineres.md). O frontend é um conjunto de arquivos estáticos e o backend é um serviço separado, no mesmo servidor. Enquanto não houver login, quem cuida do HTTPS é a rede privada; o servidor web roda em HTTP puro atrás dela.

## Alternativas descartadas
- **nginx no lugar do Caddy:** faz o mesmo trabalho, gasta menos memória (cerca de 6 MB contra 28 MB) e tem vinte anos de receita publicada. O Caddy leva na configuração curta, em entregar arquivo já comprimido sem gastar processador e por não ter a pegadinha clássica de combinar raiz de arquivos com rota, que é onde configuração de SPA costuma quebrar. Quando existir domínio próprio com portas abertas, o certificado automático do Caddy soma outro ganho.
- **O próprio Spring servindo os arquivos estáticos:** uma imagem, um contêiner, um deploy, e cache global resolvido por configuração. O `dist` do frontend passaria a entrar na imagem do backend, então corrigir uma tela exigiria reconstruir e reiniciar a API, amarrando o ciclo dos dois artefatos que o [ADR-0001](0001-repositorio-unico-sem-ferramenta-de-monorepo.md) mantém separados.
- **Hospedar os arquivos fora** (Cloudflare Pages, Netlify): entrega rápida, de graça e sem carga no servidor. Se o app está na internet pública, a API precisa estar também, e aí a rede privada deixa de proteger qualquer coisa.
- **Usar o próprio recurso de publicação da rede privada** (Tailscale Serve), que serve pasta e repassa requisição sem peça nova: não faz o desvio de rota que uma SPA exige, não define cabeçalho de cache, e só publica endereço da própria rede, então não sobrevive ao lançamento público.

## Consequências
- **Ganhos:** mesma origem para app e API; desvio de rota, cabeçalho de cache e compressão resolvidos fora do código; o backend deixa de ter responsabilidade de servir arquivo.
- **Custos:** mais um contêiner e um arquivo de configuração; publicar uma correção de tela reinicia a porta de entrada, o que interrompe o acesso por cerca de um segundo.
- **Passa a ser obrigatório:**
  - o desvio para a página inicial vale só para navegação; arquivo inexistente responde 404, e não a página inicial, senão o navegador recebe HTML onde espera script;
  - `index.html`, `sw.js`, `registerSW.js` e `manifest.webmanifest` nunca entram em cache longo; só os arquivos com identificador no nome entram;
  - compressão é feita no build, e o servidor só entrega o arquivo já comprimido; resposta da API não é comprimida, por causa de ataque conhecido contra resposta comprimida sobre TLS;
  - cabeçalho de segurança é responsabilidade nossa, escrito na configuração; o HSTS (regra que obriga o navegador a usar HTTPS em toda visita futura) entra só quando existir o domínio final;
  - a interface de administração do servidor web fica desligada;
  - enquanto o acesso for por rede privada, o servidor web atende em HTTP puro e não tenta emitir certificado.
