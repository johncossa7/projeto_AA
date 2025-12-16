import matplotlib.pyplot as plt
import numpy as np
import os
from Simulator import Simulator

# --- CONFIGURAÇÃO ---
FICHEIRO_MUNDO = "world_foraging.txt"
EPISODIOS = 2000
MAX_PASSOS = 400
POSICAO_INICIAL = (5,5)
ALIMENTOS_INICIAIS = {(1,1), (1,8), (8,1), (8,8), (2,2)}
NOME_FICHEIRO_CAMPEAO = "agente_estavel.json"
TAMANHO_MAPA = 10  # Assumindo mapa 10x10

if os.path.exists(NOME_FICHEIRO_CAMPEAO):
    os.remove(NOME_FICHEIRO_CAMPEAO)

sim = Simulator.cria(FICHEIRO_MUNDO)
if not sim.agents: exit()
agente = sim.agents[0]

# --- MATRIZ PARA O HEATMAP ---
# Cria uma grelha 10x10 a zeros
mapa_visitas = np.zeros((TAMANHO_MAPA, TAMANHO_MAPA))

# --- HIPERPARÂMETROS ---
agente.alpha = 0.2
ALPHA_MIN = 0.01
ALPHA_DECAY = 0.9995

agente.beta = 2.0
BETA_MIN = 0.1
BETA_DECAY = 0.999

agente.epsilon = 1.0
EPSILON_MIN = 0.01
EPSILON_DECAY = 0.999

print(f"--- A TREINAR E MAPEAR ({EPISODIOS} Episódios) ---")

scores = []
melhor_passos_global = float('inf')
campeao_existe = False

for ep in range(EPISODIOS):
    # --- RESET ---
    sim.world.alimentos = ALIMENTOS_INICIAIS.copy()
    sim.world.agent_pos[0] = POSICAO_INICIAL
    sim.world.agent_carrying[0] = False
    sim.world.score = 0
    sim.world._terminado = False
    sim.passos = 0

    agente.reset_curiosity()

    # --- DECAIMENTOS ---
    if agente.epsilon > EPSILON_MIN: agente.epsilon *= EPSILON_DECAY
    if agente.alpha > ALPHA_MIN: agente.alpha *= ALPHA_DECAY
    if agente.beta > BETA_MIN: agente.beta *= BETA_DECAY

    # --- TREINO ---
    while sim.passos < MAX_PASSOS and not sim.world.terminado():
        # 1. REGISTAR POSIÇÃO PARA O HEATMAP
        x, y = sim.world.agent_pos[0]
        mapa_visitas[y, x] += 1  # [Linha, Coluna] = [y, x]

        # 2. MOVIMENTO NORMAL
        sim.passos += 1
        acao = agente.age()
        recompensa = sim.world.agir(0, acao)
        agente.avaliacaoEstadoAtual(recompensa)
        sim.world.atualizacao()

    scores.append(sim.world.score)

    # --- SAVE CHAMPION ---
    if sim.world.score >= 5.0:
        if sim.passos < melhor_passos_global:
            melhor_passos_global = sim.passos
            campeao_existe = True
            agente.save_q(NOME_FICHEIRO_CAMPEAO)

    if (ep + 1) % 500 == 0:
        print(f"Ep {ep+1} | Progresso... (Alpha={agente.alpha:.3f})")

# --- GERAR HEATMAP ---
print("\nGerando Heatmap...")

plt.figure(figsize=(10, 8))

# Criar o mapa de calor
# 'inferno' ou 'hot' são boas cores para intensidade
plt.imshow(mapa_visitas, cmap='inferno', interpolation='nearest', origin='upper')

# Barra lateral
cbar = plt.colorbar()
cbar.set_label('Frequência de Visitas (Acumulado)', rotation=270, labelpad=15)

# --- ANOTAÇÕES NO MAPA ---
# Marcar Ninho
plt.text(5, 5, 'NINHO', ha='center', va='center', color='cyan', fontweight='bold', fontsize=9)

# Marcar Comidas Iniciais
for (cx, cy) in ALIMENTOS_INICIAIS:
    plt.text(cx, cy, '🍎', ha='center', va='center', fontsize=12)

# Configurações do Gráfico
plt.title(f"Heatmap de Exploração: Novelty Search\n({EPISODIOS} Episódios | Beta Inicial: 2.0)")
plt.xlabel("X")
plt.ylabel("Y")
plt.xticks(range(TAMANHO_MAPA))
plt.yticks(range(TAMANHO_MAPA))

# Guardar e Mostrar
plt.savefig("heatmap_novelty_final.png", dpi=150)
print("Gráfico guardado como 'heatmap_novelty_final.png'")
plt.show()

# --- TESTE DO CAMPEÃO (OPCIONAL) ---
if campeao_existe:
    print("\n--- TESTE DO CAMPEÃO ---")
    agente.load_q(NOME_FICHEIRO_CAMPEAO)
    agente.modo = "TEST"
    agente.epsilon = 0
    agente.beta = 0 # Sem curiosidade no teste final

    sim.world.alimentos = ALIMENTOS_INICIAIS.copy()
    sim.world.agent_pos[0] = POSICAO_INICIAL
    sim.world.agent_carrying[0] = False
    sim.world.score = 0
    sim.world._terminado = False
    sim.passos = 0

    sim.executa(max_passos=300, render=True, delay=0.2)