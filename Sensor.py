class SensorBase:
    def __init__(self, world, nome_agente):
        self.world = world
        self.nome = nome_agente

    def observacao(self):
        # metodo abstrato a ser implementado por todos os sensores
        raise NotImplementedError


class SensorObservacao(SensorBase):
    def observacao(self):
        # devolve a direção como string: "N", "SE", "AQUI", etc.
        return self.world.observacaoPara(self.nome)


class SensorLivre(SensorBase):
    def __init__(self, world, nome_agente, raio=1):
        super().__init__(world, nome_agente)
        self.raio = raio

    def livre(self, dx, dy):
        # verifica se a nova posição está livre
        x, y = self.world.agent_pos[self.nome]
        nx, ny = x + dx, y + dy
        return self._livre(nx, ny)

    def _livre(self, nx, ny):
        # verifica se a posição nx,ny está dentro dos limites do mapa e se não é um objeto
        if not (0 <= nx < self.world.size and 0 <= ny < self.world.size):
            return False
        if (nx, ny) in self.world.obstaculos:
            return False
        return True

    def observacao(self):
        # apenas cruz + ficar parado (compatível com AgenteFarol.MOVS)
        candidatos = [(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]
        livres = []

        x, y = self.world.agent_pos[self.nome]
        for dx, dy in candidatos:
            nx, ny = x + dx, y + dy
            if self._livre(nx, ny):
                livres.append((dx, dy))

        return livres
