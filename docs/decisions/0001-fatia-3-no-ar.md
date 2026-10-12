---
status: registrado
atualizado: 2026-10-12
---
# Registro-0001: Fatia 3, colocar o sistema no ar

**Cobre:** as decisões de infraestrutura e de CI (as máquinas do GitHub que rodam os fluxos do projeto) tomadas entre 2026-09-25 e 2026-10-12 para a terceira fatia do esqueleto, que põe o sistema num servidor. Preços e medições valem para a data de cada entrada.

O que virou ADR (registro de decisão de arquitetura) está linkado; aqui ficam os números, os fornecedores e o caminho.

## Decisões

### 1. Como o sistema fica fora da internet pública (2026-09-25)
| Opção | Custo e limites | Contra |
|---|---|---|
| **Tailscale** (rede privada entre as máquinas, sem porta aberta) | Grátis: até 6 usuários, 1.000 minutos por mês de máquina descartável | Depende de um terceiro para abrir conexão nova |
| Cloudflare Tunnel com Access | Grátis até 50 usuários | Exige domínio próprio já; o sistema fica alcançável pela internet, atrás de login |
| WireGuard configurado à mão | Grátis | O endereço do servidor muda a cada criação, e a configuração teria de ser refeita a cada subida |
| Firewall liberando SSH (acesso remoto por linha de comando) só para um IP | Grátis | O CI roda em faixas de endereço enormes e rotativas: liberar o CI é abrir para quase todos |

