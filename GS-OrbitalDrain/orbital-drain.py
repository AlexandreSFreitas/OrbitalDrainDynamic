"""
ORBITAL DRAIN
Sistema de monitoramento e prevenção de enchentes urbanas.

Projeto Acadêmico — Estruturas de Dados
GitHub: https://github.com/seu-usuario/orbital-drain


"""

import heapq
from collections import deque
from datetime import datetime
import random


PROBLEMA = """
╔══════════════════════════════════════════════════════════════════╗
║              ORBITAL DRAIN — DEFINIÇÃO DO PROBLEMA          ║
╚══════════════════════════════════════════════════════════════════╝

 CONTEXTO:
   Cidades brasileiras sofrem enchentes recorrentes que provocam:
   • Mortes e desaparecimentos de cidadãos
   • Prejuízos bilionários (São Paulo: >R$1 bi/ano)
   • Colapso da mobilidade urbana e serviços de saúde
   • Deslocamento forçado de populações vulneráveis

 PROBLEMA CENTRAL:
   Ausência de um sistema integrado e PREDITIVO que permita que
   prefeituras e defesa civil ajam ANTES da enchente.
   Atualmente a resposta é tardia e reativa.

 CAUSAS:
   1. Monitoramento fragmentado da rede de drenagem urbana
   2. Dados de satélite, pluviômetros e sensores não integrados
   3. Comunicação ineficiente entre órgãos responsáveis
   4. Sem priorização automática no despacho de equipes de socorro
   5. Histórico de eventos subutilizado para predição

 SOLUÇÃO — ORBITAL DRAIN:
   Sistema que usa GRAFOS (rede de drenagem), FILA DE PRIORIDADE
   (triagem de alertas), PILHA (histórico e rollback de planos)
   e FILA FIFO (despacho de equipes) para monitorar, predizer e
   responder a enchentes urbanas em tempo real.
"""


REDE_NOS = [
    ("N01", "Bacia Cantareira",            "bacia",         500.0, "Santana",         -23.42, -46.55),
    ("N02", "Bacia Guarulhos",             "bacia",         350.0, "Guarulhos",       -23.46, -46.53),
    ("N03", "Rio Tietê — Trecho Norte",    "rio",           800.0, "Tucuruvi",        -23.48, -46.58),
    ("N04", "Rio Tietê — Centro",          "rio",           950.0, "Barra Funda",     -23.54, -46.66),
    ("N05", "Piscinão Itaquera",           "piscinhao",     600.0, "Itaquera",        -23.55, -46.44),
    ("N06", "Galeria Central Paulista",    "galeria",       250.0, "Centro",          -23.55, -46.64),
    ("N07", "Bacia ABC Paulista",          "bacia",         420.0, "Santo André",     -23.66, -46.51),
    ("N08", "Rio Tamanduateí",             "rio",           380.0, "Mooca",           -23.55, -46.62),
    ("N09", "Pto. Crítico — Vl. Formosa", "ponto_critico", 120.0, "Vila Formosa",    -23.57, -46.54),
    ("N10", "Rio Aricanduva",              "rio",           310.0, "Penha",           -23.57, -46.46),
    ("N11", "Piscinão Aricanduva",         "piscinhao",     700.0, "Aricanduva",      -23.56, -46.47),
    ("N12", "Rio Pinheiros",               "rio",           520.0, "Pinheiros",       -23.58, -46.70),
    ("N13", "Represa Guarapiranga",        "piscinhao",     900.0, "Interlagos",      -23.72, -46.72),
    ("N14", "Pto. Crítico — Brooklin",    "ponto_critico",  90.0, "Brooklin",        -23.62, -46.69),
    ("N15", "Saída Mar — Canal Santos",    "saida",        1200.0, "Baixada Santista",-23.98, -46.30),
    ("N16", "Bacia Butantã",              "bacia",         280.0, "Butantã",         -23.58, -46.73),
    ("N17", "Galeria Subterrânea Sul",    "galeria",        180.0, "Jabaquara",       -23.64, -46.65),
    ("N18", "Pto. Crítico — Mooca",       "ponto_critico",  80.0, "Mooca",           -23.55, -46.60),
]

