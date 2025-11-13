import json
import networkx as nx

class Veiculo:
    def __init__(self, id, tipo, marca, modelo, ano, autonomia, max_autonomia, custoKm, localizacao, capacidade, impAmbiental):
        self.id = id
        self.tipo = tipo                    #eletrico ou combustao
        self.marca = marca
        self.modelo = modelo
        self.ano = ano
        self.autonomia = autonomia          #autonomia atual
        self.max_autonomia = max_autonomia
        self.custoKm = custoKm
        self.localizacao = localizacao      #atual em coordenadas
        self.capacidade = capacidade        #capacidade de passageiros
        self.impAmbiental = impAmbiental    #impacto ambiental
        self.disponivel = True              #disponibilidade do veiculo
        
class Pedido:
    def __init__(self, id, origem, destino, numPassageiros, horario, prioridade, prefAmbiental):
        self.id = id
        self.origem = origem                #coordenadas de origem
        self.destino = destino              #coordenadas de destino
        self.numPassageiros = numPassageiros
        self.horario = horario              #horario pretendido para o pedido
        self.prioridade = prioridade
        self.prefAmbiental = prefAmbiental
        self.atribuido = False              #se o pedido ja foi atribuido a um veiculo
        
class Mapa:
    def __init__(self, filepath):
        self.graph = nx.Graph()
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        for e in data["edges"]:
            self.graph.add_edge(
                e["from"],
                e["to"],
                length=e["length"]
            )
    def get_neighbors(self, node):
        return list(self.graph.neighbors(node))
    
    def distance(self, a, b):
        return self.graph[a][b]["length"]
    
    def time(self, a, b):
        return self.graph[a][b]["time"]
    