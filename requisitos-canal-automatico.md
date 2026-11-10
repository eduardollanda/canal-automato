# Levantamento de Requisitos e Ordem de Implementação

## Canal Automático com Vídeos do YouTube (Cache ≤ 2GB)

Documento de requisitos para implementar um algoritmo de canal automático que baixa vídeos do YouTube, monta a programação em sequência contínua **com breaks de propaganda**, identifica tipo e duração de cada comercial, busca um equivalente no YouTube, **aprende com as views** para entregar mais do tipo de conteúdo mais assistido, garante que sempre haja conteúdo no ar, calcula o cache mínimo necessário para troca sem delay e respeita o limite de **2GB** de armazenamento da máquina.

---

## 1. Objetivo do produto

Criar o canal automático **frapfel TV**, focado em **futebol brasileiro** (Brasileirão, clubes, seleções, gols, melhores momentos, análises, bastidores, entrevistas, clássicos, Copa do Brasil e temas afins), que:

1. Seleciona vídeos do YouTube de futebol do Brasil para a programação principal
2. Monta uma programação sequencial (playlist contínua) com playout 24h
3. Insere **propagandas no meio** da programação (breaks comerciais tipados, com bias esportivo quando fizer sentido)
4. Para cada slot comercial: **identifica o tipo**, define a **duração** e **encontra um vídeo equivalente no YouTube**
5. **Aprende com a interação de views**: quanto mais um tipo editorial (ex.: `gols`, `classico`) é visto, mais esse tipo entra na programação
6. Garante que **sempre** haja algo passando (sem buraco / tela preta)
7. Mantém em cache apenas o mínimo necessário para a próxima troca ser instantânea
8. Apaga o vídeo da memória/disco assim que ele termina de tocar
9. Nunca ultrapassa **2GB** somando todos os vídeos em cache (conteúdo + propaganda)
10. Possui **logo oficial do canal** e exibe **marca d'água permanente** no canto inferior direito durante toda a programação

Em essência: um playout linear 24h de **futebol BR** com identidade **frapfel TV**, grade comercial simplificada, **recomendação por afinidade de views**, prefetch inteligente e orçamento rígido de disco.

---

## 2. Contexto herdado (conceitos de TV aplicados)

Este sistema adapta a lógica de programação/playout/grade comercial descrita no documento de referência:

| Conceito de TV | Equivalente neste canal automático |
|---|---|
| Grade de programação | Fila ordenada de vídeos a tocar |
| Playout | Player local que executa a timeline |
| Break / vinheta | Bloco de propaganda inserido entre (ou no meio de) conteúdos |
| Spot comercial | Vídeo curto do YouTube classificado por tipo + duração |
| Tráfego comercial | Motor que escolhe tipo/duração e busca equivalente no YouTube |
| Playlist / rundown | Fila runtime: atual + próximos (conteúdo ou ad) |
| As-run | Log do que tocou de fato (programa vs propaganda) |
| Inventário limitado | Orçamento de disco = 2GB |
| Fill | Vídeo reserva / fallback sempre disponível |
| Scheduler de prefetch | Decide o que baixar e quando apagar |
| Audiência / views | Sinal de afinidade por tipo de conteúdo |
| Programação por demanda | Source Manager enviesa a fila para tipos mais vistos |

Escopo do produto: **programação contínua de futebol brasileiro sem delay + propagandas tipadas + feedback de views para reforçar tipos editoriais populares**.

---

## 3. Restrições hard (não negociáveis)

### R1 — Limite de armazenamento
- Soma do tamanho de **todos** os arquivos de vídeo em cache ≤ **2048 MB** (2GB).
- Preferência operacional: trabalhar com teto de segurança de **1900 MB** para sobra de SO, logs, metadados e downloads parciais.

### R2 — Continuidade do ar
- Em operação normal, o fim de um vídeo e o início do próximo devem ocorrer **sem gap perceptível** (meta: delay ≈ 0; tolerância máxima sugerida < 100–200 ms de handoff).

### R3 — Evicção imediata pós-exibição
- Assim que o vídeo **atual** terminar de tocar, seu arquivo deve ser **apagado** do cache (salvo se marcado como `pinned` / fallback).

### R4 — Sempre haver próximo pronto
- Antes do vídeo atual acabar, o **próximo** vídeo já deve estar **baixado e validado** no disco.

### R5 — Fonte de conteúdo
- Entrada principal: vídeos do YouTube (URLs, IDs, playlists ou busca configurada).
- Propagandas também vêm do YouTube, escolhidas por **tipo + duração alvo**.

### R6 — Ambiente alvo
- Máquina com pouco recurso e disco limitado a 2GB para o cache de mídia.
- O algoritmo deve priorizar **poupar armazenamento** acima de “baixar muita coisa adiantado”.

### R7 — Propagandas no meio da programação
- O canal deve inserir breaks comerciais conforme a política de grade.
- Cada propaganda precisa ter: **tipo identificado**, **duração alvo** e **match no YouTube**.

### R8 — Feedback de views na seleção de conteúdo
- O algoritmo deve se alimentar das views/interações.
- Tipos de conteúdo com mais views efetivas devem receber **maior probabilidade** de entrar na programação seguinte.
- Deve haver freio de exploração para não travar 100% em um único tipo.

### R9 — Identidade visual (logo + marca d'água)
- O canal deve ter uma **logo oficial** criada e versionada no projeto (`assets/logo.png` ou equivalente).
- Durante **toda** a programação (conteúdo e propaganda), a logo deve aparecer como **marca d'água fixa no canto inferior direito**.
- A marca d'água não pode bloquear controles essenciais do player de forma permanente, mas deve permanecer visível o tempo todo.
- Opacidade sugerida: 55–80%; tamanho responsivo (ex.: ~8–12% da largura do player no desktop).
- A logo também deve aparecer na UI do canal (cabeçalho / painel do algoritmo).

---

## 4. Atores e componentes

