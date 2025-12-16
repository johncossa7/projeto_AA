import time
# Imports dos Mundos
from World import WorldFarol, WorldForaging
# Imports dos Sensores
from Sensor import SensorVisual, SensorLivre, SensorCarga,SensorGPS
# Imports dos Agentes
from Agent import AgenteFarolQLearning, AgenteNovelty

class Simulator:
    def __init__(self, world, agents):
        self.world = world
        self.agents = agents
        self.passos = 0
        self._terminado = False

    @staticmethod
    def cria(ficheiro):
        with open(ficheiro, "r") as f:
            primeira = f.readline().strip()

        # Deteta qual o tipo de mundo pelo cabeçalho do ficheiro
        if primeira == "WORLD_FAROL":
            return Simulator._cria_farol(ficheiro)
        elif primeira == "WORLD_FORAGING":
            return Simulator._cria_foraging(ficheiro)

        raise ValueError(f"Tipo de mundo desconhecido: {primeira}")

    @staticmethod
    def _cria_farol(ficheiro):
        world = WorldFarol(ficheiro)
        agents = []
        for i, (ax, ay) in enumerate(world.agent_pos):
            # Agente Q-Learning Clássico
            ag = AgenteFarolQLearning(f"Agente{i}")
            ag.instala(SensorVisual(world, i))
            ag.instala(SensorLivre(world, i))
            agents.append(ag)
        return Simulator(world, agents)

    @staticmethod
    def _cria_foraging(ficheiro):
        world = WorldForaging(ficheiro)
        agents = []
        for i in range(len(world.agent_pos)):
            # Beta alto (5.0) para valorizar muito a exploração
            ag = AgenteNovelty(f"Explorador{i}", alpha=0.1, gamma=0.9, epsilon=0.2, beta=5.0)

            # Instalar Sensores
            ag.instala(SensorGPS(world, i))     # Onde estou?
            ag.instala(SensorLivre(world, i))   # Para onde posso ir?
            ag.instala(SensorCarga(world, i))   # Tenho comida?

            agents.append(ag)
        return Simulator(world, agents)

    def executa(self, max_passos=50, render=True, delay=0.2):
        while self.passos < max_passos and not self.world.terminado():
            self.passos += 1

            if render:
                self.world.render()
                time.sleep(delay)

            for i, ag in enumerate(self.agents):
                acao = ag.age()
                recompensa = self.world.agir(i, acao) # O indice 'i' é passado para o mundo saber quem agiu
                ag.avaliacaoEstadoAtual(recompensa)

            self.world.atualizacao()
            if self.world.terminado():
                self._terminado = True
                break

        if render:
            self.world.render()
            if self.world.terminado():
                print(f"\n🏆 FIM: Score Final = {getattr(self.world, 'score', 'N/A')} 🏆")
            else:
                print("\n❌ FIM: O tempo acabou.")

        return {"terminado": self.world.terminado(), "passos": self.passos}