from typing import List
from models import Pedido, Mapa, Veiculo
import random
import networkx as nx

VELOCIDADE_KMH = 30.0  # velocidade média para estimar tempo de viagem


class GestorPedidos:
    def __init__(self):
        self.pedidos: List[Pedido] = []
        self._proximo_id = 1

    def criar_pedido(self, origem, destino, numPassageiros, horario,
                     prioridade, prefAmbiental,tempo_espera=None) -> Pedido:
        pedido = Pedido(
            id=self._proximo_id,
            origem=origem,
            destino=destino,
            numPassageiros=numPassageiros,
            horario=horario,
            prioridade=prioridade,
            prefAmbiental=prefAmbiental,
            tempo_espera=tempo_espera,
        )
        self._proximo_id += 1
        self.pedidos.append(pedido)
        return pedido

    def pedidos_pendentes(self) -> List[Pedido]:
        return [p for p in self.pedidos if p.estado == "pendente"]

    def escolher_proximo_pedido(self) -> Pedido | None:
        pendentes = self.pedidos_pendentes()
        if not pendentes:
            return None

        # maior prioridade primeiro; em empate, menor horário
        pendentes.sort(key=lambda p: (-p.prioridade, p.horario))
        return pendentes[0]

    def gerar_pedido_aleatorio(self, mapa: Mapa, horario_atual: float) -> Pedido:
        nos = list(mapa.graph.nodes())

        origem = random.choice(nos)
        destino = random.choice(nos)
        while destino == origem:
            destino = random.choice(nos)

        num_pass = random.randint(1, 4)
        prioridade = random.choices([1, 2, 3], weights=[0.5, 0.3, 0.2])[0]
        prefAmbiental = random.choice(["eletrico", "indiferente"])

        #  50% dos pedidos têm limite de espera 15–30 min
        if random.random() < 0.5:
            tempo_espera = random.choice([10, 15, 20, 30])  # minutos
        else:
            tempo_espera = None

        return self.criar_pedido(
            origem=origem,
            destino=destino,
            numPassageiros=num_pass,
            horario=horario_atual,
            prioridade=prioridade,
            prefAmbiental=prefAmbiental,
            tempo_espera=tempo_espera,
        )



# --------- Funções de apoio à alocação de veículos ---------


def calcular_distancia_km(mapa: Mapa, origem, destino) -> float | None:
    """Devolve a distância em km entre origem e destino no grafo, ou None se não houver caminho."""
    try:
        dist_m = nx.shortest_path_length(
            mapa.graph,
            source=origem,
            target=destino,
            weight="length",
        )
    except (nx.NetworkXNoPath, KeyError):
        return None
    return dist_m / 1000.0


def _fator_custo_por_tipo(tipo: str) -> float:
    """Fator de custo por tipo de motorização."""
    if tipo == "eletrico":
        return 1.0
    if tipo == "diesel":
        return 1.4
    if tipo == "gasolina":
        return 1.6
    return 1.5  # default para outros tipos


def veiculos_candidatos_para_pedido(
    pedido: Pedido,
    veiculos: List[Veiculo],
    mapa: Mapa,
    tempo_atual: float,
) -> List[Veiculo]:

    dist_km = calcular_distancia_km(mapa, pedido.origem, pedido.destino)
    if dist_km is None:
        # sem caminho → ninguém é candidato
        return []

    candidatos: List[Veiculo] = []

    for v in veiculos:
        # se o veículo não tiver atributo , assume livre desde 0
        ocupado_ate = getattr(v, "ocupado_ate", 0.0)
        if ocupado_ate > tempo_atual:
            # ainda a meio de uma viagem
            continue

        # capacidade
        if v.capacidade < pedido.numPassageiros:
            continue

        # preferência ambiental
        if pedido.prefAmbiental == "eletrico" and v.tipo != "eletrico":
            continue

        # autonomia
        if v.autonomia < dist_km:
            continue

        candidatos.append(v)

    return candidatos


def atribuir_pedido_a_melhor_veiculo(
    pedido: Pedido,
    veiculos: List[Veiculo],
    mapa: Mapa,
    tempo_atual: float,
) -> Veiculo | None:

    # 1) distância origem-destino
    dist_km = calcular_distancia_km(mapa, pedido.origem, pedido.destino)
    if dist_km is None:
        # logisticamente impossível (sem caminho)
        pedido.estado = "rejeitado"
        pedido.veiculo_id = None
        pedido.tempo_resposta = None
        return None

    # 2) verificar se existe ALGUM veículo teoricamente capaz (ignorando ocupado_ate)
    teoricamente_possiveis: List[Veiculo] = []
    for v in veiculos:
        if v.capacidade < pedido.numPassageiros:
            continue
        if pedido.prefAmbiental == "eletrico" and v.tipo != "eletrico":
            continue
        if v.autonomia < dist_km:
            continue
        teoricamente_possiveis.append(v)

    if not teoricamente_possiveis:

        pedido.estado = "rejeitado"
        pedido.veiculo_id = None
        pedido.tempo_resposta = None
        return None

    # 3) veículos candidatos livres AGORA 
    candidatos = veiculos_candidatos_para_pedido(pedido, veiculos, mapa, tempo_atual)

    if not candidatos:
        # não há nenhum carro livre neste instante
        # se o cliente não definiu tempo_espera → nunca rejeitamos por tempo
        if pedido.tempo_espera is None:
            # mantém estado "pendente"
            return None

        # se há tempo_espera, vê se já passou o limite
        limite = pedido.horario + pedido.tempo_espera
        if tempo_atual >= limite:
            # já passou o máximo que o cliente aceita esperar
            pedido.estado = "rejeitado"
            pedido.veiculo_id = None
            pedido.tempo_resposta = None
            return None
        else:
            # ainda há margem para esperar → continua pendente
            return None

    # 4) há candidatos livres agora → escolhe o mais barato (fator_tipo * dist_km)

    def custo_total(v: Veiculo) -> float:
        return _fator_custo_por_tipo(v.tipo) * dist_km

    veiculo_escolhido = min(candidatos, key=custo_total)

    # estimar tempo de viagem em minutos
    tempo_viagem_min = dist_km / VELOCIDADE_KMH * 60.0

    # atualizar veículo
    ocupado_ate_atual = getattr(veiculo_escolhido, "ocupado_ate", 0.0)
    inicio_viagem = max(tempo_atual, ocupado_ate_atual)
    veiculo_escolhido.ocupado_ate = inicio_viagem + tempo_viagem_min

    # atualizar pedido
    pedido.estado = "atribuido"
    pedido.veiculo_id = veiculo_escolhido.id
    pedido.tempo_resposta = tempo_atual - pedido.horario

    return veiculo_escolhido