REDE_ARESTAS = [
    ("N01", "N03", 180.0),
    ("N02", "N03", 120.0),
    ("N03", "N04", 300.0),
    ("N04", "N08",  90.0),
    ("N04", "N15", 400.0),
    ("N05", "N10", 200.0),
    ("N06", "N04",  80.0),
    ("N07", "N08", 150.0),
    ("N08", "N04", 180.0),
    ("N08", "N18",  40.0),
    ("N09", "N08",  30.0),
    ("N10", "N04", 120.0),
    ("N11", "N10", 250.0),
    ("N12", "N04", 200.0),
    ("N13", "N12", 300.0),
    ("N14", "N12",  50.0),
    ("N16", "N12",  90.0),
    ("N17", "N12",  60.0),
    ("N18", "N04",  35.0),
]



class FilaPrioridade:
    """
    Fila de prioridade (max-heap) para triagem de alertas.
    Alertas mais críticos saem primeiro, independente da ordem de chegada.
    Implementada com heapq usando valores negados para simular max-heap.
    """
    def __init__(self):
        self._heap = []
        self._seq  = 0

    def inserir(self, prioridade: int, item: dict) -> None:
        self._seq += 1
        heapq.heappush(self._heap, (-prioridade, self._seq, item))

    def retirar(self) -> dict | None:
        if self._heap:
            return heapq.heappop(self._heap)[2]
        return None

    def espiar(self) -> dict | None:
        return self._heap[0][2] if self._heap else None

    def tamanho(self) -> int:
        return len(self._heap)

    def vazia(self) -> bool:
        return len(self._heap) == 0

    def listar(self) -> list:
        return [item[2] for item in sorted(self._heap)]


class Pilha:
    """
    Pilha LIFO para histórico de eventos do sistema.
    Permite rollback: reverter o último plano de evacuação caso
    haja mudança de cenário ou erro operacional.
    """
    def __init__(self):
        self._dados = []
        self.total  = 0

    def empilhar(self, item: dict) -> None:
        item["seq"]       = self.total + 1
        item["timestamp"] = datetime.now().strftime("%H:%M:%S")
        self._dados.append(item)
        self.total += 1

    def desempilhar(self) -> dict | None:
        return self._dados.pop() if self._dados else None

    def topo(self) -> dict | None:
        return self._dados[-1] if self._dados else None

    def tamanho(self) -> int:
        return len(self._dados)

    def vazia(self) -> bool:
        return len(self._dados) == 0

    def recentes(self, n: int = 5) -> list:
        return list(reversed(self._dados[-n:]))


class FilaFIFO:
    """
    Fila FIFO para sequenciamento de despacho de equipes de socorro.
    Garante que bombeiros e defesa civil sejam despachados
    na ordem em que ficaram disponíveis.
    """
    def __init__(self):
        self._fila       = deque()
        self.despachados = 0

    def enfileirar(self, item: dict) -> None:
        self._fila.append(item)

    def desenfileirar(self) -> dict | None:
        if self._fila:
            self.despachados += 1
            return self._fila.popleft()
        return None

    def tamanho(self) -> int:
        return len(self._fila)

    def vazia(self) -> bool:
        return len(self._fila) == 0

    def listar(self) -> list:
        return list(self._fila)



def construir_grafo(nos: list, arestas: list) -> dict:
    """
    Monta o grafo de drenagem como dicionário de adjacência.
    Cada entrada representa um ponto da rede com seus atributos
    e a lista de conexões de saída (vizinhos).
    """
    grafo = {}

    for no_id, nome, tipo, cap, bairro, lat, lon in nos:
        grafo[no_id] = {
            "id":        no_id,
            "nome":      nome,
            "tipo":      tipo,
            "capacidade": cap,
            "bairro":    bairro,
            "lat":       lat,
            "lon":       lon,
            "nivel":     0.0,
            "risco":     0,
            "em_alerta": False,
            "vizinhos":  []
        }

    for origem, destino, cap_esc in arestas:
        if origem in grafo and destino in grafo:
            grafo[origem]["vizinhos"].append({
                "destino":    destino,
                "capacidade": cap_esc,
                "vazao":      0.0
            })

    return grafo