- **Escolha:** Tailscale.
- **Motivo:** é a única que dá nome fixo ao servidor sem endereço fixo e deixa o CI entrar sem abrir porta, as duas coisas que o [ADR-0019](../adr/0019-ambiente-criado-e-destruido-sob-demanda.md) e o [ADR-0017](../adr/0017-publicacao-automatica-e-deploy-disparado-a-mao.md) pressupõem.
- **Fonte:** [planos do Tailscale](https://tailscale.com/pricing), [máquinas descartáveis](https://tailscale.com/kb/1111/ephemeral-nodes).

### 2. Em qual máquina o ambiente é criado e destruído (2026-10-10)
Máquina de 4 GB de memória, preço do mês inteiro ligada. Latência (tempo de ida e volta de uma chamada) medida da máquina de desenvolvimento, no Brasil, em duas rodadas com 1 a 3 ms de variação.

| Opção | Mês | Hora | Latência |
|---|---|---|---|
| **Hetzner CX23, Alemanha ou Finlândia** | €5,99 com IPv4 | €0,0088 | 239 a 245 ms |
| Vultr, Santiago | US$ 20 | US$ 0,027 | 55 ms |
| Vultr, Miami ou Nova Jersey | US$ 20 | US$ 0,027 | 131 a 139 ms |
| AWS Lightsail, São Paulo | US$ 24 | não confirmado | cerca de 30 ms, por outro método |
| DigitalOcean, EUA | US$ 24 | US$ 0,036 | não medida |
| Vultr, São Paulo | US$ 30 | US$ 0,041 | 9 ms |
| Hetzner CPX21, EUA | €31,99 | €0,051 | 120 ms |

- **Critério:** preço antes de latência. Quem mantém o projeto avaliou que 240 ms não são perceptíveis no uso e que o preço pesa primeiro se o ambiente passar a ficar mais tempo ligado. Se a latência virar gargalo, a decisão é revista.
- **Escolha:** Hetzner, com uma **escada de quatro degraus**, cada um tentado em Falkenstein, Nuremberg e Helsinque. Um script consulta o estoque antes de criar e pega o primeiro degrau disponível.

| Degrau | Memória | Mês | Estoque em 2026-10-05 |
|---|---|---|---|
| CX23 | 4 GB | €5,99 | some e volta, em janelas de cerca de 1 h |
| CX33 | 8 GB | €8,99 | esgotado nas três cidades |
| CPX12 | 2 GB | €11,99 | disponível |
| CPX22 | 4 GB | €19,99 | disponível |

- **Motivo da escada:** a linha barata da Hetzner fica sem estoque desde setembro, e um ambiente recriado sob demanda poderia não subir. A cobrança é por hora, então cair no degrau caro por uma tarde custa centavos.
- **Descartado, Vultr como degrau:** economizaria cerca de US$ 4 por mês no pior caso, e exigiria duas contas, duas credenciais e o código de infraestrutura escrito duas vezes.
- **Descartado por ora, linha ARM (arquitetura de processador diferente do x86, a dos servidores comuns):** 4 GB por €6,49 e 8 GB por €10,99, com estoque. O CI teria de construir cada imagem para duas arquiteturas. Entra só se o CX23 faltar com frequência.
- **Não confirmado:** o estoque do dia (a consulta exige credencial); que 2 GB bastam no degrau CPX12; se a Lightsail cobra por hora.
- **Fonte:** [tabela de preços da Hetzner de 2026-06-15](https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/), [linha econômica](https://www.hetzner.com/cloud/cost-optimized/), API pública da Vultr (`api.vultr.com/v2/plans`), [Lightsail](https://aws.amazon.com/lightsail/pricing/), [DigitalOcean](https://www.digitalocean.com/pricing/droplets), [rastreador de estoque](https://hetzner.thegoated.dev/), relatos de falta: [Vincent Schmalbach](https://www.vincentschmalbach.com/hetzner-cheap-cloud-unavailable-price-increases/) e [stackvaluelab](https://stackvaluelab.com/hetzner-cx-cax-unavailable/).

### 3. Em que ferramenta fica o código que cria e destrói o ambiente (2026-10-10)
- **Escolha:** Terraform (ferramenta que cria e destrói a infraestrutura a partir de arquivos de texto). Opções, descartes e consequências estão no [ADR-0022](../adr/0022-terraform-descreve-a-infraestrutura.md).
- **Número que o ADR não carrega:** o plugin da Hetzner estava na versão 1.70.0, de 2026-10-05, publicado pela própria Hetzner.
- **Fora da lista:** Ansible, porque configura o que roda dentro de uma máquina já criada, não cria a máquina.
- **Fonte:** [plugin hcloud](https://registry.terraform.io/providers/hetznercloud/hcloud), [Pulumi hcloud](https://www.pulumi.com/registry/packages/hcloud/).

### 4. Onde moram a cópia do banco e o arquivo de estado do Terraform (2026-10-10)
O banco pesa megabytes, então todas as opções cabem em qualquer plano.

| Opção | Custo neste tamanho | Contra |
|---|---|---|
| **Cloudflare R2** | Grátis até 10 GB, sem taxa para baixar | Mais uma conta; o estado do Terraform só é testado oficialmente na Amazon |
| Backblaze B2 | Grátis até 10 GB; baixar é grátis até 3 vezes o armazenado | Mesma ressalva; trava contra exclusão não confirmada na fonte |
| Amazon S3 | Centavos por mês, sem faixa grátis permanente | Cobra por baixar; conta com mais risco de gasto inesperado |
| Hetzner Object Storage | Taxa mensal enquanto existir um bucket (pasta de armazenamento), mesmo vazio | Mesmo provedor do servidor, o que o ADR-0019 proíbe |

- **Escolha:** Cloudflare R2, com a cópia do banco e o arquivo de estado (registro do que o Terraform criou) em buckets separados.
- **Motivo:** é o único com custo zero confirmado para guardar e para restaurar, e a restauração roda a cada subida.
- **Proteção da cópia:** as três barreiras do [ADR-0023](../adr/0023-destruir-o-ambiente-nao-alcanca-a-copia-do-banco.md).
- **Não confirmado:** se a trava do Terraform contra duas execuções ao mesmo tempo funciona no R2.
- **Fonte:** [preços do R2](https://developers.cloudflare.com/r2/pricing/), [trava de bucket do R2](https://developers.cloudflare.com/r2/buckets/bucket-locks/), [preços do B2](https://www.backblaze.com/cloud-storage/pricing), [Hetzner Object Storage](https://www.hetzner.com/storage/object-storage/), [estado do Terraform em S3](https://developer.hashicorp.com/terraform/language/backend/s3).

### 5. Onde as imagens ficam publicadas (2026-10-12)
| Opção | Custo e limites | Contra |
|---|---|---|
| **GHCR** (registro de imagens do próprio GitHub) | Grátis para pacote público; o CI publica com a credencial que o GitHub já entrega | O preço é descrito como "atualmente grátis", com um mês de aviso antes de mudar |
| Docker Hub | Grátis com 1 repositório privado e 200 baixadas a cada 6 horas | Conta nova e segredo novo no GitHub |
| Amazon ECR | Cobrado por GB | Conta AWS e credencial que expira em 12 horas |

- **Escolha:** GHCR, com imagens **públicas**.
- **Motivo:** é a única sem conta nova e sem segredo novo para publicar.
- **Por que pública:** o repositório já é público e, pelo [ADR-0020](../adr/0020-segredos-fora-do-ambiente-e-configuracao-por-variavel.md), nenhum segredo entra na imagem. Privada custaria um token gravado no servidor a cada subida, com limite de 500 MB e 1 GB de tráfego por mês, para esconder o que o código já mostra.
- **Custo aceito:** imagem pública não perdoa segredo copiado para dentro dela por engano. Os arquivos `.dockerignore` controlam o que entra.
- **Quando rever:** se o repositório virar privado, as imagens viram privadas junto.
- **Fonte:** [cobrança do GitHub Packages](https://docs.github.com/en/billing/concepts/product-billing/github-packages), [limites do Docker Hub](https://docs.docker.com/docker-hub/usage/).

### 6. O que o CI executa no servidor para implantar (2026-10-12)
| Opção | Como funciona | Contra |
|---|---|---|
| **SSH e Docker Compose** (ferramenta que sobe vários contêineres a partir de um arquivo) | O CI entra, envia o arquivo de produção e manda baixar as imagens da versão pedida e subir | O roteiro é um script do projeto, a manter |
| Ansible | Uma receita descreve o estado desejado do servidor | Ferramenta e linguagem novas para subir três contêineres numa máquina |
| Executor do GitHub dentro do servidor | O próprio servidor busca e roda os passos | Teria de se recadastrar a cada criação; desaconselhado em repositório público |

- **Escolha:** SSH e Docker Compose.
- **Motivo:** é a única que não acrescenta ferramenta, para um problema do tamanho de três comandos.

### 7. Com que credencial o CI entra na rede privada (2026-10-12)
| Opção | O que fica guardado no GitHub | Contra |
|---|---|---|
| **Identidade federada** (o GitHub prova ao Tailscale de qual repositório vem a execução) | Nenhum segredo | Configuração inicial mais longa; ainda não testada aqui |
| Cliente OAuth (credencial de aplicação, com identificador e segredo) | Um identificador e um segredo de longa duração | Quem obtiver o segredo entra na rede até ser revogado |
| Chave de acesso | Uma chave que vence | Trocada à mão; esquecer quebra o deploy |

- **Escolha:** identidade federada, com cliente OAuth como reserva se a configuração travar. O login na máquina usa o SSH do Tailscale, em que a regra "o CI entra no servidor" fica na política da rede, sem chave guardada.
- **Motivo:** elimina o segredo que dá acesso direto à rede.
- **Regras que vêm junto:** o CI entra só como o usuário da aplicação, nunca como administrador, e um passo do fluxo falha se o acesso de administrador funcionar. A política da rede fica escrita no Terraform.
- **Condição:** o SSH do Tailscale entre máquinas etiquetadas só é seguro se a origem roda código confiável. O deploy é disparado à mão, na `main`, nunca por PR de terceiro.
- **Segredos que continuam existindo:** token da Hetzner, token da Cloudflare, chaves do R2 para o estado, credencial do Tailscale para o Terraform, chaves do R2 para a cópia do banco.
- **Não confirmado:** se a credencial do Tailscale usada pelo Terraform também pode ser federada.
- **Fonte:** [ação do Tailscale para o GitHub](https://tailscale.com/kb/1276/tailscale-github-action), [SSH do Tailscale](https://tailscale.com/kb/1193/tailscale-ssh).

### 8. Como o CI publica as imagens (2026-10-12)
| Ponto | Escolha | Motivo | Descartado |
|---|---|---|---|
| Onde fica | Job `images` no `ci.yml`, depois dos quatro jobs da suíte | A receita de construção existe num lugar só | Arquivo separado, que repetiria a receita, já que ela também roda no PR |
| Etiqueta | Só o identificador completo do commit | Etiqueta que se move pode implantar a versão antiga sem avisar | `latest` |
| Como constrói | Ações oficiais da Docker, com cache (reaproveitamento entre execuções) | A construção roda em todo PR, então o tempo pesa | `docker build` direto, sem cache |
| No PR | Constrói sem publicar; na `main`, constrói de novo e publica | Dockerfile quebrado aparece antes do merge | Construir só na `main` |
| Arquitetura | Só x86 | Coerente com a escada sem ARM | Duas arquiteturas |
| Permissão de escrita em pacotes | Só neste job | O resto do arquivo continua só leitura | No arquivo inteiro |

- **Por que construir duas vezes:** o merge cria um commit novo na `main`, com outro identificador, e o conteúdo pode diferir do PR se outra mudança entrou antes.
- **Custo medido:** o PR foi de 1 min 20 s a 1 min 38 s (5 execuções) para 3 min 33 s (1 execução, sem cache). Os minutos são gratuitos em repositório público.

| Imagem | Local, sem cache | CI sem cache | CI com cache |
|---|---|---|---|
| backend | 142 s, 548 MB | 2 min 36 s e 1 min 57 s | 26 s e 23 s |
| frontend | 19 s, 93,5 MB | 38 s e 53 s | 21 s e 17 s |

- **Observado:** as imagens nasceram públicas, sem ação manual. As duas respondem sem credencial pela etiqueta do commit.

### 9. Ajustes no CI depois de uma revisão independente (2026-10-12)
| Ajuste | Antes | Depois | Motivo |
|---|---|---|---|
| Versão das ações | `checkout` v4, `setup-java` v4, `setup-node` v4 | v7, v6, v7 | Aviso de Node 20 depreciado em toda execução |
| Limite de tempo | 6 horas, o padrão | 10 minutos por job | Um passo travado seguraria a verificação |
| Verificações obrigatórias para merge | `docs`, `code`, `backend`, `frontend` | As quatro, mais `images (backend)` e `images (frontend)` | O merge era liberado cerca de 2 min 30 s antes de a imagem terminar |

- **Avaliado e mantido:** a suíte roda de novo na `main` (cerca de 1 minuto), porque é o portão do ADR-0017.
- **Cache do GitHub, como funciona:** um depósito por repositório; uma execução de PR lê o próprio cache e o da `main`, e a `main` não lê o de PR. Uso medido: 2,4 GB.
- **Efeito colateral:** a `setup-java` v6 guarda o Gradle em dois pacotes, e o pacote antigo de 278 MB deixou de servir. O job de backend foi de 50 a 57 s para 1 min 40 s e 1 min 47 s nas duas primeiras execuções.
- **Fonte:** notas de versão de cada ação e API do repositório. O prazo de 7 dias sem leitura e o limite de 10 GB do cache vêm da documentação do GitHub Actions, não reconferida nesta data.

### 10. Como se escolhe a versão a implantar e como se volta atrás (2026-10-12)
Combinado para o fluxo de deploy, ainda não implementado.

- **Disparo:** só por botão, nunca automático no merge.
- **Campo de versão vazio:** implanta o último commit da `main`. Se a imagem dele ainda não existe, o fluxo espera ou falha dizendo por quê.
- **Versão informada:** aceita o começo do identificador (7 caracteres ou mais) e completa. Trecho ambíguo ou inexistente para antes de tocar no servidor.
- **Proteção:** o fluxo confere que as duas imagens existem. O repositório só aceita squash (cada PR vira um commit só), então todo commit da `main` tem imagem.
- **Voltar atrás:** disparar de novo com a versão anterior, que o resumo do fluxo informa ("implantado X; antes estava Y").
- **Limite:** voltar a imagem não desfaz mudança no banco. A proposta é o deploy copiar o banco antes de qualquer mudança.

### 11. Onde cada decisão fica registrada (2026-10-12)
- **ADR só para Terraform e para as barreiras da cópia:** são as duas que o ADR-0019 deixou em aberto por escrito.
- **Sem ADR para Tailscale, Hetzner, R2 e GHCR:** são fornecedores, e trocar um não derruba nenhuma decisão. Vão para os runbooks (passo a passo de operação).
- **Lugar do arquivo de estado:** runbook de deploy, com uma frase de motivo. Trocar depois é um comando, então não é caro de reverter.
- **Runbook novo, "Preparar contas e credenciais":** como gerar, cadastrar e conferir cada credencial.
- **Este tipo de documento:** criado nesta entrega, para o que não cabia em ADR nem em runbook.

## Corrigido no caminho
| O que foi afirmado | O que era verdade | O que mudou |
|---|---|---|
| Hetzner CX22 a €3,79, disponível nos EUA, com 119 ms | A linha barata só existe na Alemanha e na Finlândia; nos EUA o mínimo de 4 GB custa €31,99. O preço subiu em 2026-06-15 e o plano virou CX23 | A latência da opção barata passou de 119 para cerca de 240 ms |
| Vultr em São Paulo por cerca de US$ 24 | São Paulo tem acréscimo de 50%: US$ 30 | A opção de menor latência ficou a mais cara das comparáveis |
| Recomendação inicial: Vultr em São Paulo, por latência | O critério de quem mantém o projeto é preço | A escolha passou para a Hetzner |
| "O deploy não deixa nenhum segredo no GitHub" | A identidade federada tira só os dois segredos de entrada na rede | A lista de segredos que continuam entrou na decisão 7 |
| O job de imagens "nunca roda em PR" | Roda, com a permissão declarada; duas condições impedem publicar | A condição de publicar passou a exigir também a branch `main` |
| Os pacotes nasceriam privados | Nasceram públicos | O passo manual saiu do runbook |
| A construção no PR barraria Dockerfile quebrado | O job não era obrigatório para o merge | Virou obrigatório (decisão 9) |

## Em aberto
- **Trava do estado no R2:** testar na camada persistente; se não funcionar, fila no CI.
- **Identidade federada:** testar no fluxo de deploy; se travar, cliente OAuth.
- **Degrau de 2 GB:** medir se basta quando houver servidor.
- **Cache do Gradle:** conferir se o job de backend volta para perto de 57 s na próxima execução.
- **Backend compilado duas vezes** (no teste e dentro da imagem): medir o custo com cache quente antes de mexer.
- **Fixar as ações pelo identificador e ligar atualizador automático:** quando o fluxo de deploy trouxer segredos do servidor.
- **Reexecutar um fluxo da `main` sobrescreve a imagem daquele commit,** porque as imagens base mudam com o tempo. Sem ação por ora.
- **Entregas que faltam, uma por vez:** camada persistente com o runbook de contas e credenciais; camada efêmera com o runbook de backup; fluxo de deploy com o runbook de deploy.
