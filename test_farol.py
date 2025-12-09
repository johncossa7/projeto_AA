from Simulator import Simulator
from utils import evoluir
from Sensor import SensorObservacao, SensorLivre

FICHEIRO = "world_farol.txt"

print("--- TREINO ---")
melhor = evoluir(FICHEIRO, populacao=30, geracoes=100, max_passos=20)

print("\n--- DEMONSTRAÇÃO ---")
sim = Simulator.cria(FICHEIRO)
melhor.sensores = []
melhor.instala(SensorObservacao(sim.world, 0))
melhor.instala(SensorLivre(sim.world, 0))
sim.agents[0] = melhor
sim.executa(max_passos=50, render=True, delay=0.6)