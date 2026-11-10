# Programação de Televisão e Grade Comercial

Documento de referência com o conteúdo completo discutido sobre como funciona a programação de TV, a grade comercial, o tráfego de spots, as janelas nacional × afiliada e o modelo em software para um canal automático.

---

## 1. Como funciona a programação de televisão

A programação de televisão é o **plano do que vai ao ar, em que ordem e em quais horários**. Em resumo: alguém monta uma grade, encaixa conteúdos e a emissora transmite nessa sequência.

### 1.1 O que é a “programação”

É a **grade horária** do canal: novela às 21h, jornal às 20h, filme no fim de semana, etc. Cada bloco tem início, fim, duração e tipo (ao vivo, gravado, reprise, comercial).

### 1.2 Como a grade é montada

1. **Definição da grade**  
   A direção de programação decide faixas (manhã, tarde, noite, madrugada) e o perfil do público em cada horário.

2. **Aquisição / produção**  
   Conteúdo pode ser:
   - **produzido** pela própria emissora (jornal, novelas, reality)
   - **comprado** (séries, filmes, desenhos)
   - **licenciado** de outras empresas

3. **Encaixe na grade**  
   Cada programa ganha um **slot** (ex.: 20:30–21:15). O restante do tempo é preenchido com:
   - comerciais
   - vinhetas / chamadas
   - fills (encartes curtos se faltar tempo)

4. **Playout (ir ao ar)**  
   Na central técnica, um sistema de **playout** toca a sequência: programa → break comercial → volta ao programa. Pode ser ao vivo (estúdio/link) ou arquivo pré-gravado.

### 1.3 Partes técnicas básicas

| Elemento | Função |
|---|---|
| **Playlist / rundown** | Lista ordenada do que toca e quando |
| **Breaks** | Janelas de comercial dentro/entre programas |
| **As-run** | Registro do que realmente foi ao ar |
| **EPG** | Guia eletrônico (o que aparece na TV como “programação”) |

### 1.4 Ao vivo vs gravado

- **Ao vivo:** jornal, esportes, eventos — horário fixo, com risco de atraso; a grade se adapta.
- **Gravado:** novela, série, filme — duração conhecida; mais fácil de automatizar.
- **Misto:** programa ao vivo com blocos gravados e comerciais inseridos.

### 1.5 Quem decide o quê

- **Programação:** o que entra na grade e em que horário
- **Comercial:** quanto tempo de anúncio e em quais breaks
- **Jornalismo / esportes:** conteúdo ao vivo e prioridades
- **Operação / playout:** execução técnica no ar

### 1.6 Modelo “canal automático”

Em canais 24h (música, filmes, infantil, etc.), muita coisa é **automática**: uma playlist longa roda sozinha, com comerciais e vinhetas inseridos por software — sem apresentador ao vivo. É o mesmo princípio da grade, só que quase tudo é arquivo + regras.

---

## 2. Grade comercial

A **grade comercial** é o mapa de **onde e quanto tempo de anúncio** cabe na programação — e como isso vira dinheiro sem “furar” o horário dos programas.

### 2.1 O que ela define

Para cada dia/faixa/programa, a grade comercial marca:

- **Quantos breaks** existem
- **Duração** de cada break (ex.: 2 min, 3 min)
- **Posição** do break (antes, no meio, depois do programa)
- **Tipo de inventário** (nacional, local, patrocínio, merchandising)
- **Restrições** (não vender álcool em infantil, concorrentes no mesmo break, etc.)

Sem isso, a emissora não sabe o que pode vender nem o que o playout deve inserir.

### 2.2 Anatomia de um break

Um break típico não é só “comerciais em sequência”. Costuma ter:

1. **Abertura do break** (vinheta “intervalinho” / saída do programa)
2. **Spots comerciais** (15s, 30s, 60s…)
3. **Chamadas da casa** (promo de novelas, reality, etc.)
4. **Institucionais / utilidade pública** (às vezes)
5. **Volta ao programa** (vinheta de retorno)

