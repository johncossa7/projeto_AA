# simulator.py

import time
from World import WorldFarol
from Agent import AgenteFarolFixo


class Simulator:
    def __init__(self, world, agents):
        self.world = world
        self.agents = agents
        self.terminado = False
        self.passos = 0

    @staticmethod
    def cria(_):
        world = WorldFarol(size=10, num_obstaculos=35)
        agent = AgenteFarolFixo("Explorer", world)
        return Simulator(world, [agent])

    def listaAgentes(self):
        return self.agents

    def executa(self, max_passos=20):
        self.terminado = False
        self.passos = 0

        while not self.terminado and self.passos < max_passos:
            self.passos += 1

            self.world.render()
            time.sleep(0.4)

            for agente in self.agents:
                obs = self.world.observacaoPara(agente)
                acao = agente.decidir(obs)
                self.world.agir(acao, agente)

            self.world.atualizacao()
            if self.world.terminado():
                self.terminado = True

        self.world.render()
        return {"terminado": self.terminado, "passos": self.passos}