def simular_leituras(grafo: dict, cenario: str = "chuva_intensa") -> None:
    """
    Preenche o nível de cada nó simulando leituras de sensores IoT e satélite.
    O cenário define o fator base de ocupação da rede.
    """
    fatores = {
        "seco":           0.10,
        "chuva_leve":     0.30,
        "chuva_moderada": 0.55,
        "chuva_intensa":  0.80,
        "enchente":       0.95,
    }
    base = fatores.get(cenario, 0.55)

    for no in grafo.values():
        variacao    = random.uniform(-0.05, 0.10)
        fator       = min(1.0, base + variacao)
        no["nivel"] = round(no["capacidade"] * fator, 2)


def calcular_risco(no: dict) -> int:
    """
    Calcula o índice de risco de um nó de 0 a 100,
    com base na proporção entre nível atual e capacidade máxima.

    Faixas:
        ocupação >= 90% → risco 100
        ocupação >= 75% → risco 60 a 99
        ocupação >= 50% → risco 30 a 59
        ocupação <  50% → risco 0 a 29
    """
    if no["capacidade"] == 0:
        return 0

    ocupacao = (no["nivel"] / no["capacidade"]) * 100

    if ocupacao >= 90:
        risco = 100
    elif ocupacao >= 75:
        risco = int(60 + (ocupacao - 75) * 2.66)
    elif ocupacao >= 50:
        risco = int(30 + (ocupacao - 50) * 1.2)
    else:
        risco = int(ocupacao * 0.6)

    no["risco"] = risco
    return risco


def atualizar_riscos(grafo: dict) -> None:
    """Recalcula o risco de todos os nós do grafo."""
    for no in grafo.values():
        calcular_risco(no)


def bfs_propagacao(grafo: dict, origem_id: str) -> list:
    """
    Busca em Largura (BFS) para mapear quais nós serão atingidos
    quando uma enchente começa em origem_id.
    Retorna os nós em ordem de alcance pelo fluxo da água.
    """
    if origem_id not in grafo:
        return []

    visitados = set()
    fila_bfs  = deque([origem_id])
    ordem     = []

    while fila_bfs:
        atual = fila_bfs.popleft()
        if atual in visitados:
            continue
        visitados.add(atual)
        ordem.append(atual)

        for viz in grafo[atual]["vizinhos"]:
            if viz["destino"] not in visitados:
                fila_bfs.append(viz["destino"])

    return ordem


def dijkstra_risco_maximo(grafo: dict, origem_id: str) -> dict:
    """
    Adaptação do Dijkstra para encontrar o caminho de maior risco
    acumulado a partir de um ponto de origem.
    Usa max-heap (heapq com valores negados) para expandir sempre
    o nó de maior risco ainda não visitado.
    Retorna {no_id: risco_acumulado} para cada nó alcançável.
    """
    if origem_id not in grafo:
        return {}

    acumulado = {nid: 0 for nid in grafo}
    acumulado[origem_id] = grafo[origem_id]["risco"]
    visitados = set()
    heap = [(-acumulado[origem_id], origem_id)]

    while heap:
        neg_risco, atual = heapq.heappop(heap)
        if atual in visitados:
            continue
        visitados.add(atual)

        for viz in grafo[atual]["vizinhos"]:
            dest = viz["destino"]
            novo = acumulado[atual] + grafo[dest]["risco"]
            if novo > acumulado[dest]:
                acumulado[dest] = novo
                heapq.heappush(heap, (-novo, dest))

    return acumulado