A soma disso precisa caber no tempo reservado. Se vendeu 90s de spot num break de 120s, os 30s restantes viram chamadas, fill ou ficam “disponíveis” para última hora.

### 2.3 Tipos de inventário comercial

| Tipo | O que é | Quem vende |
|---|---|---|
| **Nacional** | Anúncio para toda a rede | Comercial da cabeça de rede |
| **Local / afiliada** | Anúncio só na praça | Comercial da afiliada |
| **Patrocínio** | Marca “apresenta” o programa | Pacote especial |
| **Merchandising** | Marca dentro do conteúdo | Comercial + produção |
| **Product placement** | Marca na cena/roteiro | Comercial + conteúdo |
| **Branded content** | Conteúdo feito para a marca | Comercial + criação |
| **Overspill / last minute** | Sobras de tempo | Venda rápida / fill |

Na TV aberta brasileira, o clássico é: **rede** manda o sinal com espaços; a **afiliada** pode inserir comerciais locais em janelas combinadas.

### 2.4 Como a grade comercial se encaixa na programação

Exemplo de um jornal das 20:00 às 20:45:

```text
20:00–20:12  Bloco 1 (conteúdo)
20:12–20:15  Break A (3 min)
20:15–20:27  Bloco 2
20:27–20:30  Break B (3 min)
20:30–20:42  Bloco 3
20:42–20:45  Break C / saída (ou encerramento)
```

A **grade de programação** define os blocos de conteúdo.  
A **grade comercial** define os breaks A/B/C e o inventário vendável dentro deles.

Se o jornal atrasa (ao vivo), a operação pode:

- encurtar um break
- cortar chamadas
- empurrar o próximo programa
- ou “comprimir” o fim

### 2.5 Unidades de venda (o produto)

O que o comercial vende não é “um vídeo”, é um **slot**:

- **Duração:** 5s, 10s, 15s, 30s, 60s…
- **Posição no break:** 1º lugar, meio, último (preços diferentes)
- **Programa / faixa:** novelão custa mais que madrugada
- **Alcance:** nacional vs praça
- **Pacote:** várias inserções ao longo da semana
- **Exclusividade:** concorrente fora do mesmo break/programa

Preço costuma seguir **audiência esperada** (GRP, ponto de audiência, CPM) + demanda da faixa.

### 2.6 Fluxo operacional (do contrato ao ar)

1. **Planejamento da grade** — define inventário do mês/semana
2. **Venda** — agências/anunciantes compram slots
3. **Tráfego / traffic** — monta a **playlist comercial** de cada break (ordem dos spots)
4. **Materiais** — chega o VT/arquivo do anúncio, com validade e versão
5. **Aprovação** — jurídico/comercial/qualidade (duração, áudio, conteúdo permitido)
6. **Playout** — no horário, o sistema insere o break
7. **As-run / comprovação** — registra o que realmente foi ao ar (para cobrança e relatório ao cliente)

O “tráfego” é o coração: transforma vendas em ordem cronológica tocável.

### 2.7 Regras que a grade precisa respeitar

- **Tempo máximo de comercial** por hora/programa (regulação e política da casa)
- **Separação de concorrentes** (dois refrigerantes no mesmo break, por exemplo)
- **Público-alvo / classificação** (não colocar produto adulto em faixa infantil)
- **Validade do material** (campanha só de 10 a 20; depois some)
- **Prioridade** (patrocinador > venda avulsa > chamada da casa)
- **Make-good:** se o spot não foi ao ar ou foi errado, a emissora “recompõe” com outra inserção

### 2.8 Nacional × local (visão geral)

Em rede:

- A cabeça de rede manda o programa com **janelas** marcadas
- Em alguns breaks, a afiliada **corta o sinal** e coloca comerciais locais
- Depois sincroniza de volta no programa

Se a afiliada atrasa 2 segundos, o retorno “come” o começo do próximo bloco. Por isso grade comercial e playout precisam de timing milimétrico.

