import matplotlib.pyplot as plt
import numpy as np
import os
from Simulator import Simulator
from Agent import AgenteNovelty # Certifica-te que importas a tua classe correta
from Sensor import SensorGPS, SensorCarga, SensorLivre

# --- CONFIGURAÇÃO ---
FICHEIRO_MUNDO = "world_foraging.txt"
EPISODIOS = 2000       # Quantidade de jogos para acumular dados
MAX_PASSOS = 400     # Passos por episódio
TAMANHO_MAPA = 10    # Assumindo mapa 10x10

# Garante que o mundo existe
if not os.path.exists(FICHEIRO_MUNDO):
    with open(FICHEIRO_MUNDO, "w") as f:
        f.write(f"{TAMANHO_MAPA}\n0,0\n5,5\n")

# --- INICIALIZAÇÃO ---
sim = Simulator.cria(FICHEIRO_MUNDO)
agente = AgenteNovelty("AgenteExplorer", alpha=0.1, gamma=0.9, epsilon=0.1)

# Instalar sensores
agente.instala(SensorGPS(sim.world, 0))
agente.instala(SensorCarga(sim.world, 0))
agente.instala(SensorLivre(sim.world, 0))

sim.agents[0] = agente

# Matriz para guardar as visitas (10x10)
# Usamos zeros inicialmente
mapa_visitas = np.zeros((TAMANHO_MAPA, TAMANHO_MAPA))

print(f"--- A gerar Heatmap ({EPISODIOS} episódios) ---")

# --- LOOP DE SIMULAÇÃO ---
for ep in range(EPISODIOS):
    # Reset do Mundo
    sim.world.alimentos = {(1,1), (1,8), (8,1), (8,8), (2,2)} # Podes ajustar
    sim.world.agent_pos[0] = (5,5)
    sim.world.agent_carrying[0] = False
    sim.world._terminado = False
    sim.passos = 0

    # Reset da memória de novidade (opcional, se quiseres ver a aprendizagem acumulada)
    # agente.reset_curiosity()

    while sim.passos < MAX_PASSOS and not sim.world.terminado():
        # 1. Regista a posição atual
        x, y = sim.world.agent_pos[0]

        # NOTA: Invertemos Y se o gráfico sair de cabeça para baixo,
        # mas normalmente matrizes leem-se [Linha, Coluna], ou seja [Y, X]
        mapa_visitas[y, x] += 1

        # 2. Agir
        sim.passos += 1
        acao = agente.age()
        sim.world.agir(0, acao)

        # Recompensa manual simples para o treino ocorrer em background
        # (Aqui não precisamos do gráfico de score, só do movimento)
        r = 0
        if sim.world.terminado(): r = 100
        agente.avaliacaoEstadoAtual(r)

        sim.world.atualizacao()

    if (ep+1) % 10 == 0:
        print(f"Episódio {ep+1}/{EPISODIOS} concluído...")

# --- GERAR GRÁFICO ---

plt.figure(figsize=(8, 8))

# Criar o Heatmap
# cmap='hot' (preto/vermelho/amarelo) ou 'viridis' (azul/verde/amarelo)
# 'interpolation="nearest"' garante que vemos os quadrados perfeitos
plt.imshow(mapa_visitas, cmap='inferno', interpolation='nearest', origin='upper')

# Adicionar Barra de Cor (Legenda de Frequência)
cbar = plt.colorbar()
cbar.set_label('Frequência de Visitas', rotation=270, labelpad=15)

# Marcar o Ninho e Comidas para referência visual
# Ninho em (5,5)
plt.text(5, 5, 'NINHO', ha='center', va='center', color='cyan', fontweight='bold', fontsize=10)

# Labels e Título
plt.title(f"Mapa de Calor: Onde o Agente Novelty Passou\n({EPISODIOS} Episódios Acumulados)")
plt.xlabel("Coordenada X")
plt.ylabel("Coordenada Y")

# Ajustar os ticks para mostrar 0 a 9
plt.xticks(range(TAMANHO_MAPA))
plt.yticks(range(TAMANHO_MAPA))

# Guardar
nome_arquivo = 'heatmap_novelty.png'
plt.savefig(nome_arquivo, dpi=150)
print(f"Gráfico guardado como '{nome_arquivo}'")
plt.show()