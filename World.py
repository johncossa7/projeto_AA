# world.py

import random


class WorldBase:
    def observacaoPara(self, agente):
        raise NotImplementedError

    def agir(self, accao, agente):
        raise NotImplementedError

    def atualizacao(self):
        raise NotImplementedError

    def terminado(self):
        return False


class WorldFarol(WorldBase):
    def __init__(self, size=10, num_obstaculos=15):
        self.size = size
        self.agent_pos = {"Explorer": (0, 0)}
        self.farol_pos = (size - 1, size - 1)

        # gerar obstáculos aleatórios
        self.obstaculos = set()
        while len(self.obstaculos) < num_obstaculos:
            x = random.randint(0, size - 1)
            y = random.randint(0, size - 1)

            if (x, y) not in [(0, 0), self.farol_pos]:
                self.obstaculos.add((x, y))

        self._terminado = False

    def observacaoPara(self, agente):
        ax, ay = self.agent_pos[agente.nome]
        fx, fy = self.farol_pos

        dx = fx - ax
        dy = fy - ay

        if dx == 0 and dy == 0:
            direcao = "AQUI"
        else:
            direcao = ""
            if dy < 0:
                direcao += "N"
            elif dy > 0:
                direcao += "S"
            if dx > 0:
                direcao += "E"
            elif dx < 0:
                direcao += "W"

        return {"pos": (ax, ay), "direcao": direcao}

    def agir(self, accao, agente):
        ax, ay = self.agent_pos[agente.nome]
        dx, dy = accao
        nx, ny = ax + dx, ay + dy

        # dentro dos limites?
        if not (0 <= nx < self.size and 0 <= ny < self.size):
            return

        # obstáculo?
        if (nx, ny) in self.obstaculos:
            return

        self.agent_pos[agente.nome] = (nx, ny)

    def atualizacao(self):
        if self.agent_pos["Explorer"] == self.farol_pos:
            self._terminado = True

    def terminado(self):
        return self._terminado

    def render(self):
        ax, ay = self.agent_pos["Explorer"]
        fx, fy = self.farol_pos

        print("\n----- MUNDO -----")
        for y in range(self.size):
            linha = ""
            for x in range(self.size):
                if (x, y) == (ax, ay):
                    linha += " A "
                elif (x, y) == (fx, fy):
                    linha += " F "
                elif (x, y) in self.obstaculos:
                    linha += " X "
                else:
                    linha += " . "
            print(linha)
        print("-----------------\n")