### 2.9 Indicadores que a grade comercial controla

- **Inventário total** (quantos segundos dá para vender)
- **Ocupação** (% já vendido)
- **Yield** (receita por segundo disponível)
- **No-show / underdelivery** (vendeu audiência e não entregou)
- **Fill rate** (quanto do break foi preenchido vs sobrou)

Uma grade “cheia” demais aperta o conteúdo; “vazia” demais perde receita e enche de chamadas.

### 2.10 Resumo prático da grade comercial

A grade comercial responde a três perguntas:

1. **Onde** posso inserir anúncio?
2. **Quanto tempo** tenho em cada ponto?
3. **Quem** entra em cada segundo — e com qual prioridade?

É o contrato entre **dinheiro**, **experiência do espectador** e **execução técnica**.

As três linhas detalhadas a seguir aprofundam esse sistema:

1. Tráfego / playlist de spots
2. Janelas nacional × afiliada
3. Modelagem em software para canal automático

---

## 3. Tráfego e playlist de spots

### 3.1 O que é o tráfego

É o setor (ou módulo de software) que transforma **vendas comerciais** em uma **ordem executável** para o playout: “neste break, nesta ordem, estes arquivos, nestas durações”.

Sem tráfego, a grade comercial é só intenção. Com tráfego, vira playlist.

### 3.2 Entradas do tráfego

- Grade de programação (horários dos blocos e breaks)
- Grade/inventário comercial (duração e tipo de cada break)
- Pedidos de venda (ordem de inserção / IO)
- Materiais de anúncio (arquivos + metadados)
- Regras da casa (concorrentes, classificação, prioridades)
- Prioridades especiais (patrocínio, make-good, institucional)

### 3.3 Ciclo diário típico

1. Congela a grade do dia (ou da semana)
2. Confirma inventário vendável por break
3. Aloca os pedidos nos slots
4. Ordena os spots dentro de cada break
5. Valida materiais (existe? duração certa? vigente?)
6. Gera a playlist comercial
7. Envia ao playout / automação
8. Monitora o ar e trata falhas
9. Gera as-run para cobrança e comprovação

### 3.4 Unidade mínima: o spot

Cada item da playlist carrega algo como:

- ID do comercial / campanha
- Anunciante e produto
- Arquivo de mídia (versão correta)
- Duração real (ex.: 00:00:30:00)
- Break de destino (ex.: Jornal 20h — Break B)
- Posição desejada (1º, meio, último, “qualquer”)
- Vigência (de/até)
- Praça / rede
- Prioridade
- Restrições (não junto com concorrente X; não em infantil)

### 3.5 Como se monta a ordem dentro do break

Exemplo de break de 180 segundos:

| Ordem | Tipo | Duração | Motivo |
|---|---|---|---|
| 1 | Vinheta de saída | 5s | Identidade / transição |
| 2 | Spot A (patrocinador) | 30s | Prioridade contratual |
| 3 | Spot B | 30s | Venda premium (posição alta) |
| 4 | Spot C | 15s | Avulso |
| 5 | Spot D | 30s | Avulso |
| 6 | Chamada da casa | 20s | Fill / promoção |
| 7 | Spot E (make-good) | 30s | Compensação |
| 8 | Vinheta de retorno | 5s | Volta ao programa |
| | **Total** | **165s** | Sobram 15s de folga/fill |

### 3.6 Regras de ordenação (as mais usadas)

- **Prioridade contratual:** patrocínio > make-good > venda normal > chamada da casa
- **Posição comprada:** 1º e último costumam ser mais caros
- **Separação de concorrentes:** não colocar dois softdrinks seguidos (ou no mesmo break)
- **Variedade:** evitar 4 spots do mesmo setor em sequência
- **Duração exata:** a soma não pode estourar o break
- **Áudio/loudness e formato técnico:** se falha QC, o spot não entra
- **Vigência:** campanha expirada some automaticamente

### 3.7 Overbooking e underbooking

