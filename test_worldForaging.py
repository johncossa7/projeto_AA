# ... (Incluir as classes WorldForaging, Sensores e AgenteNovelty acima) ...
# ... (Incluir Simulator original e modificar método cria) ...
from Agent import AgenteNovelty
from Sensor import SensorLivre
from Simulator import Simulator
from World import WorldForaging


# Modificação na Factory do Simulator para suportar Foraging
def cria_simulator(ficheiro):
    with open(ficheiro, "r") as f:
        primeira = f.readline().strip()

    if primeira == "WORLD_FAROL":
        # ... (código antigo) ...
        pass
    elif primeira == "WORLD_FORAGING":
        world = WorldForaging(ficheiro)
        agents = []
        for i in range(len(world.agent_pos)):
            # Agente Novelty
            ag = AgenteNovelty(f"Explorador{i}", alpha=0.1, epsilon=0.3, beta=0.5)

            # Instalar Sensores Específicos
            ag.instala(SensorLivre(world, i))    # Para não bater

            agents.append(ag)
        return Simulator(world, agents)
    return None

# --- MAIN ---
sim = cria_simulator("world_foraging.txt")

if not sim.agents:
    print("ERRO: Nenhum agente foi criado. Verifica o ficheiro de texto.")
    exit()

# Treino
print("--- A TREINAR (NOVELTY SEARCH) ---")
historico_scores = []
for ep in range(500):
    # Reset
    sim.world.alimentos = {(1,1), (1,8), (8,1), (8,8), (2,2)} # Respawn manual para teste
    sim.world.agent_pos[0] = (5,5)
    sim.world.agent_carrying[0] = False
    sim.world._terminado = False
    sim.world.score = 0
    sim.passos = 0

    sim.agents[0].fim_episodio() # Decay epsilon

    while sim.passos < 100 and not sim.world.terminado():
        sim.passos += 1
        # Loop normal de agem/avaliação
        for i, ag in enumerate(sim.agents):
            acao = ag.age()
            r = sim.world.agir(i, acao)
            ag.avaliacaoEstadoAtual(r)
        sim.world.atualizacao()

    historico_scores.append(sim.world.score)
    if ep % 50 == 0:
        print(f"Ep {ep}: Score={sim.world.score} | VisitasDistintas={len(sim.agents[0].visitas)}")

# Teste Visual
print("\n--- TESTE FINAL ---")
sim.world.alimentos = {(1,1), (1,8), (8,1), (8,8), (2,2)}
sim.world.agent_pos[0] = (5,5)
sim.world.agent_carrying[0] = False
sim.world._terminado = False
sim.world.score = 0
sim.passos = 0
sim.agents[0].modo = "TEST"

sim.executa(max_passos=100, delay=0.1)