def gerar_alertas(grafo: dict, fila: FilaPrioridade, pilha: Pilha) -> int:
    """
    Varre os nós do grafo e cria alertas para aqueles com risco >= 30.
    Cada alerta é inserido na fila de prioridade e registrado na pilha.

    Níveis: risco >= 90 → EMERGÊNCIA | >= 70 → ALERTA | >= 50 → ATENÇÃO | >= 30 → OBSERVAÇÃO
    Prioridade = nível × 100 + risco, para desempate por gravidade.
    """
    NIVEIS   = {4: "EMERGÊNCIA", 3: "ALERTA", 2: "ATENÇÃO", 1: "OBSERVAÇÃO"}
    CORES    = {4: "🔴", 3: "🟠", 2: "🟡", 1: "🟢"}
    contador = 0

    for no_id, no in grafo.items():
        risco = no["risco"]
        if risco < 30:
            continue

        if risco >= 90:
            nivel = 4
            msg   = f"EMERGÊNCIA: {no['nome']} em colapso! Evacuar área imediatamente."
        elif risco >= 70:
            nivel = 3
            msg   = f"ALERTA: {no['nome']} com risco elevado. Acionar equipes."
        elif risco >= 50:
            nivel = 2
            msg   = f"ATENÇÃO: {no['nome']} em monitoramento intensivo."
        else:
            nivel = 1
            msg   = f"OBSERVAÇÃO: {no['nome']} acima do nível normal."

        prioridade = nivel * 100 + risco
        alerta = {
            "id":        f"ALT-{contador+1:04d}",
            "no_id":     no_id,
            "nome":      no["nome"],
            "bairro":    no["bairro"],
            "nivel":     nivel,
            "nivel_str": NIVEIS[nivel],
            "cor":       CORES[nivel],
            "risco":     risco,
            "mensagem":  msg,
            "hora":      datetime.now().strftime("%H:%M:%S"),
        }

        fila.inserir(prioridade, alerta)
        no["em_alerta"] = True

        pilha.empilhar({
            "tipo":   "alerta_gerado",
            "alerta": alerta["id"],
            "no_id":  no_id,
            "nivel":  nivel,
            "risco":  risco,
        })

        contador += 1

    return contador


def despachar_equipes(fila_alertas: FilaPrioridade,
                       fila_equipes: FilaFIFO,
                       pilha: Pilha) -> list:
    """
    Consome os alertas em ordem de prioridade e despacha equipes
    disponíveis para os pontos de risco. Registra cada despacho na pilha.
    """
    despachos = []

    while not fila_alertas.vazia() and not fila_equipes.vazia():
        alerta = fila_alertas.retirar()
        equipe = fila_equipes.desenfileirar()

        despacho = {
            "equipe_id":   equipe["id"],
            "tipo_equipe": equipe["tipo"],
            "destino_id":  alerta["no_id"],
            "destino":     alerta["nome"],
            "bairro":      alerta["bairro"],
            "nivel":       alerta["nivel"],
            "nivel_str":   alerta["nivel_str"],
            "cor":         alerta["cor"],
            "risco":       alerta["risco"],
            "hora":        datetime.now().strftime("%H:%M:%S"),
        }
        despachos.append(despacho)

        pilha.empilhar({
            "tipo":       "despacho",
            "equipe_id":  equipe["id"],
            "destino_id": alerta["no_id"],
            "nivel":      alerta["nivel"],
        })

    return despachos


