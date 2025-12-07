import time
from World import WorldFarol
from Sensor import SensorObservacao, SensorLivre
from Agent import AgenteFarol

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

        if primeira == "WORLD_FAROL":
            return Simulator._cria_farol(ficheiro)

        raise ValueError(f"Tipo de mundo desconhecido: {primeira}")

    @staticmethod
    def _cria_farol(ficheiro):
        world = WorldFarol(ficheiro)
        agents = []

        for i, (ax, ay) in enumerate(world.agent_pos):
            ag = AgenteFarol(f"Agente{i}")

            # instalar sensores
            ag.instala(SensorObservacao(world, i))
            ag.instala(SensorLivre(world, i))

            agents.append(ag)

        return Simulator(world, agents)


    def listaAgentes(self):
        return self.agents

    def executa(self, max_passos=50, render=True, delay=0.2):
        self._terminado = False
        self.passos = 0

        while self.passos < max_passos and not self.world.terminado():
            self.passos += 1
            if render: self.world.render(); time.sleep(delay)

            for i, ag in enumerate(self.agents):
                obs = self.world.observacaoPara(i)
                ag.observacao(obs)
                acao = ag.age()
                self.world.agir(i, acao)

            self.world.atualizacao()
            if self.world.terminado():
                self._terminado = True
                break

        if render: self.world.render()
        return {"terminado": self.world.terminado(), "passos": self.passos}