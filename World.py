class WorldBase:
    def observacaoPara(self, agente):
        raise NotImplementedError

    def agir(self, accao, agente):
        raise NotImplementedError

    def atualizacao(self):
        raise NotImplementedError

    def terminado(self):
        return False

class WorldFarol:
    def __init__(self, ficheiro):
        self._terminado = False
        self.obstaculos = set()
        self.agent_pos = []
        self.spawn_agent_pos = (0,0)

        with open(ficheiro, "r") as f:
            for linha in f:
                linha = linha.strip()

                if not linha or linha.startswith("#"):
                    continue

                partes = linha.split()

                if partes[0] == "SIZE":
                    self.size = int(partes[1])

                elif partes[0] == "FAROL":
                    x = int(partes[1])
                    y = int(partes[2])
                    self.farol_pos = (x, y)

                elif partes[0] == "OBSTACULO":
                    x = int(partes[1])
                    y = int(partes[2])
                    self.obstaculos.add((x,y))

                elif partes[0] == "AGENTE":
                    # o Simulator vai criar os agentes, o world só regista posições possíveis
                    nome = partes[1]
                    ax = int(partes[2])
                    ay = int(partes[3])
                    self.agent_pos.append((ax, ay))

        if not hasattr(self, "size"):
            raise ValueError("Falta SIZE no ficheiro.")

        if not hasattr(self, "farol_pos"):
            raise ValueError("Falta FAROL no ficheiro.")

        if self.farol_pos in self.obstaculos:
            self.obstaculos.remove(self.farol_pos)

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