def prever_enchente(grafo: dict, precipitacao_mm: float, duracao_horas: float) -> dict:
    """
    Modelo preditivo baseado no Método Racional de Hidrologia,
    combinado com o grau de saturação atual da rede de drenagem.

    Q = C × i × A  (simplificado)
      C = 0.72  coeficiente de impermeabilização urbana (São Paulo)
      i = intensidade de chuva
      A = representado pela duração e escoamento médio

    Retorna probabilidade de enchente, janela temporal e ação recomendada.
    """
    C_IMPERMEABILIZACAO = 0.72
    C_ESCOAMENTO        = 0.65

    volume       = precipitacao_mm * C_IMPERMEABILIZACAO * C_ESCOAMENTO * duracao_horas
    cap_restante = sum(no["capacidade"] - no["nivel"] for no in grafo.values()) / len(grafo)
    nos_criticos = [n for n in grafo.values() if n["risco"] >= 70]
    pct_saturado = len(nos_criticos) / len(grafo) * 100

    fator_vol = min(1.0, volume / (cap_restante + 1))
    prob      = round((fator_vol * 0.6 + (pct_saturado / 100) * 0.4) * 100, 1)

    if prob >= 80:
        janela = "CRÍTICO — enchente em menos de 2 horas"
        acao   = "EVACUAR imediatamente as zonas de risco"
    elif prob >= 60:
        janela = "ALTO — enchente em 2 a 6 horas"
        acao   = "Acionar equipes e alertar população via sirenes"
    elif prob >= 40:
        janela = "MODERADO — possível alagamento em 6 a 12 horas"
        acao   = "Pré-posicionar equipes e monitorar intensivamente"
    else:
        janela = "BAIXO — sem risco imediato"
        acao   = "Manter monitoramento padrão"

    return {
        "precipitacao_mm":    precipitacao_mm,
        "duracao_horas":      duracao_horas,
        "volume_escoamento":  round(volume, 2),
        "cap_restante_media": round(cap_restante, 2),
        "nos_criticos":       len(nos_criticos),
        "pct_saturado":       round(pct_saturado, 1),
        "probabilidade":      prob,
        "janela":             janela,
        "acao":               acao,
        "hora":               datetime.now().strftime("%H:%M:%S"),
    }