| Componente | Responsabilidade |
|---|---|
| **Source Manager** | Descobre/seleciona próximos vídeos de conteúdo no YouTube (enviesado pelos pesos de afinidade) |
| **Content Taxonomy** | Classifica cada conteúdo em um ou mais `content_type` |
| **View Tracker** | Captura eventos de view/interação e atribui ao tipo de conteúdo |
| **Affinity Engine** | Atualiza pesos por tipo (“quanto mais visto, mais entregar”) |
| **Brand Overlay** | Exibe logo/marca d'água no canto inferior direito em todo o playout |
| **Ad Planner (Tráfego)** | Decide onde entra break, tipo de propaganda e duração do slot |
| **Ad Matcher** | Busca no YouTube um vídeo equivalente ao tipo+duração pedidos |
| **Downloader** | Baixa o arquivo (conteúdo ou ad) para cache local |
| **Cache Manager** | Controla espaço (≤ 2GB), TTL, delete e pinned |
| **Scheduler / Algoritmo de prefetch** | Decide quantos e quais itens manter prontos |
| **Playout Engine** | Toca o item atual e faz handoff para o próximo |
| **Program Queue** | Fila lógica misturando `content` e `ad` |
| **Fallback Pack** | Conteúdo/ad reserva se download falhar |
| **As-run Logger** | Registra o que foi ao ar, tipo (programa/ad), views e cache |

---

## 5. Requisitos funcionais

### RF01 — Montagem da programação
- O sistema deve manter uma **fila de programação** com itens ordenados.
- Cada item contém no mínimo: `kind` (`content` | `ad`), `video_id`, `titulo`, `duracao_estimada`, `tamanho_estimado`, `status`, `prioridade`.
- Itens `content` contêm ainda: `content_type` (categoria principal) e opcionalmente `content_tags[]`.
- Itens `ad` contêm ainda: `ad_type`, `target_duration_sec`, `matched_query`, `match_score`.
- Status sugeridos: `planned` → `matching` → `downloading` → `ready` → `playing` → `played` → `deleted` (ou `failed`).

### RF02 — Seleção de conteúdo YouTube
- Deve aceitar pelo menos uma origem configurável:
  - lista de IDs/URLs
  - playlist do YouTube
  - regras simples de busca/categoria (fase 2)
- Não deve enfileirar item sem metadados mínimos (duração e tamanho estimado, ou política de estimativa).

### RF11 — Inserção de propagandas no meio
- A grade deve intercalhar conteúdo e propaganda.
- Políticas mínimas configuráveis:
  - `ads_every_n_content_videos` (ex.: 1 ad a cada 1 conteúdo)
  - `ads_every_n_seconds_of_content` (ex.: break a cada 8–12 min de conteúdo)
  - `break_size` (1..N spots por break)
- Exemplo de timeline:
  ```text
  [conteúdo A] → [ad 30s] → [conteúdo B] → [ad 15s] → [ad 30s] → [conteúdo C]
  ```
- O break não pode abrir buraco: o(s) ad(s) do próximo break precisam estar `ready` antes do handoff.

### RF12 — Identificar tipo de propaganda
- Todo slot comercial deve nascer com um **tipo** explícito.
- Taxonomia mínima obrigatória:

| Código | Tipo | Descrição | Duração típica |
|---|---|---|---|
| `spot_15` | Spot curto | Anúncio rápido de marca/produto | 15s |
| `spot_30` | Spot padrão | Anúncio clássico de TV | 30s |
| `spot_60` | Spot longo | Filme publicitário curto | 60s |
| `promo_house` | Chamada da casa | Divulga o próprio canal/programação | 10–20s |
| `trailer` | Trailer / teaser | Prévia de filme, série, game, evento | 30–90s |
| `retail` | Varejo | Oferta, preço, loja, promoção | 15–30s |
| `food_beverage` | Alimentação / bebida | Comida, delivery, refrigerante etc. | 15–30s |
| `tech` | Tecnologia | App, celular, eletrônicos | 15–30s |
| `auto` | Automotivo | Carro, moto, concessionária | 30–60s |
| `finance` | Financeiro | Banco, cartão, seguro, pix/crédito | 15–30s |
| `beauty` | Beleza / higiene | Cosmético, perfume, higiene | 15–30s |
| `public_service` | Utilidade pública | Campanha educativa/alerta | 15–30s |
| `event` | Evento | Show, esporte, live, ingresso | 15–30s |
| `generic_brand` | Marca genérica | Fallback quando não houver tipo específico | 15–30s |

- O Ad Planner escolhe o tipo por:
  1. regra da grade (rodízio / pesos)
  2. contexto do conteúdo anterior (opcional; ex.: conteúdo de games → prioriza `tech`/`trailer`)
  3. restrições (não repetir o mesmo tipo N vezes seguidas)

### RF13 — Definir duração do comercial
- Cada tipo tem uma **duração alvo** e uma **janela de tolerância**.
- Exemplos de política:

| Tipo | Alvo | Aceita entre |
|---|---|---|
| `spot_15` | 15s | 12–18s |
| `spot_30` | 30s | 25–35s |
| `spot_60` | 60s | 50–70s |
| `trailer` | 60s | 30–90s |
| `promo_house` | 15s | 8–20s |

- O break tem `break_budget_sec` (ex.: 60s). A soma das durações reais dos spots deve caber nesse orçamento (± tolerância pequena).
- Se o match do YouTube vier um pouco maior/menor, o sistema:
  - aceita se estiver na janela
  - senão busca outro candidato
  - em último caso, usa fill/`promo_house` curto pinned

### RF14 — Achar propaganda equivalente no YouTube
- Dado `ad_type` + `target_duration_sec`, o **Ad Matcher** deve buscar no YouTube um vídeo semelhante.
- Pipeline de matching:
  1. Montar query a partir do tipo (ex.: `spot_30` + `food_beverage` → `"commercial food ad 30 seconds"` / `"propaganda comida 30 segundos"`)
  2. Buscar N candidatos (ex.: 8–15)
  3. Filtrar por duração dentro da janela
  4. Filtrar por restrições (duração, tamanho estimado ≤ espaço livre, não listado como live, etc.)
  5. Pontuar (`match_score`) por:
     - proximidade da duração alvo
     - palavras-chave do tipo no título/descrição
     - tamanho pequeno (favorece cache 2GB)
     - não-repetição recente (já exibido nas últimas X horas)
  6. Escolher o melhor score e enfileirar como `ad`
