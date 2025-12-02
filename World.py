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
    import random

import random

class WorldFarol:
    def __init__(self, size=10, num_obstaculos=0, farol_pos=None):
        self.size = size
        self._terminado = False

        # definir farol
        if farol_pos is None:
            self.farol_pos = (size - 1, size - 1)
        else:
            self.farol_pos = farol_pos

        # obstáculos aleatórios
        possiveis = [(x, y) for x in range(size) for y in range(size)
                     if (x, y) != self.farol_pos]
        self.obstaculos = set(random.sample(possiveis, min(num_obstaculos, len(possiveis))))

        # lista de posições de agentes
        self.agent_pos = []

    def add_agent(self, pos):
        x, y = pos
        if not (0 <= x < self.size and 0 <= y < self.size):
            raise ValueError("Posição fora da grelha")
        if (x, y) in self.obstaculos:
            raise ValueError("Posição em obstáculo")
        if (x, y) == self.farol_pos:
            raise ValueError("Posição em cima do farol")
        self.agent_pos.append((x, y))

    def observacaoPara(self, agente_idx):
        ax, ay = self.agent_pos[agente_idx]
        fx, fy = self.farol_pos

        dx = fx - ax
        dy = fy - ay

        if dx == 0 and dy == 0:
            return "AQUI"

        direcao = ""
        if dy < 0: direcao += "N"
        elif dy > 0: direcao += "S"
        if dx > 0: direcao += "E"
        elif dx < 0: direcao += "W"

        return direcao

    def _livre(self, x, y):
        if not (0 <= x < self.size and 0 <= y < self.size): return False
        if (x, y) in self.obstaculos: return False
        return True

    def agir(self, agente, acao):
        dx, dy = acao.dx, acao.dy  # agora acao é sempre do tipo Acao
        ax, ay = self.agent_pos[agente]
        nx, ny = ax + dx, ay + dy
        if self._livre(nx, ny):
            self.agent_pos[agente] = (nx, ny)



    def atualizacao(self):
        for pos in self.agent_pos:
            if pos == self.farol_pos:
                self._terminado = True
                break

    def terminado(self):
        return self._terminado

    def render(self):
        grid = [[" . " for _ in range(self.size)] for _ in range(self.size)]
        fx, fy = self.farol_pos
        grid[fy][fx] = " F "
        for (x, y) in self.obstaculos:
            grid[y][x] = " X "
        for (x, y) in self.agent_pos:
            grid[y][x] = " A "
        print("\n----- MUNDO FAROL -----")
        for y in range(self.size):
            print("".join(grid[y]))
        print("-----------------------\n")
