# 🌊 FLOOD GUARD URBAN
### Sistema Inteligente de Monitoramento e Prevenção de Enchentes Urbanas

> Projeto Acadêmico — Estruturas de Dados | Python 3.11+

---

## 📋 Critérios atendidos

| # | Critério | Como está atendido |
|---|----------|--------------------|
| 1 | Definição do problema | Constante `PROBLEMA` exibida ao iniciar |
| 2 | Filas, Pilhas e Grafos com >30 informações | `REDE_NOS` (18×7=126) + `REDE_ARESTAS` (19×3=57) = **183 dados** |
| 3 | Lógica de resolução | BFS, Dijkstra adaptado, Método Racional |
| 4 | Funções `def` | 11 funções autônomas com toda a lógica do sistema |
| 5 | GitHub + documentação | Este repositório com docstrings em todas as funções |

---

## 1. Definição do Problema

Cidades brasileiras sofrem enchentes recorrentes que causam mortes, prejuízos bilionários e colapso de serviços públicos. São Paulo possui mais de 600 pontos de alagamento e registra prejuízos anuais acima de R$ 1 bilhão.

**Problema central:** ausência de um sistema integrado e preditivo — a resposta é sempre tardia e reativa.

**Solução:** FLOOD GUARD URBAN integra dados de satélites, sensores IoT e análise de grafos para monitorar, predizer e responder a enchentes em tempo real.

---

## 2. Estruturas de Dados (>30 informações)

### Grafo Dirigido Ponderado — Rede de Drenagem
Modelado como dicionário de adjacência com dados explícitos nas listas `REDE_NOS` e `REDE_ARESTAS`.

**`REDE_NOS` — 18 nós × 7 campos = 126 informações**
```
(id, nome, tipo, capacidade_m3s, bairro, latitude, longitude)
```

**`REDE_ARESTAS` — 19 arestas × 3 campos = 57 informações**
```
(origem, destino, capacidade_escoamento_m3s)
```

**Total: 183 informações explícitas no grafo.**

Diagrama simplificado da rede:
```
[N01 Cantareira] ──180→ [N03 Tietê Norte] ──300→ [N04 Tietê Centro] ──400→ [N15 Saída Mar]
[N02 Guarulhos]  ──120↗                            ↑90── [N08 Tamanduateí] ←─150── [N07 ABC]
                                                   ↑200─ [N10 Aricanduva]  ←─250── [N11 Piscinão]
                                                   ↑200─ [N12 Pinheiros]   ←─300── [N13 Guarapiranga]
```

### Fila de Prioridade (Max-Heap) — Triagem de Alertas
```python
fila = FilaPrioridade()
fila.inserir(prioridade=495, item=alerta_emergencia)   # risco 95%
fila.inserir(prioridade=268, item=alerta_atencao)      # risco 68%
fila.retirar()   # → retorna emergência primeiro
```
Implementada com `heapq` (min-heap com valores negados = max-heap).

### Pilha (LIFO Stack) — Histórico e Rollback
```python
pilha = Pilha()
pilha.empilhar({"tipo": "alerta_gerado", "no_id": "N07", "risco": 95})
pilha.empilhar({"tipo": "despacho", "equipe_id": "BM-01", "destino_id": "N07"})
pilha.desempilhar()   # rollback: cancela último despacho
```

### Fila FIFO (deque) — Despacho Sequencial de Equipes
```python
fila_eq = FilaFIFO()
fila_eq.enfileirar({"id": "BM-01", "tipo": "Bombeiros"})
fila_eq.enfileirar({"id": "DC-01", "tipo": "Defesa Civil"})
fila_eq.desenfileirar()   # → BM-01 (primeiro a entrar)
```

---

## 3. Lógica de Resolução

```
[Satélites + Sensores IoT]
         ↓
simular_leituras(grafo, cenario)   ← fatores por tipo de chuva
         ↓
calcular_risco(no)                 ← fórmula por faixa de ocupação
         ↓
gerar_alertas() → FilaPrioridade   ← nível 1 a 4 por risco
         ↓
prever_enchente() ← Método Racional + saturação da rede
         ↓
bfs_propagacao()  ← quais bairros serão atingidos
dijkstra_risco_maximo() ← ranking de impacto
         ↓
despachar_equipes() ← match alerta × equipe disponível
         ↓
exibir_relatorio() → Gestores de Defesa Civil
```

### Algoritmos
| Algoritmo | Onde | Para que serve |
|-----------|------|---------------|
| BFS | `bfs_propagacao()` | Simula propagação da enchente pela rede |
| Dijkstra (adaptado) | `dijkstra_risco_maximo()` | Calcula risco acumulado por bairro |
| Método Racional | `prever_enchente()` | Prevê volume de escoamento superficial |
| Max-Heap | `FilaPrioridade` | Garante atendimento por ordem de criticidade |

---

## 4. Funções `def`

| Função | O que faz |
|--------|-----------|
| `construir_grafo(nos, arestas)` | Monta o grafo de drenagem |
| `simular_leituras(grafo, cenario)` | Preenche níveis conforme o cenário climático |
| `calcular_risco(no)` | Calcula risco 0–100 de um nó |
| `atualizar_riscos(grafo)` | Recalcula risco em todos os nós |
| `bfs_propagacao(grafo, origem)` | BFS — nós atingíveis pela enchente |
| `dijkstra_risco_maximo(grafo, origem)` | Dijkstra — risco acumulado por bairro |
| `gerar_alertas(grafo, fila, pilha)` | Cria alertas e insere na fila de prioridade |
| `despachar_equipes(fila, fila_eq, pilha)` | Matching alerta × equipe disponível |
| `prever_enchente(grafo, mm, horas)` | Modelo preditivo com Método Racional |
| `exibir_relatorio(...)` | Relatório executivo para gestores |
| `main()` | Orquestra o fluxo completo |

---

## 5. Como Executar

```bash
# Clonar o repositório
git clone https://github.com/seu-usuario/flood-guard-urban.git
cd flood-guard-urban

# Sem dependências externas — apenas biblioteca padrão Python
python flood_guard.py
```

**Requisitos:** Python 3.11+

**Cenários disponíveis** (alterar em `main()`):
```python
cenario = "seco"            # ~10% capacidade
cenario = "chuva_leve"      # ~30%
cenario = "chuva_moderada"  # ~55%
cenario = "chuva_intensa"   # ~80%  ← padrão
cenario = "enchente"        # ~95%
```

---

## Estrutura do Repositório

```
flood-guard-urban/
├── flood_guard.py    ← sistema completo (único arquivo Python)
├── README.md         ← documentação completa
├── .gitignore        ← arquivos ignorados pelo Git
└── requirements.txt  ← dependências (apenas stdlib)
```

---

*Projeto Acadêmico — Estruturas de Dados e Algoritmos — 2026*