- Deve existir um **mapa tipo → queries** configurável (PT/EN), por exemplo:
  - `retail`: `["propaganda oferta loja", "retail commercial ad", "promocao varejo comercial"]`
  - `auto`: `["car commercial 30 seconds", "propaganda carro", "automotive ad"]`
- Se não achar match bom (`score < limiar`):
  1. tentar tipo coringa `generic_brand` com mesma duração
  2. tentar `promo_house`
  3. pular o slot e seguir ao próximo conteúdo **somente** se a política permitir; caso contrário usar fallback de ad pinned

### RF15 — Prefetch também dos ads
- Ads entram na mesma fila de prefetch que conteúdo.
- Prioridade de prontidão: se o próximo item da timeline for `ad`, ele precisa estar `ready` com a mesma regra anti-delay.
- Ads tendem a ser curtos/leves → preferir baixá-los cedo, pois ajudam a manter o handoff sem ocupar muito dos 2GB.

### RF16 — Tipagem de conteúdo (taxonomia)
- Todo item `content` deve ter um `content_type` antes de entrar na fila (ou no máximo ao iniciar o play).
- Taxonomia editorial do **frapfel TV** (futebol brasileiro, configurável):

| Código | Tipo de conteúdo |
|---|---|
| `gols` | Gols e placas |
| `melhores_momentos` | Highlights / resumos de jogos |
| `analise` | Análise tática e comentários pós-jogo |
| `entrevista` | Entrevistas e coletivas |
| `bastidores` | Bastidores de clubes e seleção |
| `classico` | Clássicos e derbies brasileiros |
| `brasileirao` | Campeonato Brasileiro (Série A / rodadas) |
| `copa` | Copa do Brasil e competições de mata-mata |
| `selecao` | Seleção brasileira |
| `curiosidade` | História, curiosidades e documentários |
| `other` | Futebol BR genérico / não classificado |

- Buscas YouTube devem priorizar queries em português sobre futebol do Brasil (clubes, Brasileirão, seleção, etc.).
- Fontes de classificação (em ordem):
  1. tag manual / regra da origem (playlist → tipo)
  2. palavras-chave do título/descrição/canal (taxonomia de futebol BR)
  3. fallback `other`

### RF17 — Captura de interação de views
- O sistema deve registrar eventos de view por conteúdo exibido.
- Eventos mínimos:
  - `view_start` — começou a tocar
  - `view_progress` — marcos (25%, 50%, 75%)
  - `view_complete` — chegou ao fim (ou ≥ `completion_threshold`, ex.: 90%)
  - `view_skip` / `view_abandon` — saiu cedo (se houver controle remoto/UI; no canal linear puro, abandon pode ser N/A)
- Cada evento carrega: `video_id`, `content_type`, `watched_sec`, `watched_ratio`, `timestamp`
- No MVP linear sem app de usuário, **view = exibição no ar** (as-run + completion).  
  Quando houver player com audiência mensurável (web/app), views reais do espectador substituem/somam a esse sinal.

### RF18 — Score de afinidade por tipo (“mais visto → mais entregar”)
- Manter um vetor de pesos `affinity[content_type]`.
- A cada view válida, atualizar o peso do tipo correspondente.
- Fórmula sugerida (simples e testável):

```text
signal = watched_ratio                    # 0..1
se watched_ratio >= completion_threshold:
  signal += bonus_complete                # ex.: +0.5

affinity[type] =
  affinity[type] * decay                  # ex.: 0.995 por ciclo/hora
  + learning_rate * signal                # ex.: 0.2 * signal

# normalizar periodicamente para soma = 1 (ou softmax)
```

- Regra de negócio central:
  - **quanto maior `affinity[type]`, maior a chance desse tipo ser escolhido** no próximo enfileiramento de conteúdo.
- Deve existir:
  - `min_explore_ratio` (ex.: 15–20%) para tipos fracos/aleatórios — evita monocultura
  - `max_type_share` (ex.: 50–60%) — nenhum tipo domina totalmente a grade
  - `decay` temporal — views antigas pesam menos que views recentes

### RF19 — Seleção de próximo conteúdo enviesada por afinidade
- Ao completar a fila, o Source Manager:
  1. amostra um `content_type` com probabilidade ∝ `affinity[type]` (com exploração)
  2. busca no YouTube candidatos desse tipo
  3. aplica filtros de cache (tamanho ≤ espaço livre)
  4. enfileira o escolhido
- Pseudoseleção:

```text
se random() < min_explore_ratio:
  tipo = random_type()
senão:
  tipo = weighted_sample(affinity)

candidatos = youtube_search_by_type(tipo)
escolher candidato que caiba no cache e não tenha repetido recentemente
```

- O mesmo sinal pode **influenciar ads** (opcional, fase 2):
  - conteúdo `classico` / `gols` em alta → mais chance de `event` / `food_beverage` no break
  - conteúdo `brasileirao` / `copa` em alta → mais `event` / `finance` (patrocínio esportivo)

### RF20 — Persistência e observabilidade da afinidade
- Persistir `affinity` em disco (JSON/SQLite) entre restarts.
- Expor no log/métricas:
  - top tipos por peso
  - views por tipo na última hora/dia
  - % da grade entregue por tipo vs % de afinidade (calibração)
- Permitir reset manual dos pesos (“esquecer preferências”).

### RF21 — Logo do canal
- Deve existir asset oficial de logo do canal no repositório (`assets/logo.jpg`).
- Nome de marca na UI: **frapfel TV** (canal de futebol brasileiro).
- A logo é usada na marca d'água e no chrome da aplicação (header), com identidade visual alinhada ao tema esportivo/BR.

### RF22 — Marca d'água permanente
- Overlay da logo no **canto inferior direito** do player em todos os itens (`content` e `ad`).
- Visível do início ao fim de cada vídeo, inclusive em handoff.
- Não deve ser removida por troca de item; faz parte do layer fixo da UI de playout.

### RF03 — Garantia de continuidade (“sempre algo passando”)
- Enquanto o canal estiver `ON`, deve existir:
  - 1 item `playing`
  - ≥ 1 item `ready` **ou** fallback pronto
