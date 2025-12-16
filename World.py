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

class WorldForaging:
    def __init__(self, ficheiro):
        self._terminado = False
        self.obstaculos = set()
        self.alimentos = set()
        self.agent_pos = []
        self.agent_carrying = {}
        self.ninho_pos = (5, 5)
        self.size = 10
        self.score = 0

        try:
            with open(ficheiro, "r") as f:
                for linha in f:
                    linha = linha.strip()
                    if not linha or linha.startswith("#"): continue

                    partes = linha.split()
                    comando = partes[0].upper()

                    if comando == "SIZE":
                        self.size = int(partes[1])
                    elif comando == "NINHO":
                        self.ninho_pos = (int(partes[1]), int(partes[2]))
                    elif comando == "ALIMENTO":
                        self.alimentos.add((int(partes[1]), int(partes[2])))
                    elif comando == "OBSTACULO":
                        self.obstaculos.add((int(partes[1]), int(partes[2])))
                    elif comando == "AGENTE":
                        if len(partes) == 4:
                            x, y = int(partes[2]), int(partes[3])
                        else:
                            x, y = int(partes[1]), int(partes[2])

                        idx = len(self.agent_pos)
                        self.agent_pos.append((x, y))
                        self.agent_carrying[idx] = False

        except Exception as e:
            print(f"ERRO CRÍTICO ao ler {ficheiro}: {e}")
            raise e

    def observacaoPara(self, agente_idx):
        return "UNK"

    def _livre(self, x, y):
        if not (0 <= x < self.size and 0 <= y < self.size): return False
        if (x, y) in self.obstaculos: return False
        return True

    def agir(self, agente_idx, acao):
        # Posição antes do movimento
        antigo_x, antigo_y = self.agent_pos[agente_idx]
        ax, ay = antigo_x, antigo_y

        dx, dy = acao.dx, acao.dy
        nx, ny = antigo_x + dx, antigo_y + dy

        recompensa = -0.1 # CORREÇÃO: Custo de movimento normalizado

        # 2. Movimento
        if self._livre(nx, ny):
            self.agent_pos[agente_idx] = (nx, ny)
            ax, ay = nx, ny # Nova posição atual
        else:
            recompensa -= 2.0 # CORREÇÃO: Bater dói (Penalização)
            # ax, ay permanece como antigo_x, antigo_y

        # 3. Lógica de Foraging (Apanhar/Entregar)
        estou_no_ninho = ((ax, ay) == self.ninho_pos)
        estou_na_comida = ((ax, ay) in self.alimentos)
        carregando = self.agent_carrying[agente_idx]

        if estou_na_comida and not carregando:
            self.agent_carrying[agente_idx] = True
            self.alimentos.remove((ax, ay))
            recompensa += 5.0 # CORREÇÃO: Recompensa por apanhar (Normalizada)

        elif estou_no_ninho and carregando:
            self.agent_carrying[agente_idx] = False
            recompensa += 10.0 # CORREÇÃO: GRANDE Recompensa final (Normalizada)
            self.score += 1

        # 4. SHAPING REWARD (Completo: Guia nas duas fases do ciclo)

        target_pos = None
        shaping_factor = 0.0

        if carregando:
            # FASE 1: Ir para o Ninho
            target_pos = self.ninho_pos
            shaping_factor = 0.2
        elif self.alimentos:
            # FASE 2: Ir para a Comida Mais Próxima (Shaping Reverso)

            # Encontra a posição do alimento mais próximo
            min_dist = float('inf')
            temp_target = None
            for fx, fy in self.alimentos:
                dist = abs(ax - fx) + abs(ay - fy)
                if dist < min_dist:
                    min_dist = dist
                    temp_target = (fx, fy)

            target_pos = temp_target
            shaping_factor = 0.1 # Menor valor para ir buscar

        # Aplicar o SHAPING, se houver um alvo
        if target_pos:
            # Distância de Manhattan: |x1-x2| + |y1-y2|
            dist_antes = abs(antigo_x - target_pos[0]) + abs(antigo_y - target_pos[1])
            dist_agora = abs(ax - target_pos[0]) + abs(ay - target_pos[1])

            if dist_agora < dist_antes:
                recompensa += shaping_factor  # A aproximar-se
            elif dist_agora > dist_antes:
                recompensa -= shaping_factor / 2 # A afastar-se

        return recompensa

    def atualizacao(self):
        if len(self.alimentos) == 0 and not any(self.agent_carrying.values()):
            self._terminado = True

    def terminado(self):
        return self._terminado

    def render(self):
        grid = [[" . " for _ in range(self.size)] for _ in range(self.size)]

        nx, ny = self.ninho_pos
        grid[ny][nx] = "[N]"

        for (ox, oy) in self.obstaculos: grid[oy][ox] = "XXX"
        for (fx, fy) in self.alimentos: grid[fy][fx] = " * "

        for i, (ax, ay) in enumerate(self.agent_pos):
            symbol = " A " if not self.agent_carrying[i] else " A*"
            if (ax, ay) == self.ninho_pos: symbol = "[A]"
            grid[ay][ax] = symbol

        print(f"\n--- FORAGING (Score: {self.score}) ---Remaining Food: {len(self.alimentos)}")
        for y in range(self.size): print("".join(grid[y]))
        print("--------------------------------------\n")