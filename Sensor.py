class SensorBase:
    def __init__(self, world, nome_agente):
        self.world = world
        self.nome = nome_agente
    def observacao(self): raise NotImplementedError

class SensorLivre(SensorBase):
    def __init__(self, world, nome_agente, raio=1):
        super().__init__(world, nome_agente)

    def _livre(self, nx, ny):
        if not (0 <= nx < self.world.size and 0 <= ny < self.world.size): return False
        if (nx, ny) in self.world.obstaculos: return False
        return True

    def observacao(self):
        candidatos = [(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]
        livres = []
        x, y = self.world.agent_pos[self.nome]
        for dx, dy in candidatos:
            nx, ny = x + dx, y + dy
            if self._livre(nx, ny): livres.append((dx, dy))
        return livres

class SensorVisual(SensorBase):
    def observacao(self):
        # [Cima(0,-1), Baixo(0,1), Esq(-1,0), Dir(1,0)]
        vizinhos = []
        deltas = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        x, y = self.world.agent_pos[self.nome]

        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            tipo = 0

            # Limites e Obstáculos (Comum a todos os mundos)
            if not (0 <= nx < self.world.size and 0 <= ny < self.world.size): tipo = 1
            elif (nx, ny) in self.world.obstaculos: tipo = 1

            # Objetos Específicos do Foraging (Try/Except ou hasattr para robustez)
            elif hasattr(self.world, 'ninho_pos') and (nx, ny) == self.world.ninho_pos:
                tipo = 3
            elif hasattr(self.world, 'alimentos') and (nx, ny) in self.world.alimentos:
                tipo = 2

            vizinhos.append(tipo)
        return tuple(vizinhos)

class SensorCarga(SensorBase):
    def observacao(self):
        if hasattr(self.world, 'agent_carrying'):
            return self.world.agent_carrying[self.nome]
        return False

class SensorGPS(SensorBase):
    def observacao(self):
        # Retorna a posição exata (tuplo)
        return self.world.agent_pos[self.nome]