- Se não houver próximo `ready` a tempo, acionar fallback automaticamente sem interromper o ar.

### RF04 — Prefetch mínimo sem delay
- O algoritmo deve calcular e manter a **quantidade mínima de vídeos em cache** para que, quando o atual acabar, o próximo inicie imediatamente.
- Em condições ideais, o mínimo operacional é:
  - **1 tocando** + **1 pronto** (= 2 arquivos)
- Em condições de rede lenta, pode precisar de **1 tocando + 1 pronto + 1 baixando** (ainda assim, só o necessário).

### RF05 — Cálculo de orçamento de disco
- Antes de baixar, estimar se o novo arquivo cabe em:
  `espaco_livre = LIMITE_CACHE - soma(arquivos_em_cache) - margem_seguranca`
- Se não couber, o sistema deve:
  1. apagar elegíveis (já tocados; ou planned cancelados)
  2. se ainda não couber, baixar versão menor (qualidade mais baixa)
  3. se ainda não couber, pular o item e escolher outro menor
  4. nunca estourar 2GB

### RF06 — Apagar após tocar
- No evento `onEnded` do player:
  1. promover próximo `ready` para `playing`
  2. iniciar handoff imediato
  3. apagar arquivo do item recém-finalizado
  4. atualizar orçamento de cache
  5. disparar prefetch do próximo necessário

### RF07 — Qualidade adaptativa para caber no limite
- Deve ser possível escolher formato/qualidade de download visando menor tamanho (ex.: 360p/480p), desde que assistível.
- Política padrão sugerida: menor qualidade que atenda `min_height` configurável (ex.: 360).

### RF08 — Fallback obrigatório
- Deve existir pelo menos **1 vídeo local fallback** (pinned), pequeno, que:
  - nunca é apagado automaticamente
  - entra no ar se a fila falhar
  - conta dentro dos 2GB

### RF09 — Observabilidade mínima
- Logar:
  - início/fim de cada vídeo
  - tempo restante vs progresso do download do próximo
  - uso de disco em MB
  - falhas de download / handoff / delete
  - acionamento de fallback

### RF10 — Recuperação de falhas
- Download falhou: tentar próximo candidato; se crítico, fallback.
- Arquivo corrompido: marcar `failed`, apagar, buscar outro.
- Queda do processo: ao reiniciar, limpar downloads parciais órfãos e remontar fila com base no estado salvo.

---

## 6. Requisitos não funcionais

| ID | Requisito |
|---|---|
| RNF01 | Uso de disco de mídia ≤ 2GB (hard) |
| RNF02 | Handoff sem gap perceptível em operação normal |
| RNF03 | Baixo uso de RAM; não manter múltiplos vídeos inteiros em memória além do necessário ao decode/playback |
| RNF04 | Determinismo do algoritmo de prefetch (regras claras, testáveis) |
| RNF05 | Operação headless (servidor/VPS) |
| RNF06 | Resiliência a rede instável (buffer de tempo, não buffer excessivo de disco) |
| RNF07 | Idempotência nas operações de delete/download |

---

## 7. Núcleo do algoritmo (requisito central)

### 7.1 Problema
Manter playback contínuo baixando do YouTube (conteúdo + propaganda), com troca sem delay, **minimizando arquivos em disco** e respeitando 2GB — incluindo a etapa de **classificar tipo/duração do ad e achar equivalente no YouTube**.

### 7.2 Definições

- `V_atual`: item tocando agora (`content` ou `ad`)
- `V_prox`: próximo da fila
- `T_restante`: tempo restante de `V_atual`
- `T_download(v)`: tempo estimado para baixar `v`
- `T_match(ad)`: tempo estimado para buscar/selecionar equivalente no YouTube
- `S(v)`: tamanho estimado/real de `v` em bytes
- `CacheUsed`: soma dos arquivos presentes
- `Limit`: 2GB (ou 1900MB úteis)
- `PinnedSize`: tamanho do(s) fallback(s)
- `AdSlot(type, duration)`: intenção comercial antes do match
- `AdMatch`: vídeo YouTube escolhido para preencher o slot

### 7.3 Invariantes do algoritmo

1. `CacheUsed ≤ Limit`
2. Enquanto canal ON: existe `V_atual` tocando
3. Se `T_restante ≤ T_download(V_prox) + margem`, então `V_prox` já deve estar `ready` (senão risco de buraco)
4. Ao terminar `V_atual`: apagar `V_atual` (se não pinned) e iniciar `V_prox` imediatamente
5. Nunca baixar item se `CacheUsed + S(v) > Limit` sem antes liberar espaço elegível

### 7.4 Quantidade mínima em cache

Meta de poupar armazenamento: manter o menor número possível de arquivos.

**Caso A — Rede rápida o bastante**

```text
mínimo = 2 arquivos
(atual ready/playing + próximo ready)
```

Condição:
`T_download(próximo_ainda_não_baixado) < T_restante(atual) - margem`

Na prática: enquanto toca o atual, baixa o seguinte; quando o seguinte já estiver `ready`, não precisa de um terceiro.

**Caso B — Rede lenta / arquivo grande**

```text
mínimo = 3 arquivos (temporariamente)
(atual playing + próximo ready + seguinte downloading)
```

Isso só é permitido se couber em 2GB. Se não couber, reduzir qualidade ou escolher vídeo menor.

**Caso C — Emergência**

```text
1 playing + fallback pinned
```

Usado quando a fila não consegue preparar próximo a tempo.

### 7.5 Fórmula de decisão de prefetch

Para cada ciclo de decisão:

```text
espaço_livre = Limit - CacheUsed
precisa_baixar_agora =
  (não existe item ready além do atual)
  OR (T_restante(atual) <= T_download(candidato) + margem_seguranca)

se precisa_baixar_agora:
  escolher candidato C na fila com menor S(C) que ainda atenda política de qualidade
  se S(C) <= espaço_livre:
     baixar C
  senão:
     tentar reduzir qualidade de C
     senão escolher outro candidato menor
     senão manter/ativar fallback
```

### 7.6 Fórmula de capacidade (quantos vídeos cabem)