- **Overbooking:** vendeu mais segundos do que o break tem  
  Solução: empurrar para outro break, reduzir chamada da casa, negociar remanejamento, ou recusar venda extra.

- **Underbooking:** sobrou tempo  
  Solução: chamadas da emissora, institucionais, fills, ou oferta last-minute.

### 3.8 Make-good

Se o spot:

- não foi ao ar
- foi ao ar truncado
- foi a versão errada
- ou foi em programa/faixa errada

o tráfego agenda uma **reposição** equivalente (ou melhor, conforme contrato). Isso entra com prioridade alta na playlist seguinte.

### 3.9 As-run (comprovação)

Depois do ar, o sistema registra:

- o que estava previsto
- o que realmente tocou
- horário exato de início/fim
- se houve corte, black, falha de arquivo

Esse log alimenta faturamento, relatório para agência e auditoria.

### 3.10 Papéis humanos (mesmo com software)

- **Executivo comercial:** vende
- **Tráfego:** aloca e ordena
- **Operação/playout:** executa e trata emergência
- **Qualidade:** aprova material
- **Financeiro:** cobra com base no as-run

---

## 4. Janelas nacional × afiliada

### 4.1 O problema que isso resolve

Uma rede quer um jornal nacional único, mas cada cidade precisa vender comerciais locais (loja da esquina, política local, varejo da praça). A solução é a **janela local**: um intervalo em que a afiliada pode “tomar” o sinal e inserir o próprio break.

### 4.2 Modelo mental

```text
[REDE]  conteúdo nacional -----> break nacional -----> conteúdo nacional
                                      |
                                      v
[AFILIADA]                    corta sinal e põe break local
                                      |
                                      v
[REDE]                    retoma no ponto combinado (sync)
```

### 4.3 Tipos de break na prática

1. **Break só nacional**  
   Toda a rede vê os mesmos anunciantes. Afiliada não corta.

2. **Break só local**  
   A rede manda “buraco” (slate/preto/tom) ou sinal com permissão de corte; a afiliada preenche 100% com comerciais locais.

3. **Break misto**  
   Parte nacional + parte local no mesmo intervalo (mais delicado de sincronizar).

4. **Break opt-out / opt-in**  
   A afiliada pode optar por inserir local ou deixar o feed nacional passar.

### 4.4 Sinalização e sincronismo

Para a afiliada saber **quando cortar e quando voltar**, usa-se:

- **Cue tones / DTMF / tones de automação**
- **SCTE markers** (comum em fluxos digitais/IP)
- **Playlist/rundown compartilhado** com horários nominais
- Em fluxos modernos: mensagens de automação (GPI, API, metadata no transporte)

O essencial é um protocolo claro:

- “inicia janela local em T”
- “duração = N segundos”
- “retorne ao programa em T+N”

### 4.5 O que a afiliada precisa ter pronto

- Playlist local do break
- Materiais locais aprovados
- Tempo exatamente igual (ou controlado) ao da janela
- Plano B: se faltar material, tocar fill/chamada local ou devolver o sinal nacional

### 4.6 Riscos clássicos de dessync

| Problema | Efeito na tela |
|---|---|
| Afiliada volta atrasada | Começa o próximo bloco no meio da frase |
| Afiliada volta adiantada | Corta o fim do break nacional / entra cedo demais |
| Duração local maior que a janela | Estoura e come conteúdo |
| Duração local menor | Fica preto, freeze ou “buraco” |
| Falha de cue | Não corta (fica nacional) ou corta na hora errada |

Por isso a operação trata janela local como evento crítico de timing.

### 4.7 Quem fatura o quê

- **Rede:** vende e fatura inventário nacional
- **Afiliada:** vende e fatura inventário local da sua praça

Contratos de afiliação definem:

- quantas janelas locais existem
- duração
- se a afiliada é obrigada a cortar
- se paga/recebe participação sobre nacional
- regras de conteúdo político/eleitoral na praça

### 4.8 Exemplo de uma hora de jornal em rede

