import matplotlib.pyplot as plt
import os
import numpy as np
from Simulator import Simulator
# Importamos o novo agente do nosso ficheiro Agent.py
from Agent import AgenteReativoSensores
from Sensor import SensorGPS, SensorCarga, SensorVisual, SensorLivre

# --- CONFIGURAÇÃO ---
FICHEIRO_MUNDO = "world_foraging.txt"
EPISODIOS = 2000
MAX_PASSOS = 400
POSICAO_INICIAL = (5,5)
ALIMENTOS_INICIAIS = {(1,1), (1,8), (8,1), (8,8), (2,2)}

# Garante que o mundo existe
if not os.path.exists(FICHEIRO_MUNDO):
    with open(FICHEIRO_MUNDO, "w") as f:
        f.write("10\n0,0\n5,5\n")

sim = Simulator.cria(FICHEIRO_MUNDO)

# --- SETUP DO AGENTE REATIVO ---
# Instanciamos o agente que acabámos de adicionar ao Agent.py
agente = AgenteReativoSensores("AgenteReativo")

# Instalamos os sensores necessários
agente.instala(SensorGPS(sim.world, 0))
agente.instala(SensorCarga(sim.world, 0))
agente.instala(SensorVisual(sim.world, 0))
agente.instala(SensorLivre(sim.world, 0))

sim.agents[0] = agente
scores = []

print(f"--- A testar Baseline Reativa ({EPISODIOS} eps) ---")

# --- LOOP DE SIMULAÇÃO ---
for ep in range(EPISODIOS):
    # Reset do Mundo
    sim.world.alimentos = ALIMENTOS_INICIAIS.copy()
    sim.world.agent_pos[0] = POSICAO_INICIAL
    sim.world.agent_carrying[0] = False
    sim.world.score = 0
    sim.world._terminado = False
    sim.passos = 0

    while sim.passos < MAX_PASSOS and not sim.world.terminado():
        sim.passos += 1
        acao = agente.age()
        sim.world.agir(0, acao)
        sim.world.atualizacao()

    scores.append(sim.world.score)

# --- GERAR GRÁFICO (ESTILO PROFISSIONAL) ---

# 1. Largura Panorâmica (Igual ao do Agente Inteligente)
plt.figure(figsize=(12, 5))

# 2. Linha de Máximo (Referência)
plt.axhline(y=5, color='green', linestyle=':', label='Máximo Possível (5.0)', alpha=0.5)

# 3. Dados Brutos (Cinzento Claro)
plt.plot(scores, color='lightgray', alpha=0.5, label='Raw Score')

# 4. Média Móvel (Linha Preta para Baseline)
window = 50
media_movel = [sum(scores[max(0, i-window):i+1])/(i-max(0, i-window)+1) for i in range(len(scores))]
plt.plot(media_movel, color='black', linewidth=2, label='Média (Reativo)')

# 5. Configurações de Eixos e Títulos
plt.title("Baseline: Agente Reativo (Sensores Locais)")
plt.xlabel("Episódios")
plt.ylabel("Score (Comida Entregue)")

# IMPORTANTE: Forçar a escala Y para ser igual à do gráfico de aprendizagem
plt.ylim(-0.2, 5.2)

plt.legend(loc='lower right')

plt.show()