def exibir_relatorio(grafo: dict,
                      fila: FilaPrioridade,
                      pilha: Pilha,
                      despachos: list,
                      previsao: dict,
                      cenario: str) -> None:
    """Exibe o relatório executivo consolidado para gestores de defesa civil."""
    SEP = "═" * 66

    print(f"\n{SEP}")
    print("  ORBITAL DRAIN — RELATÓRIO EXECUTIVO")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} | Cenário: {cenario.upper()}")
    print(SEP)

    riscos      = [n["risco"] for n in grafo.values()]
    n_criticos  = len([r for r in riscos if r >= 70])
    risco_medio = sum(riscos) / len(riscos)

    print(f"\n{'─'*25} REDE DE DRENAGEM {'─'*22}")
    print(f"  🏙️  Cidade           : São Paulo — SP")
    print(f"  🔵  Nós monitorados  : {len(grafo)}")
    print(f"  ↔️  Arestas (fluxos) : {sum(len(n['vizinhos']) for n in grafo.values())}")
    print(f"  📊  Risco médio      : {risco_medio:.1f}%")
    print(f"  🔴  Risco máximo     : {max(riscos)}%")
    print(f"  ⚠️  Nós críticos     : {n_criticos}")

    print(f"\n{'─'*25} MAPA DE RISCO (Top 10) {'─'*17}")
    ordenados = sorted(grafo.values(), key=lambda x: x["risco"], reverse=True)[:10]
    for no in ordenados:
        r     = no["risco"]
        barra = "█" * (r // 10) + "░" * (10 - r // 10)
        flag  = " ⚠️" if no["em_alerta"] else ""
        print(f"  {barra} {r:3d}% │ {no['nome'][:32]:<32} ({no['bairro']}){flag}")

    print(f"\n{'─'*25} FILA DE ALERTAS {'─'*23}")
    print(f"  Pendentes na fila : {fila.tamanho()}")
    for al in fila.listar()[:5]:
        print(f"  {al['cor']} [{al['nivel_str']:<11}] {al['nome'][:32]:<32} risco={al['risco']}%")

    print(f"\n{'─'*25} DESPACHO DE EQUIPES {'─'*20}")
    print(f"  Total despachados : {len(despachos)}")
    for d in despachos:
        print(f"  {d['cor']} {d['equipe_id']} ({d['tipo_equipe']:<12}) "
              f"→ {d['destino'][:28]:<28} [{d['nivel_str']}]")

    print(f"\n{'─'*25} MODELO PREDITIVO IA {'─'*19}")
    print(f"  💧  Precipitação     : {previsao['precipitacao_mm']} mm")
    print(f"  ⏱️  Duração          : {previsao['duracao_horas']} horas")
    print(f"  🌊  Volume escoamento: {previsao['volume_escoamento']} m³")
    print(f"  🎯  Probabilidade    : {previsao['probabilidade']}%")
    print(f"  ⏰  Janela temporal  : {previsao['janela']}")
    print(f"  📋  Ação recomendada : {previsao['acao']}")

    print(f"\n{'─'*25} PILHA DE HISTÓRICO {'─'*21}")
    print(f"  Total de eventos  : {pilha.total}")
    print(f"  Na pilha agora    : {pilha.tamanho()}")
    for ev in pilha.recentes(5):
        print(f"  #{ev['seq']:>3} [{ev['timestamp']}] {ev['tipo']}")

    criticos = [n for n in grafo.values() if n["risco"] >= 70]
    if criticos:
        pior = max(criticos, key=lambda x: x["risco"])
        bfs  = bfs_propagacao(grafo, pior["id"])
        dijk = dijkstra_risco_maximo(grafo, pior["id"])

        print(f"\n{'─'*25} PROPAGAÇÃO DE RISCO {'─'*19}")
        print(f"  Epicentro : {pior['nome']} — risco {pior['risco']}%")
        print(f"  Nós atingíveis via BFS: {len(bfs)}")
        print("  Top 5 nós por risco acumulado (Dijkstra):")
        top5 = sorted(
            [(nid, dijk[nid]) for nid in bfs if dijk[nid] > 0],
            key=lambda x: x[1], reverse=True
        )[:5]
        for nid, racum in top5:
            print(f"    • {grafo[nid]['nome'][:38]:<38} acumulado={racum}")

    print(f"\n{SEP}")
    print("  ✅  Relatório concluído. Sistema ativo e monitorando.")
    print(SEP)


def main():
    """Orquestra o fluxo completo do sistema ORBITAL DRAIN."""
    print(PROBLEMA)
    input("  [ Pressione ENTER para iniciar a simulação ] ")

    cenario = "chuva_intensa"

    print("\n  ⚙️  Construindo grafo da rede de drenagem...")
    grafo = construir_grafo(REDE_NOS, REDE_ARESTAS)
    print(f"      → {len(grafo)} nós | {len(REDE_ARESTAS)} arestas criados.")

    print(f"  🌧️  Simulando cenário: {cenario.upper()}...")
    simular_leituras(grafo, cenario)

    print("  📊  Calculando risco em cada nó...")
    atualizar_riscos(grafo)

    fila  = FilaPrioridade()
    pilha = Pilha()
    print("  🚨  Gerando alertas para pontos críticos...")
    n = gerar_alertas(grafo, fila, pilha)
    print(f"      → {n} alertas inseridos na fila de prioridade.")

    fila_equipes = FilaFIFO()
    for eq in [
        {"id": "BM-01", "tipo": "Bombeiros"},
        {"id": "DC-01", "tipo": "Defesa Civil"},
        {"id": "BM-02", "tipo": "Bombeiros"},
        {"id": "DC-02", "tipo": "Defesa Civil"},
        {"id": "AM-01", "tipo": "Ambulância"},
        {"id": "ENG-1", "tipo": "Engenharia"},
    ]:
        fila_equipes.enfileirar(eq)

    print("  🚒  Despachando equipes de socorro...")
    despachos = despachar_equipes(fila, fila_equipes, pilha)
    print(f"      → {len(despachos)} equipes despachadas.")

    print("  🤖  Executando modelo preditivo...")
    previsao = prever_enchente(grafo, precipitacao_mm=85.0, duracao_horas=3.5)

    exibir_relatorio(grafo, fila, pilha, despachos, previsao, cenario)

    print("\n  🔄  Demonstração de ROLLBACK (desempilhar último evento):")
    ultimo = pilha.desempilhar()
    if ultimo:
        print(f"      Evento revertido: #{ultimo['seq']} — {ultimo['tipo']}")
    print(f"      Eventos restantes na pilha: {pilha.tamanho()}")

    return grafo, fila, pilha, despachos, previsao


if __name__ == "__main__":
    random.seed(42)
    main()