```text
20:00-20:10  Bloco 1 nacional
20:10-20:13  Break nacional (rede)
20:13-20:23  Bloco 2 nacional
20:23-20:26  Janela local (afiliada)
20:26-20:36  Bloco 3 nacional
20:36-20:39  Break misto (90s rede + 90s local)
20:39-20:45  Bloco final nacional
```

Nesse exemplo, a afiliada só “assume o ar” nas janelas locais/mistas; no resto, retransmite a rede.

### 4.9 Casos especiais

- **Ao vivo com atraso:** a rede pode encurtar break; a afiliada precisa seguir o cue, não o relógio de parede
- **Evento esportivo:** janelas mudam conforme o jogo
- **Eleições:** regras rígidas de inserção local e tempo político
- **Canal 24h / cabo / streaming linear:** muitas vezes não há afiliada; o “local” vira segmentação por região via servidor de ad insertion

---

## 5. Como modelar isso num canal automático (software)

A ideia é transformar grade comercial + tráfego + janelas em **dados + motor de decisão + playout**.

### 5.1 Arquitetura em camadas

1. **Cadastro** — anunciantes, campanhas, materiais, restrições
2. **Inventário** — breaks e segundos vendáveis
3. **Vendas / orders** — o que foi comprado
4. **Scheduler / tráfego** — aloca e ordena
5. **Playout** — executa a timeline
6. **As-run + billing** — prova e cobra

### 5.2 Modelo de dados (essencial)

**Channel**  
Canal, timezone, normas de loudness, FPS.

**Program / ScheduleItem**  
Item da grade: início, fim, tipo (programa, vinheta, break), se é ao vivo ou arquivo.

**Break**  
Pertence a um ScheduleItem (ou fica entre dois). Campos típicos:

- `start_at` / `duration`
- `inventory_type`: national | local | mixed
- `max_ad_ms`
- `allow_house_promo`
- `region_scope`

**Campaign / OrderLine**  
Pedido comercial:

- `advertiser_id`
- `media_asset_id`
- `duration_ms`
- `priority`
- `flight_start` / `flight_end`
- `target_breaks` / `target_dayparts`
- `position_preference`
- `frequency_cap`
- `competitor_category`
- `price` / `deal_id`

**MediaAsset**  
Arquivo + QC status + vigência + duração real medida.

**Restriction**  
Regras: “categoria cerveja ≠ faixa infantil”, “concorrente A ≠ concorrente B no mesmo break”, etc.

**Playlist / BreakPlaylist**  
Resultado do tráfego para um break específico: lista ordenada de itens.

**AsRunEvent**  
O que tocou de fato.

### 5.3 Algoritmo de tráfego (versão prática)

Para cada break do dia:

1. Calcular `available_ms`
2. Buscar order lines elegíveis (vigentes, região ok, material aprovado)
3. Filtrar por restrições do programa/faixa
4. Ordenar candidatos por prioridade (make-good, patrocínio, CPM/yield, prazo de entrega)
5. Encaixar spots sem estourar `available_ms`
6. Resolver posições (primeiro/último) se compradas
7. Separar concorrentes (reordenar ou trocar de break)
8. Preencher sobra com house promo / fill
9. Gerar playlist final e trava (lock) perto do horário

### 5.4 Pseudomodelo de playlist

```text
BreakPlaylist
  break_id
  total_duration
  items[]:
    - type: slate | ad | house_promo | tip | bumper
      asset_id
      duration
      order_line_id?
      must_air: true/false
```

### 5.5 Motor de playout

Uma timeline contínua:

```text
[programa][bumper out][ad][ad][promo][bumper in][programa]...
```

No automático:

- quase tudo é arquivo
- clock-based (relógio) ou sequence-based (encadeado)
- se um ad falha no QC em cima da hora: hot-swap para promo/fill
- se o item estoura duração: trim/cut policy definida

### 5.6 Nacional × “local” no mundo automático

Sem afiliada física, o equivalente é **ad insertion segmentada**:

