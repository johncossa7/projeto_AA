class WorldBase:
    def observacaoPara(self, agente): raise NotImplementedError
    def agir(self, accao, agente): raise NotImplementedError
    def atualizacao(self): raise NotImplementedError
    def terminado(self): return False

class WorldFarol:
    def __init__(self, ficheiro):
        self._terminado = False
        self.obstaculos = set()
        self.agent_pos = []
        self.spawn_agent_pos = (0,0)

        # Valores padrão de segurança
        self.size = 10
        self.farol_pos = (9, 9)

        try:
            with open(ficheiro, "r") as f:
                for linha in f:
                    linha = linha.strip()
                    if not linha or linha.startswith("#"): continue
                    partes = linha.split()

                    if partes[0] == "SIZE":
                        self.size = int(partes[1])
                    elif partes[0] == "FAROL":
                        self.farol_pos = (int(partes[1]), int(partes[2]))
                    elif partes[0] == "OBSTACULO":
                        # AQUI ESTÁ A CORREÇÃO CRÍTICA (INT)
                        self.obstaculos.add((int(partes[1]), int(partes[2])))
                    elif partes[0] == "AGENTE":
                        x, y = int(partes[2]), int(partes[3])
                        self.spawn_agent_pos = (x, y)
                        self.agent_pos.append((x, y))
        except Exception as e:
            print(f"Erro ao ler ficheiro: {e}")

        # Se não houver agentes no ficheiro, usa o spawn
        if not self.agent_pos:
            self.agent_pos = [self.spawn_agent_pos]

        # Remove farol dos obstáculos se houver sobreposição
        if self.farol_pos in self.obstaculos:
            self.obstaculos.remove(self.farol_pos)

    def add_agent(self, pos):
        x, y = pos
        if not (0 <= x < self.size and 0 <= y < self.size): raise ValueError("Posição fora")
        if (x, y) in self.obstaculos: raise ValueError("Posição em obstáculo")
        if (x, y) == self.farol_pos: raise ValueError("Posição em farol")
        self.agent_pos.append((x, y))

    def observacaoPara(self, agente_idx):
        ax, ay = self.agent_pos[agente_idx]
        fx, fy = self.farol_pos
        dx = fx - ax; dy = fy - ay
        if dx == 0 and dy == 0: return "AQUI"
        d = ""
        if dy < 0: d += "N"
        elif dy > 0: d += "S"
        if dx > 0: d += "E"
        elif dx < 0: d += "W"
        return d

    def _livre(self, x, y):
        # Verifica limites
        if not (0 <= x < self.size and 0 <= y < self.size): return False
        # Verifica obstáculos
        if (x, y) in self.obstaculos: return False
        return True

    def agir(self, agente, acao):
        dx, dy = acao.dx, acao.dy
        ax, ay = self.agent_pos[agente]
        fx, fy = self.farol_pos

        dist_antiga = abs(fx - ax) + abs(fy - ay)
        nx, ny = ax + dx, ay + dy

        if not self._livre(nx, ny):
            return -1  # Penalização

        self.agent_pos[agente] = (nx, ny)
        dist_nova = abs(fx - nx) + abs(fy - ny)
        return dist_antiga - dist_nova

    def atualizacao(self):
        for pos in self.agent_pos:
            if pos == self.farol_pos:
                self._terminado = True
                break

    def terminado(self): return self._terminado

    def render(self):
        grid = [[" . " for _ in range(self.size)] for _ in range(self.size)]
        for (x, y) in self.obstaculos: grid[y][x] = " X "
        fx, fy = self.farol_pos
        grid[fy][fx] = " F "
        for (x, y) in self.agent_pos:
            if (x,y) == self.farol_pos: grid[y][x] = " @ "
            else: grid[y][x] = " A "

        print(f"\n----- MUNDO FAROL -----")
        for y in range(self.size): print("".join(grid[y]))
        print("-----------------------\n")