# agente.py

class AgenteBase:
    def __init__(self, nome, world):
        self.nome = nome
        self.world = world

    def decidir(self, observacao):
        raise NotImplementedError


class AgenteFarolFixo(AgenteBase):
    def decidir(self, observacao):
        direcao = observacao["direcao"]

        movimentos = {
            "N":  (0, -1),
            "S":  (0, 1),
            "E":  (1, 0),
            "W":  (-1, 0),
            "NE": (1, -1),
            "NW": (-1, -1),
            "SE": (1, 1),
            "SW": (-1, 1),
            "AQUI": (0, 0)
        }

        principal = movimentos[direcao]

        ax, ay = self.world.agent_pos[self.nome]

        # 1) tentar movimento principal
        dx, dy = principal
        nx, ny = ax + dx, ay + dy
        if self._livre(nx, ny):
            return principal

        # 2) tentar movimentos alternativos simples
        alternativas = [
            (1, 0), (-1, 0), (0, 1), (0, -1)
        ]

        for dx, dy in alternativas:
            nx, ny = ax + dx, ay + dy
            if self._livre(nx, ny):
                return (dx, dy)

        # 3) se tudo falhar, fica parado
        return (0, 0)

    def _livre(self, x, y):
        # dentro do mundo?
        if not (0 <= x < self.world.size and 0 <= y < self.world.size):
            return False
        # sem obstáculo?
        if (x, y) in self.world.obstaculos:
            return False
        return True