Não fixar “N vídeos”, fixar por **bytes**:

```text
capacidade_dinamica =
  quantos itens ready/downloading cabem em (Limit - PinnedSize)
  priorizando: 1 playing + 1 next ready
```

Exemplo:
- fallback pinned = 40MB
- útil ≈ 1860MB
- se cada vídeo médio = 120MB → teoricamente caberiam ~15, mas a política deve manter só 2–3

**Regra de ouro do produto:**  
*Cabe mais ≠ deve guardar mais.* Guardar só o mínimo para continuidade.

### 7.7 Política de apagamento

Ordem de deleção:

1. vídeos com status `played`
2. downloads parciais `failed` / órfãos
3. itens `ready` mais distantes na fila (só em emergência de espaço)
4. nunca apagar `playing`
5. nunca apagar `pinned` automaticamente

Trigger principal: `onEnded` → delete imediato do concluído.

### 7.8 Margem de segurança temporal

Definir `margem_seguranca` (ex.: 15–30s) para:

- overhead de validação do arquivo
- abertura do demuxer/player
- jitter de rede
- tempo de matching do ad (busca YouTube), quando o próximo ainda não tiver `video_id`

O próximo deve estar `ready` **antes** de `T_restante` chegar a zero, com essa folga.

### 7.9 Algoritmo do break comercial (tipo → duração → match YouTube)

```text
quando a grade pedir um break:
  budget = break_budget_sec                      # ex.: 60
  slots = []

  enquanto budget > 0 e ainda couber spot:
    tipo = escolher_tipo_por_politica()          # RF12
    dur_alvo = duracao_padrao(tipo)              # RF13
    se dur_alvo > budget: escolher tipo mais curto ou encerrar break

    slot = AdSlot(tipo, dur_alvo)
    match = buscar_equivalente_youtube(slot)     # RF14

    se match ok:
      enfileirar item kind=ad com video_id do match
      budget -= match.duration
      slots.append(match)
    senão:
      tentar generic_brand / promo_house / ad_fallback_pinned
      se nada servir: encerrar break sem furar o ar

  prefetch do primeiro ad do break junto com a regra de continuidade
```

Regras extras do matcher:

1. Preferir vídeos **já curtos** (não cortar no player no MVP, salvo flag futura `trim_to_target`)
2. Evitar repetir o mesmo `video_id` de ad na mesma janela (ex.: 6h)
3. Contar o ad no mesmo orçamento de 2GB
4. Como ads são pequenos, podem ficar `ready` com prioridade alta sem pressionar o disco

### 7.10 Algoritmo de afinidade por views (mais visto → mais entregar)

```text
estado persistente:
  affinity[type]   # pesos >= 0, preferencialmente normalizados
  view_stats[type] # contagem, watched_sec, completes

on_view_event(video, watched_ratio):
  type = video.content_type
  signal = watched_ratio
  if watched_ratio >= completion_threshold:
    signal += bonus_complete

  affinity[type] = affinity[type] * decay + learning_rate * signal
  clamp/normalize(affinity)
  persist(affinity)

pick_next_content_type():
  if random() < min_explore_ratio:
    return random_eligible_type()
  type = weighted_sample(affinity)
  if share(type) already >= max_type_share in recent window:
    return next_best_type(affinity)
  return type

enqueue_next_content():
  type = pick_next_content_type()
  candidates = youtube_search(type)
  choose first that fits 2GB policy and anti-repeat
  enqueue(kind=content, content_type=type, ...)
```

Princípios:

1. **Reforço positivo:** completar/assistir muito sobe o peso do tipo
2. **Decaimento:** sem views novas, o peso cai aos poucos
3. **Exploração mínima:** sempre testa outros tipos
4. **Teto por tipo:** evita canal monotemático
5. **Mesmo orçamento 2GB:** afinidade só escolhe *o quê* buscar; o cache continua mandando no *quanto* guardar

### 7.11 Exemplo concreto de decisão (conteúdo + ad + views)

Conteúdo atual: resumo de clássico (11 min, `content_type=classico`). Política: 1 break de ~45s a cada conteúdo. Afinidade atual: `classico` alta após várias views.

1. View Tracker registra progresso/complete de `classico` → sobe `affinity[classico]`
2. Ad Planner define break de 45s
3. Escolhe tipos: `event` (30s) + `promo_house` (15s) (enviesado pelo conteúdo quente de futebol)
4. Matcher busca:
   - query A: `"football match promo"` / `"propaganda jogo futebol ingresso"`
   - filtra duração 25–35s, pega melhor score
   - query B: `"tv sports channel bump promo"` (ou usa pinned house)
5. Downloader baixa os 2 ads (leves) enquanto o conteúdo ainda roda
6. Ao fim do conteúdo: toca ad 30s → ad 15s → próximo conteúdo
7. Source Manager, com `affinity[classico]` alto, tende a buscar outro vídeo `classico` (respeitando explore/max share)
8. Apaga cada arquivo ao terminar

---

## 8. Regras de negócio do cache (2GB)

### RN01 — Teto absoluto
`sum(size_on_disk of cached media) <= 2147483648 bytes`

### RN02 — Reserva de sistema
Reservar margem (sugerido 100–150MB) fora do orçamento de mídia para OS/app/logs, se o disco total da máquina for 2GB.  
Se o limite de 2GB for **somente** da pasta de cache, ainda assim usar margem interna (~5%).

### RN03 — Download atômico
Baixar para arquivo temporário (`.part`) e só promover a `ready` após:
- download completo
- tamanho final conhecido
- validação básica de mídia

Arquivos `.part` também contam no orçamento.

### RN04 — Uma qualidade por vídeo
Não guardar múltiplas resoluções do mesmo ID.

### RN05 — Proibição de binge-download
É proibido pré-baixar a fila inteira. Prefetch apenas do horizonte mínimo (1, no máximo 2 à frente).  
Exceção controlada: se o próximo break tiver 2–3 spots curtos, pode pré-baixar o **break inteiro** desde que caiba e continue dentro do horizonte imediato.

### RN06 — Estimativa antes do download
Usar metadados (yt-dlp/`filesize_approx`) para prever `S(v)`. Se incerto, assumir pior caso conservador.

