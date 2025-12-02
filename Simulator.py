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

        # inicializa posições dos agentes se não tiverem sido adicionados
        for i, ag in enumerate(self.agents):
            if i >= len(self.world.agent_pos):
                self.world.add_agent((0, i))

    @staticmethod
    def cria(nome_do_ficheiro_parametros=None):
        # parâmetros por defeito
        params = {
            "size": 10,
            "num_obstaculos": 30,
            "farol_pos": None,
            "agents": [{"nome": "Explorer", "tipo": "fixo"}]
        }

        # criar mundo
        world = WorldFarol(
            size=params["size"],
            num_obstaculos=params["num_obstaculos"],
            farol_pos=params["farol_pos"]
        )

        # criar agentes e adicionar posições
        agents = []
        for i, a in enumerate(params["agents"]):
            ag = a.get("objeto")  # aqui deves passar a classe já instanciada
            if not ag:
                from Agent import AgenteFarol
                ag = AgenteFarol.cria()
            agents.append(ag)

            # adiciona posição no mundo
            pos = tuple(a.get("pos", (0, i)))
            world.add_agent(pos)

            # instala sensores para o agente
            sensor_obs = SensorObservacao(world, i)  # ou o índice do agente
            sensor_livre = SensorLivre(world, i)
            ag.instala(sensor_obs)  # ou sensor_livre se quiseres usar movimento
            ag.instala(sensor_livre)

        return Simulator(world, agents)

    def listaAgentes(self):
        return self.agents

    def executa(self, max_passos=50, render=True, delay=0.2):
        self._terminado = False
        self.passos = 0

        dist_prev = [abs(self.world.farol_pos[0]-x)+abs(self.world.farol_pos[1]-y)
                     for x, y in self.world.agent_pos]

        while self.passos < max_passos and not self.world.terminado():
            self.passos += 1
            if render: self.world.render(); time.sleep(delay)

            for i, ag in enumerate(self.agents):
                pos_antiga = self.world.agent_pos[i]
                obs = self.world.observacaoPara(i)
                ag.observacao(obs)
                acao = ag.age()
                self.world.agir(i, acao)
                pos_nova = self.world.agent_pos[i]

                # recompensa avançada
                recompensa = self.calcula_recompensa(pos_antiga, pos_nova)
                ag.avaliacaoEstadoAtual(recompensa)

            self.world.atualizacao()
            if self.world.terminado():
                self._terminado = True
                break

        if render: self.world.render()
        return {"terminado": self.world.terminado(), "passos": self.passos}

    @staticmethod
    def calcula_recompensa(pos_antiga, pos_nova, farol_pos=(9,9)):
        x0, y0 = pos_antiga
        x1, y1 = pos_nova
        fx, fy = farol_pos

        if (x1, y1) == (fx, fy):
            return 2.0

        dist_antiga = abs(fx - x0)+abs(fy - y0)
        dist_nova = abs(fx - x1)+abs(fy - y1)
        delta = dist_antiga - dist_nova

        if delta > 0: return 1.0
        elif delta < 0: return -0.5
        else: return 0.0
