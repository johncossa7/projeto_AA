# agente.py

import random

class AgenteBase:
    def __init__(self, nome):
        self.nome = nome

    def decidir(self, observacao):
        raise NotImplementedError


class AgenteFarolBurro(AgenteBase):
    def __init__(self, nome, world):
        super().__init__(nome)
        self.world = world

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

        mov_principal = movimentos[direcao]

        alternativas = {
            "NE": [(0, -1), (1, 0)],
            "NW": [(0, -1), (-1, 0)],
            "SE": [(0, 1), (1, 0)],
            "SW": [(0, 1), (-1, 0)],
            "N":  [(0, -1)],
            "S":  [(0, 1)],
            "E":  [(1, 0)],
            "W":  [(-1, 0)],
            "AQUI": [(0, 0)]
        }

        ax, ay = self.world.agent_pos[self.nome]

        # 1) Tentar movimento principal
        dx, dy = mov_principal
        nx, ny = ax + dx, ay + dy
        if (nx, ny) not in self.world.obstaculos:
            return mov_principal

        # 2) Tentar alternativas diretas
        for alt in alternativas[direcao]:
            dx, dy = alt
            nx, ny = ax + dx, ay + dy
            if (nx, ny) not in self.world.obstaculos:
                return alt

        # 3) Movimento de desvio: qualquer célula vizinha livre
        vizinhos = [
            (1, 0), (-1, 0),  # E, W
            (0, 1), (0, -1),  # S, N
            (1, 1), (1, -1), (-1, 1), (-1, -1)  # diagonais
        ]

        livres = []
        for dx, dy in vizinhos:
            nx, ny = ax + dx, ay + dy
            if 0 <= nx < self.world.size and 0 <= ny < self.world.size:
                if (nx, ny) not in self.world.obstaculos:
                    livres.append((dx, dy))

        if livres:
            return random.choice(livres)

        # 4) Se estiver COMPLETAMENTE cercado (raro), fica parado
        return (0, 0)