### RN07 — Ads no mesmo teto de disco
Conteúdo e propaganda compartilham os 2GB. Não há partição fixa obrigatória, mas recomenda-se reserva lógica:
- até ~85% para conteúdo
- até ~15% para ads ready/pinned
Isso é política, não hard-split.

### RN08 — Tipagem obrigatória do comercial
Nenhum `ad` entra na fila sem `ad_type` + `target_duration_sec`.

### RN09 — Equivalência mínima do match
Só aceitar candidato YouTube se:
- duração ∈ janela do tipo
- `match_score >= limiar`
- tamanho estimado cabe no espaço livre

---

## 9. Fluxos principais

### 9.1 Boot do canal

```text
1. Carregar config (limite 2GB, margem, fonte YouTube, qualidade mín., política de ads)
2. Verificar fallback pinned (conteúdo e, se possível, ad curto); se ausente, abortar
3. Limpar órfãos .part / played antigos
4. Montar fila inicial de conteúdo
5. Inserir breaks planejados (tipo + duração) entre conteúdos
6. Resolver match YouTube do(s) primeiro(s) ad(s)
7. Baixar V1 (conteúdo) até ready
8. Iniciar playout de V1
9. Prefetch do próximo item (conteúdo ou ad)
10. Entrar no loop de supervisão
```

### 9.2 Loop de supervisão (heartbeat)

```text
a cada N segundos:
  medir T_restante
  se próximo item é ad sem video_id: rodar Ad Matcher com antecedência
  medir progresso do download do próximo
  se risco de underrun: priorizar download / acionar fallback plan
  garantir CacheUsed <= Limit
  persistir estado
```

### 9.3 Handoff sem delay

```text
onEnded(V_atual):
  assert V_prox.status == ready (senão fallback)
  play(V_prox) imediatamente
  delete(V_atual) async mas rápido
  se a grade pedir novo break adiante: planejar tipo/duração e match
  schedule prefetch(V_prox+1)
  log as-run (kind, ad_type se houver)
```

### 9.4 Falha de download

```text
onDownloadFail(C):
  mark failed
  delete partial
  se C.kind == ad: tentar outro match do mesmo tipo/duração
  senão escolher C2 de conteúdo
  se tempo crítico: play fallback quando atual acabar
```

### 9.5 Fluxo específico de propaganda

```text
1. Ad Planner cria slot (ad_type + target_duration_sec)
2. Ad Matcher busca equivalentes no YouTube
3. Rankeia e escolhe 1 candidato
4. Downloader baixa com qualidade baixa (ads são curtos)
5. Item ad fica ready na fila
6. Playout exibe no ponto do break
7. As-run registra tipo, duração alvo, duração real, video_id
8. Delete após exibição
```

---

## 10. Dados mínimos a persistir

### 10.1 Config
- `cache_limit_bytes`
- `cache_safety_margin_bytes`
- `prefetch_margin_seconds`
- `max_ready_ahead` (default 1)
- `youtube_source`
- `preferred_max_height` (ex.: 360/480)
- `fallback_path`
- `ad_fallback_path` (opcional)
- `ads_enabled` (true)
- `ads_every_n_content_videos` / `ads_every_n_seconds_of_content`
- `break_budget_sec`
- `ad_type_weights` (rodízio/pesos)
- `ad_type_queries` (mapa tipo → lista de buscas)
- `ad_duration_windows` (alvo + min/max por tipo)
- `ad_match_score_threshold`
- `ad_no_repeat_window_hours`
- `content_types` / `content_type_queries`
- `affinity_learning_rate`
- `affinity_decay`
- `completion_threshold` (ex.: 0.9)
- `bonus_complete`
- `min_explore_ratio` (ex.: 0.2)
- `max_type_share` (ex.: 0.55)
- `ads_follow_content_affinity` (bool, default false no MVP / true na fase 2)

### 10.2 Estado runtime
- fila (ordered list de content/ad)
- item atual
- uso de disco atual
- `affinity` por `content_type`
- `view_stats` por tipo
- métricas: underruns, fallback_hits, downloads_failed, ad_match_hits, ad_match_misses, views_by_type, delivery_share_by_type

### 10.3 As-run
- `video_id`, `kind`, `content_type?`, `ad_type?`, `target_duration_sec?`, `actual_duration_sec`
- `watched_sec`, `watched_ratio`, `completed` (bool)
- `started_at`, `ended_at`, `bytes`, `source`, `match_score?`, `was_fallback`

---

## 11. Critérios de aceite (Definition of Done)

O algoritmo/MVP será aceito quando:

1. Rodar por pelo menos **60 minutos** sem tela preta em rede normal
2. Handoff entre vídeos (conteúdo↔ad) ocorrer sem delay perceptível
3. Disco de cache **nunca** passar de 2GB (teste com assert contínuo)
4. Vídeo concluído é apagado imediatamente após o handoff
5. Em falha de rede simulada, fallback entra e o canal não para
6. Nunca há mais do que `max_ready_ahead + 1 playing (+ optional downloading)` além do pinned, salvo emergência documentada
7. Logs mostram `T_restante`, status do próximo e `CacheUsed`
8. Breaks comerciais aparecem conforme a política configurada
9. Cada ad exibido tem `ad_type` + duração alvo identificados no as-run
10. O sistema encontra no YouTube um equivalente aceitável (ou cai no fallback de ad) para o tipo/duração pedidos
11. Não repete o mesmo ad dentro da janela configurada
12. Cada conteúdo exibido tem `content_type` e gera evento de view
13. Após N views concentradas em um tipo, a taxa de entrega desse tipo sobe de forma mensurável
14. Mesmo com um tipo dominante, a grade respeita `min_explore_ratio` e `max_type_share`
15. Pesos de afinidade sobrevivem a restart do processo
16. Logo oficial existe no projeto e aparece na UI
17. Marca d'água da logo permanece no canto inferior direito durante toda a programação

---

## 12. Fora de escopo (MVP)