- Master playlist nacional
- Em cada break, o servidor escolhe criativos por região/usuário/dispositivo
- Em TV linear IP/cabo: SSAI/CSAI ou inserter regional
- Em canal playout único: um schedule por praça (N canais lógicos)

Modelos comuns:

- **1 playlist por região**
- **1 playlist master + decisioning no break**
- **híbrido:** base nacional + overlays locais

### 5.7 Políticas que o software precisa ter explícitas

- Estourou o break? cortar o quê primeiro?
- Faltou material? quem substitui?
- Make-good automático ou manual?
- Qual o máximo de house promo por hora?
- Pode juntar concorrentes em último caso?
- Breaks ao vivo podem encolher? como recalcular?

### 5.8 Mínimo viável para um canal automático com grade comercial

1. Grade diária com programas + breaks
2. Cadastro de assets e duração real
3. Orders com vigência e prioridade
4. Gerador de playlist por break
5. Player/playout que respeita a timeline
6. As-run CSV/JSON
7. Painel simples de ocupação (% vendido por faixa)

### 5.9 Evolução natural do sistema

- Yield optimization (escolher o anúncio que paga mais)
- Frequência por anunciante
- A/B de posição
- Relatórios de delivery (quanto do contratado foi entregue)
- APIs para agência enviar material e receber as-run
- Markers SCTE se for integrar com distribuidores

### 5.10 Exemplo de fluxo ponta a ponta no software

1. Programação cria: “Filme 21:00–22:30, breaks em 21:25 e 22:00 (120s cada)”
2. Comercial vende 6x30s nessa faixa
3. Tráfego aloca 3 spots no break 1 e 3 no break 2
4. Scheduler gera playlists
5. Playout toca filme → break → filme → break → filme
6. As-run confirma 6 inserções
7. Billing fecha a campanha

---

## 6. Como as três linhas se conectam

```text
Venda comercial
    ↓
Tráfego monta playlist de spots
    ↓
Break nacional/local define QUEM executa a playlist
    ↓
Playout (rede e/ou afiliada / motor automático) coloca no ar
    ↓
As-run comprova e alimenta cobrança + make-good
```

- **Tráfego** responde: *o que toca dentro do break*
- **Janela nacional/local** responde: *quem controla aquele pedaço do ar*
- **Software do canal automático** responde: *como isso vira regras, dados e execução 24h*

---

## 7. Glossário rápido

| Termo | Significado |
|---|---|
| **Grade** | Mapa horário do que vai ao ar |
| **Break** | Intervalo reservado a comerciais/vinhetas |
| **Spot** | Anúncio individual (ex.: 30s) |
| **Inventário** | Segundos disponíveis para venda |
| **Tráfego (traffic)** | Alocação e ordenação dos spots |
| **Playout** | Sistema que executa a timeline no ar |
| **As-run** | Registro do que realmente foi ao ar |
| **Make-good** | Reposição de inserção falha/errada |
| **House promo / chamada** | Divulgação da própria emissora |
| **Fill** | Conteúdo curto para completar tempo |
| **Janela local** | Intervalo em que a afiliada insere comerciais da praça |
| **Cue / SCTE** | Sinalização de corte/retorno de break |
| **EPG** | Guia eletrônico de programação |
| **Yield** | Receita obtida por unidade de inventário |
| **SSAI / CSAI** | Inserção de ads no servidor / no cliente (mundos IP/streaming) |

---

## 8. Próximos passos possíveis (implementação)

A partir deste documento, os desdobramentos naturais para o projeto **Canal automato** são:

1. Modelar o **banco de dados** (tabelas/campos) a partir da seção 5.2
2. Especificar uma **API de scheduler/tráfego**
3. Implementar o **MVP** da seção 5.8
4. Definir políticas operacionais da seção 5.7 como regras de negócio versionadas

---

*Documento consolidado a partir da conversa sobre programação de televisão, grade comercial, tráfego, janelas nacional/afiliada e modelagem de canal automático.*