- Venda real para anunciantes / billing / IO de agência
- Make-good comercial financeiro
- Janelas nacional × afiliada
- UI complexa de tráfego
- Personalização multi-usuário sofisticada (MVP: afinidade global do canal; por usuário só se houver identidade)
- Multi-região SSAI
- Detecção automática de marca via visão computacional (pode ser fase futura)
- Classificação de conteúdo por modelo de ML pesado (MVP: regras/keywords; ML opcional depois)
- Corte fino frame-a-frame do ad para duração exata (MVP aceita janela de tolerância)
- Transcodificação pesada local (evitar; preferir baixar já no tamanho certo)

Podem ser fases posteriores, reaproveitando os conceitos do documento de programação/grade comercial.

---

## 13. Riscos e mitigações

| Risco | Impacto | Mitigação |
|---|---|---|
| Vídeo YouTube muito grande | Estoura cache / atrasa download | Forçar baixa resolução; pular itens grandes |
| Rede mais lenta que duração restante | Buraco no ar | margem temporal + fallback + iniciar download mais cedo |
| Remoção/bloqueio do vídeo na origem | Falha de download | candidatos reserva na fila |
| Estimativa de tamanho errada | Overcommit de disco | contar `.part`; abortar se passar do limite |
| Player demora a abrir arquivo | Microdelay no handoff | pré-abrir/pre-roll do próximo quando T_restante < X |
| Máquina com 2GB no total (não só cache) | SO sem espaço | reduzir Limit útil e pinned pequeno |
| Match de ad ruim / irrelevante | Propaganda fora do tipo | queries por tipo + score mínimo + fallback tipado |
| YouTube sem resultado na duração exata | Slot vazio | janela de tolerância + tipos curtos + ad pinned |
| Ads demais na fila | Pressão no cache 2GB | horizonte curto; apagar ads após tocar; preferir spots leves |

---

## 14. Ordem de implementação (executar nesta sequência)

### Fase 0 — Preparação
1. Definir estrutura do projeto e pasta de cache
2. Fixar constantes: `LIMIT=2GB`, margem, `max_ready_ahead=1`
3. Criar fallback local pequeno e pinned
4. Escolher stack mínima sugerida:
   - downloader: `yt-dlp`
   - player: `mpv` (ou equivalente com eventos de fim e suporte a playlist/handoff)
   - orquestração: Node, Python ou Go (qualquer um; preferir o mais simples para o time)

**Entrega:** app sobe, toca o fallback em loop sem crash.

### Fase 1 — Fila e estados
1. Modelar `ProgramItem` + status machine
2. Persistência simples (JSON/SQLite)
3. Comando para enfileirar IDs do YouTube
4. Logger as-run básico

**Entrega:** fila manipulável; estados claros.

### Fase 2 — Downloader com orçamento
1. Integrar `yt-dlp` com seleção de qualidade baixa
2. Estimar tamanho antes de baixar
3. Download em `.part` + promote
4. Enforce `CacheUsed <= Limit`
5. Delete API (played/failed/partial)

**Entrega:** baixa 1 vídeo cabendo no limite; valida e registra tamanho.

### Fase 3 — Playout contínuo (2 itens)
1. Baixar V1, tocar V1
2. Enquanto toca V1, baixar V2
3. No `onEnded`, handoff V1→V2 sem gap
4. Apagar V1 imediatamente
5. Repetir para V3…

**Entrega:** canal contínuo com 1 playing + 1 ready; delete pós-exibição.

### Fase 4 — Algoritmo de prefetch (núcleo)
1. Implementar cálculo `precisa_baixar_agora`
2. Implementar estimativa `T_download`
3. Implementar margem de segurança
4. Implementar escolha de candidato menor quando espaço/tempo apertar
5. Métricas de risco de underrun

**Entrega:** decisão automática de quando baixar/apagar/pular.

### Fase 5 — Fallback e resiliência
1. Watchdog de underrun
2. Fallback automático
3. Retentativas e skip de item inválido
4. Limpeza de órfãos no boot
5. Teste de rede lenta / disco cheio

**Entrega:** canal não para mesmo com falhas.

### Fase 6 — Programação automática de conteúdo
1. Source Manager puxa próximos da playlist/lista configurada
2. Regras simples de não-repetição imediata
3. Preenchimento automático da fila quando estiver curta
4. Painel/log de ocupação de cache (% de 2GB)

**Entrega:** operação autônoma de conteúdo por horas sem intervenção.

### Fase 7 — Grade de propagandas (tipo + duração)
1. Modelar `AdSlot` (`ad_type`, `target_duration_sec`, janela min/max)
2. Implementar Ad Planner (onde inserir break; orçamento do break)
3. Rodízio/pesos de tipos
4. Inserir itens `kind=ad` na fila entre conteúdos
5. As-run diferenciando conteúdo vs propaganda

**Entrega:** timeline com buracos comerciais tipados (ainda sem match automático completo).

### Fase 8 — Ad Matcher no YouTube
1. Mapa configurável `ad_type → queries`
2. Busca de candidatos via yt-dlp/API de busca
3. Filtro por duração na janela do tipo
4. Score de equivalência + limiar mínimo
5. Fallback: `generic_brand` → `promo_house` → ad pinned
6. Anti-repetição de `video_id` de ad
7. Prefetch dos ads do próximo break dentro do teto 2GB

**Entrega:** para cada slot, o sistema identifica tipo/tempo e acha um equivalente no YouTube.

### Fase 9 — Afinidade por views
1. Taxonomia `content_type` + classificação por keywords/origem
2. View Tracker (start/progress/complete) ligado ao playout/as-run
3. Affinity Engine (learning_rate, decay, normalize)
4. Source Manager com amostragem ponderada + explore/max share
5. Persistência de `affinity` e métricas delivery vs affinity
6. (Opcional) ads enviesados pelo tipo de conteúdo quente

**Entrega:** quanto mais um tipo é visto, mais ele aparece na programação — com freios de exploração.

### Fase 10 — Endurecimento
1. Assert contínuo do teto 2GB
2. Testes de longa duração com breaks + afinidade ativos
3. Ajuste fino de margem temporal, qualidade, queries e hiperparâmetros de affinity
4. Documentação de operação (start/stop/config/tipos/reset de afinidade)

**Entrega:** versão estável para subir na máquina alvo.

---

## 15. Pseudocódigo de referência (ordem de implementação do núcleo)

```text
LIMIT = 2GB
MAX_READY_AHEAD = 1
MARGIN_SEC = 20

function plan_break(budget_sec):
  while budget_sec > 0:
    tipo = pick_ad_type(affinity)            # pode seguir content quente
    alvo = target_duration(tipo)
    if alvo > budget_sec: break
    match = youtube_find_equivalent(tipo, alvo)
    if match:
      enqueue(kind=ad, ad_type=tipo, video=match)
      budget_sec -= match.duration
    else:
      enqueue(ad_fallback_or_promo_house())
      break

function enqueue_next_content():
  content_type = pick_next_content_type(affinity)  # RF18/RF19
  video = youtube_search_by_type(content_type)
  enqueue(kind=content, content_type=content_type, video=video)

loop forever:
  ensure_content_and_breaks_planned()

  atual = playing_item()
  ready_ahead = items_ready_after(atual)
  candidato = next_non_ready_candidate()

  if candidato.kind == ad and candidato.video_id is empty:
    candidato = youtube_find_equivalent(candidato.ad_type, candidato.target_duration)

  if ready_ahead < MAX_READY_AHEAD and candidato exists:
    eta = estimate_match_and_download_time(candidato)
    if ready_ahead == 0 or atual.remaining() <= eta + MARGIN_SEC:
      if can_fit(candidato.size):
        download(candidato)
      else:
        candidato = find_smaller_candidate_that_fits()
        if candidato: download(candidato)
        else: arm_fallback()

  on_progress/on_ended(atual):
    if atual.kind == content:
      record_view(atual)                 # alimenta affinity
      update_affinity(atual.content_type, watched_ratio)
    prox = first_ready_or_fallback()
    if event == ended:
      play(prox)                         # imediato
      delete_file(atual)                 # se não pinned
      enqueue_more_plans_if_needed()     # content enviesado + ads
```

---

## 16. Checklist de implementação (ordem curta)

- [ ] 1. Fallback pinned + play loop
- [ ] 2. Fila com estados (`content` / `ad`)
- [ ] 3. Download YouTube com qualidade baixa
- [ ] 4. Enforcement do teto 2GB
- [ ] 5. Handoff sem delay (atual→próximo)
- [ ] 6. Delete imediato do vídeo concluído
- [ ] 7. Prefetch mínimo (1 à frente)
- [ ] 8. Cálculo temporal anti-buraco
- [ ] 9. Fallback automático em falha
- [ ] 10. Autopreenchimento da programação de conteúdo
- [ ] 11. Ad Planner: inserir breaks com tipo + duração
- [ ] 12. Ad Matcher: buscar equivalente no YouTube
- [ ] 13. Score/limiar + anti-repetição de ads
- [ ] 14. As-run com tipo/duração de propaganda
- [ ] 15. Taxonomia `content_type` + classificação
- [ ] 16. View Tracker + Affinity Engine
- [ ] 17. Seleção ponderada (explore + max share)
- [ ] 18. Persistência/reset de afinidade
- [ ] 19. Teste de 1h+ com ads, views e assert de disco

---

## 17. Decisão de desenho recomendada (para não estourar 2GB)

1. **Não cachear a grade inteira** — só horizonte mínimo.
2. **Preferir 360p/480p** — mais vídeos possíveis e download mais rápido.
3. **1 playing + 1 ready** como estado saudável padrão.
4. **Apagar no término** — recuperação imediata de espaço.
5. **Fallback pequeno sempre residente** — última rede de segurança.
6. **Recusar/pular vídeos enormes** que não caibam junto com o atual + margem.
7. **Ads curtos e leves** — facilitam caber no teto e ficarem ready a tempo.
8. **Tipo + duração antes do download** — só busca/baixa propaganda depois de classificar o slot.
9. **Equivalência por busca tipada no YouTube** — não depende de anunciante real no MVP.
10. **Afinidade guia a busca, não o cache** — views escolhem o tipo; 2GB continua limitando quantos arquivos ficam prontos.
11. **Exploração mínima obrigatória** — evita loop eterno no mesmo tipo.

Com isso, o canal se comporta como playout automático de TV com grade comercial simplificada, recomendação por views, inventário físico limitado a 2GB e política agressiva de evicção.

---

## 18. Catálogo operacional rápido de propaganda (referência de implementação)

Use esta tabela como seed inicial do Ad Planner/Matcher:

| Tipo | Duração alvo | Queries seed (exemplos) |
|---|---|---|
| `spot_15` | 15s | `15 second commercial`, `propaganda 15 segundos` |
| `spot_30` | 30s | `30 second tv commercial`, `propaganda 30 segundos` |
| `spot_60` | 60s | `60 second commercial`, `filme publicitario 1 minuto` |
| `retail` | 30s | `retail store commercial`, `propaganda oferta loja` |
| `food_beverage` | 30s | `food commercial 30 seconds`, `propaganda comida bebida` |
| `tech` | 30s | `tech gadget commercial`, `propaganda celular tecnologia` |
| `auto` | 30–60s | `car commercial 30 seconds`, `propaganda carro` |
| `finance` | 30s | `bank commercial`, `propaganda banco cartao` |
| `beauty` | 15–30s | `beauty product ad`, `propaganda cosmetico` |
| `trailer` | 60s | `movie trailer 60 seconds`, `trailer oficial curto` |
| `event` | 15–30s | `event promo commercial`, `propaganda show evento` |
| `public_service` | 30s | `public service announcement`, `campanha utilidade publica` |
| `promo_house` | 10–20s | `channel bump promo`, ou arquivo local pinned |
| `generic_brand` | 15–30s | `brand commercial ad`, `propaganda marca` |

---

## 19. Próxima ação sugerida após este levantamento

Implementar na ordem:

1. **Fases 0–3** — base do canal contínuo com teto 2GB  
2. **Fases 4–6** — prefetch + resiliência + autopreenchimento  
3. **Fases 7–8** — propagandas com tipo/duração + busca de equivalente no YouTube  
4. **Fase 9** — afinidade por views (mais visto → mais entregar)  
5. **Fase 10** — endurecimento na máquina alvo
